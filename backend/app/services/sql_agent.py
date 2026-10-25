"""SQL agent: generate + run safe SELECT queries over uploaded tables.

In real mode the SQL is produced by the LLM; in Mock mode a small rule-based
generator is used so the demo works without credentials.
"""
import re
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, text

from ..config import settings
from .llm import _get_client, mock_enabled

MAX_WORDS = ["最多", "最高", "最大", "top", "Top", "前", "排名", "排行"]
AGG_WORDS = ["平均", "均值", "总和", "合计", "总数", "数量", "多少"]


def _is_numeric_type(t: str) -> bool:
    up = t.upper()
    return up.startswith(("INT", "FLOAT", "DOUBLE", "DECIMAL", "BIGINT", "NUMERIC"))


def _mock_generate_sql(question: str, tables: List[dict]) -> Optional[str]:
    if not tables:
        return None
    best = tables[0]
    for t in tables:
        cols = " ".join(c["name"] for c in (t["schema"] or []))
        if any(k in cols for k in MAX_WORDS + AGG_WORDS):
            best = t
            break
    table = best["table_name"]
    schema = best["schema"] or []
    num_cols = [c["name"] for c in schema if _is_numeric_type(c["type"])]

    if any(k in question for k in MAX_WORDS):
        if num_cols:
            return f"SELECT * FROM `{table}` ORDER BY `{num_cols[0]}` DESC LIMIT 10"
        return f"SELECT * FROM `{table}` LIMIT 20"
    if any(k in question for k in AGG_WORDS):
        if num_cols:
            return f"SELECT AVG(`{num_cols[0]}`) AS avg_{num_cols[0]} FROM `{table}`"
        return f"SELECT COUNT(*) AS total FROM `{table}`"
    return f"SELECT * FROM `{table}` LIMIT 20"


def _clean_sql(sql: str) -> str:
    sql = re.sub(r"```(sql)?", "", sql).strip()
    sql = sql.strip().rstrip(";")
    # keep only the first select statement
    sql = re.sub(r"[\r\n]+", " ", sql).strip()
    return sql


def generate_sql(question: str, tables: List[dict]) -> Optional[str]:
    if not tables:
        return None
    if mock_enabled():
        return _mock_generate_sql(question, tables)
    descs = "\n".join(
        f"表 `{t['table_name']}` 的列: " + ", ".join(
            f"{c['name']} ({c['type']})" for c in (t["schema"] or [])
        )
        for t in tables
    )
    system = (
        "你是一个数据分析 SQL 助手。根据用户问题，在给出的表上生成一条只读 SELECT 查询。"
        "只输出 SQL，不要任何解释。"
    )
    user = f"表结构：\n{descs}\n\n用户问题：{question}\n\n请生成 SQL："
    client = _get_client()
    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    return _clean_sql(resp.choices[0].message.content or "")


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from ..database import create_engine_with_db
        _engine = create_engine_with_db()
    return _engine


def execute_sql(sql: str, limit: int = 200) -> Tuple[List[str], List[list]]:
    sql = _clean_sql(sql)
    if not re.match(r"(?is)^\s*select\b", sql):
        raise ValueError("仅允许执行只读 SELECT 查询")
    if "limit" not in sql.lower():
        sql = f"{sql} LIMIT {limit}"
    eng = _get_engine()
    with eng.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [list(row) for row in result.fetchmany(limit)]
        conn.rollback()
    return columns, rows


def suggest_chart(question: str, columns: List[str], rows: List[list]) -> Optional[dict]:
    if not rows or len(columns) < 2:
        return None

    def is_num(v):
        try:
            if v is None:
                return False
            float(v)
            return True
        except (TypeError, ValueError):
            return False

    num_idx = next((i for i in range(len(columns)) if any(is_num(r[i]) for r in rows)), None)
    if num_idx is None or num_idx == 0:
        return None

    chart_type = "bar"
    if any(k in question for k in ("趋势", "变化", "走势", "时间")):
        chart_type = "line"
    elif any(k in question for k in ("占比", "比例", "构成")):
        chart_type = "pie"

    return {
        "type": chart_type,
        "x_field": columns[0],
        "y_field": columns[num_idx],
        "data": rows[:50],
    }
