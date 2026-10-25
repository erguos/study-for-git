import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ChatMessage, Dataset
from ..schemas import ChatRequest
from ..services import sql_agent
from ..services.llm import stream_chat
from ..services.vector_store import vector_store

router = APIRouter(prefix="/api", tags=["chat"])


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _load_tables(db: Session):
    tables = []
    rows = db.query(Dataset).filter(Dataset.type == "table", Dataset.status == "ready").all()
    for r in rows:
        tables.append({
            "id": r.id,
            "name": r.name,
            "table_name": r.table_name,
            "schema": r.schema_json or [],
        })
    return tables


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    question = (req.message or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="消息不能为空")

    tables = _load_tables(db)
    docs = vector_store.search(db, question, top_k=5)
    doc_text = "\n".join(f"- {d['content']}" for d in docs)

    sql = None
    table_result = None
    chart = None
    try:
        sql = sql_agent.generate_sql(question, tables)
        if sql:
            columns, rows = sql_agent.execute_sql(sql)
            table_result = {"columns": columns, "rows": rows}
            chart = sql_agent.suggest_chart(question, columns, rows)
    except Exception:
        sql = None
        table_result = None
        chart = None

    # Save user message
    db.add(ChatMessage(role="user", content=question))
    db.commit()

    extra = {
        "sql": sql,
        "table": table_result,
        "chart": chart,
        "docs": docs,
    }

    # Build prompt for the (real) LLM; Mock ignores these but we still stream.
    system = (
        "你是一个智能数据分析 Agent。你会看到用户上传的数据表结构、通过 SQL 查询得到的结构化结果，"
        "以及检索到的相关文档片段。请基于这些真实数据，用自然语言回答用户的问题，做到准确、有条理。"
        "如需引用数字，以结构化结果为准。"
    )
    user_prompt = f"用户问题：{question}\n\n"
    if tables:
        user_prompt += "表结构：\n" + "\n".join(
            f"- 表 `{t['table_name']}`: " + ", ".join(
                c["name"] for c in (t["schema"] or [])
            ) for t in tables
        ) + "\n"
    if table_result:
        user_prompt += f"\nSQL 查询结果（列: {table_result['columns']}，前若干行: {table_result['rows'][:20]}）\n"
    if doc_text:
        user_prompt += f"\n检索到的相关文档：\n{doc_text}\n"
    user_prompt += "\n请给出你的分析回答。"

    def event_stream():
        # 1) metadata: SQL result + chart + docs so the frontend can render them
        yield _sse({"type": "meta", "extra": extra})
        # 2) streaming answer text
        collected = []
        for piece in stream_chat(system, user_prompt):
            collected.append(piece)
            yield _sse({"type": "delta", "text": piece})
        full_text = "".join(collected)
        # 3) persist assistant message
        db.add(ChatMessage(role="assistant", content=full_text, extra=extra))
        db.commit()
        yield _sse({"type": "done"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from ..schemas import ChatMessageOut
    items = db.query(ChatMessage).order_by(ChatMessage.id.asc()).limit(100).all()
    return {"messages": [ChatMessageOut.model_validate(m) for m in items]}
