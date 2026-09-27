#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import decimal
import json
import tempfile
import time
from pathlib import Path

from src.agent.state import Agentstate
from src.agent.tools import tools_dict

INLINE_MAX_ROWS = 5000          # 超过该行数落盘
INLINE_MAX_BYTES = 2 * 1024 * 1024  # 超过该字节数落盘（2MB）
DATA_DIR = Path(tempfile.gettempdir()) / "agent_data"  # 落盘目录（系统临时目录）


def _json_default(obj):
    """JSON 序列化兜底：Decimal→float（保持数值），datetime→ISO 字符串"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)


def _rows(result) -> int:
    if isinstance(result, list):
        return len(result)
    if isinstance(result, dict):
        return 1
    return 0


def _estimate_size(result) -> int:
    """估算结果的 JSON 序列化字节数（近似）"""
    try:
        return len(json.dumps(result, ensure_ascii=False, default=_json_default))
    except Exception:
        return 0


def _should_spill(result) -> bool:
    return _rows(result) > INLINE_MAX_ROWS or _estimate_size(result) > INLINE_MAX_BYTES



def _spill_to_file(result, step_id):
    """大结果落盘，返回文件引用结构"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"step_{step_id}_{int(time.time() * 1000)}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return {"type": "file", "path": str(path), "rows": _rows(result)}


def _maybe_spill(result, step_id):
    """结果超过阈值则落盘，否则原样返回"""
    if _should_spill(result):
        return _spill_to_file(result, step_id)
    return result


def _resolve_data_sources(state, ds_map):

    resolved = {}
    step_results = {r.get("step_id"): r.get("result") for r in state.get("step_results", [])}

    for var, spec in (ds_map or {}).items():
        step_id = spec.get("step_id") if isinstance(spec, dict) else None
        if step_id is None:
            resolved[var] = {"type": "error", "message": f"数据源 {var} 缺少 step_id"}
            continue

        result = step_results.get(step_id)
        if result is None:
            resolved[var] = {"type": "error", "message": f"数据源 {var} 引用的 step_id={step_id} 不存在或未执行"}
            continue

        if isinstance(result, str) and (result.startswith("error") or "错误" in result):
            resolved[var] = {"type": "error", "message": f"数据源 {var} 引用的 step_id={step_id} 执行出错：{result[:200]}"}
            continue

        if _should_spill(result):
            resolved[var] = _spill_to_file(result, step_id)
        else:
            resolved[var] = {"type": "inline", "data": result}

    return resolved


def _validate_file_refs(ds_map):
    root = DATA_DIR.resolve()
    for var, spec in (ds_map or {}).items():
        if not isinstance(spec, dict) or spec.get("type") != "file":
            continue
        p = Path(spec["path"]).resolve()
        if p != root and root not in p.parents:
            spec["type"] = "error"
            spec["message"] = f"非法文件路径：{spec['path']}"
    return ds_map


def executor(state: Agentstate) -> Agentstate:

    plan = state["plan"]
    for step in plan:
        tool_name = step.get("tool_name")
        tool_args = dict(step.get("tool_args") or {})

        # python 工具：解析 data_sources 并注入数据
        if tool_name in ("python_exec", "execute_python_code") and "data_sources" in tool_args:
            ds = _resolve_data_sources(state, tool_args["data_sources"])
            ds = _validate_file_refs(ds)
            tool_args["data_sources"] = ds

        tool = tools_dict.get(tool_name)
        if tool is None:
            result = f"错误：找不到工具 {tool_name}"
        else:
            try:
                result = tool.invoke(tool_args)
            except Exception as e:
                result = f"error: 工具 {tool_name} 执行失败：{e}"

        # 大结果降级落盘（sql_query 等工具返回大列表时）
        step_id = step.get("step_id")
        result = _maybe_spill(result, step_id)

        state["step_results"].append({"step_id": step_id, "result": result})

    return state
