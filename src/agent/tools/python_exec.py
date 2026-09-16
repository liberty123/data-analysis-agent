# -*- coding: utf-8 -*-
from langchain_core.tools import tool
import tempfile
import os
import ast
import subprocess
import sys
import json

# 标准库白名单（不需要安装）
STDLIB = sys.stdlib_module_names


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


def ensure_dependencies(code: str):
    """检查并安装代码所需的所有第三方包"""
    packages = extract_imports(code)

    third_party = packages - STDLIB

    PACKAGE_NAME_MAP = {
        "sklearn": "scikit-learn",
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "bs4": "beautifulsoup4",
        "yaml": "pyyaml",
    }

    for pkg in third_party:
        pip_name = PACKAGE_NAME_MAP.get(pkg, pkg)
        try:
            __import__(pkg)
        except ImportError:
            print(f"📦 自动安装: {pip_name}")
            subprocess.run(
                ["pip", "install", pip_name],
                capture_output=True,
                timeout=120
            )


@tool
def execute_python_code(code: str, df: list) -> list[str]:
    # TUDO
    """这是一个执行python语句的函数，将sql查询结果在这一步进行处理，并且返回语句执行结果
    参数：
        code: python 语句
        df :上一步sql的查询结果
    """
    timeout = 30
    ensure_dependencies(code)

    data_json = json.dumps(df, ensure_ascii=False, default=str)
    prelude = '''
        import sys
        import json
        _data_json = sys.stdin.read()
        data = json.loads(_data_json)
    '''
    full_code = prelude + code
    try:
        result = subprocess.run(
            ["python", "-c", full_code],
            input=data_json,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
    except:
        pass


