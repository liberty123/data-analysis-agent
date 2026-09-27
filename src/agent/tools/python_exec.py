# -*- coding: utf-8 -*-
import ast
import datetime
import decimal
import json
import os
import subprocess
import sys
import tempfile

from langchain_core.tools import tool


ALLOWED_IMPORTS = {
    "pandas", "numpy", "json", "math", "statistics", "re",
    "datetime", "collections", "itertools", "functools", "decimal",
    "random", "string", "textwrap", "typing", "warnings",
}

# 明令禁止的模块（即使不在白名单里也要双保险拦截）
FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib", "glob",
    "pickle", "marshal", "ctypes", "multiprocessing", "threading",
    "signal", "sqlite3", "importlib", "requests", "urllib", "http",
}

# 危险属性 / 内建函数名
FORBIDDEN_ATTRS = {"__import__", "__builtins__", "__globals__", "__subclasses__", "eval", "exec", "compile", "open"}

TIMEOUT = 60          # 子进程超时（秒），给首次冷启动留余量
MAX_OUTPUT = 2000     # 返回结果截断长度


def _json_default(obj):
    """JSON 序列化兜底：Decimal→float（保持数值），datetime→ISO 字符串"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)


def extract_imports(code: str) -> set[str]:
    tree = ast.parse(code)
    packages = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                packages.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                packages.add(node.module.split(".")[0])
    return packages

def _safety_check(code: str):
    """
    AST 静态检查。通过返回 None，失败返回错误信息字符串。
    拦截：危险模块 import、危险内建/属性访问、open/eval/exec 调用
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"error: 代码语法错误：{e}"

    # 1. import 检查（白名单 + 黑名单）
    for pkg in extract_imports(code):
        if pkg in FORBIDDEN_MODULES:
            return f"error: 禁止导入模块 {pkg}"
        if pkg not in ALLOWED_IMPORTS:
            return f"error: 模块 {pkg} 不在允许的白名单中"

    # 2. 危险函数调用 / 属性访问检查
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_ATTRS:
            return f"error: 禁止使用 {node.id}"
        if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            return f"error: 禁止访问属性 {node.attr}"
        if isinstance(node, ast.Call):
            f = node.func
            name = None
            if isinstance(f, ast.Name):
                name = f.id
            elif isinstance(f, ast.Attribute):
                name = f.attr
            if name in FORBIDDEN_ATTRS:
                return f"error: 禁止调用 {name}"
    return None


def _ensure_dependencies(code: str):
    """白名单内但未安装的包，自动安装（超时 120s）"""
    packages = extract_imports(code)
    PACKAGE_NAME_MAP = {
        "sklearn": "scikit-learn",
        "cv2": "opencv-python",
        "PIL": "Pillow",
    }
    for pkg in packages:
        if pkg not in ALLOWED_IMPORTS:
            continue  # 安全检查会拦截，这里只处理白名单包
        try:
            __import__(pkg)
        except ImportError:
            pip_name = PACKAGE_NAME_MAP.get(pkg, pkg)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pip_name],
                capture_output=True,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )

def _build_prelude(data_sources: dict) -> str:
    """
    生成数据注入代码：
      inline 数据 -> json.loads + pd.DataFrame
      file   数据 -> pd.read_json(路径)
    每个变量在用户代码中可直接使用（pandas DataFrame）
    """
    lines = ["import pandas as pd", "import json"]
    for var, src in (data_sources or {}).items():
        if not isinstance(src, dict):
            lines.append(f"{var} = None  # 非法数据源")
            continue
        if src.get("type") == "inline":
            data_json = json.dumps(src.get("data", []), ensure_ascii=False, default=_json_default)
            lines.append(f"{var} = pd.DataFrame(json.loads({data_json!r}))")
        elif src.get("type") == "file":
            path = src.get("path", "")
            lines.append(f"{var} = pd.read_json({path!r})")
        else:
            lines.append(f"{var} = None  # 数据源解析失败: {src.get('message', '未知')}")
    return "\n".join(lines) + "\n"


@tool
def execute_python_code(code: str, data_sources: dict) -> str:
    """这是一个执行python语句的函数，将sql查询结果在这一步进行处理，并且返回语句执行结果
    参数：
        code: python 语句（纯计算，禁止文件/网络/进程操作；可使用 pandas）
        data_sources: 数据注入映射，由执行器自动填充，格式为
            {"变量名": {"type": "inline", "data": [...]}}
            或 {"变量名": {"type": "file", "path": "..."}}
            注意：LLM 生成 plan 时不要直接构造本字段，应使用 {"变量名": {"step_id": N}}
            由执行器（executor）解析注入。
    """
     # 1. AST 静态安全检查
    err = _safety_check(code)
    if err:
        return err

    # 2. 确保白名单依赖已安装
    try:
        _ensure_dependencies(code)
    except Exception as e:
        return f"error: 依赖安装失败：{e}"

    # 3. 组装完整代码（注入数据 + 用户代码）
    full_code = _build_prelude(data_sources) + code

    # 4. 隔离子进程执行（独立临时工作目录 + UTF-8 模式 + 超时）
    child_env = os.environ.copy()
    child_env["PYTHONUTF8"] = "1"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-c", full_code],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT,
                env=child_env,
                cwd=tmp,  # 隔离工作目录：即使被绕过也写不进项目目录
            )
    except subprocess.TimeoutExpired:
        return "error: 执行超时（30s）"
    except Exception as e:
        return f"error: 执行异常：{e}"

    if proc.returncode != 0:
        return f"error: 执行出错：{(proc.stderr or '')[:MAX_OUTPUT]}"
    return (proc.stdout or "(无输出)")[:MAX_OUTPUT]

