"""LLM client wrapper.

Supports OpenAI-compatible APIs for real inference, plus a Mock mode so the
whole pipeline (upload -> SQL -> RAG -> chat) can run without any credentials.
Switch to a real model by setting LLM_API_KEY / LLM_BASE_URL / LLM_MODEL in .env
and LLM_MOCK=false.
"""
from typing import Iterator, List, Optional

from ..config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY or "sk-mock-placeholder",
        )
    return _client


def mock_enabled() -> bool:
    return settings.LLM_MOCK or not settings.LLM_API_KEY


def stream_chat(
    system: str,
    user: str,
    history: Optional[List[dict]] = None,
    max_tokens: int = 1024,
) -> Iterator[str]:
    """Yield answer text chunks (streaming)."""
    if mock_enabled():
        yield from _mock_stream(system, user)
        return

    client = _get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user})

    stream = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        stream=True,
        max_tokens=max_tokens,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _mock_stream(system: str, user: str) -> Iterator[str]:
    """A simple rule-based mock answer so the demo flows without a real LLM."""
    text = user.strip()
    template = (
        "（Mock 模式回答。当前未配置真实大模型 API，以下为基于数据库检索的演示性结论。）\n\n"
    )
    if any(k in text for k in ("最多", "最高", "最大", "top", "Top")):
        template += "综合所查表的统计结果，排名靠前的记录已在上方表格中展示。\n\n"
        template += "建议关注数值最高的几项，并结合文档上下文进一步核对原因。"
    elif any(k in text for k in ("平均", "均值", "总和", "合计", "总数", "数量", "多少")):
        template += "已对所选字段完成聚合统计，结果如上方表格所示。\n\n"
        template += "如需细分维度（按时间、分类等）可进一步下钻查询。"
    elif any(k in text for k in ("文档", "报告", "内容", "是什么", "说明", "总结")):
        template += "已检索到相关文档片段并作为参考，与本次问题相关的要点已在上方上下文列出。\n\n"
        template += "您还可以继续追问更具体的细节。"
    else:
        template += (
            "已根据您的提问检索数据库中的结构化数据与文档上下文，并给出初步分析。\n\n"
            "请前往 .env 配置真实的 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL 并设置 "
            "LLM_MOCK=false，即可获得由大模型驱动的完整智能分析回答。"
        )
    # Emit a few chunks to simulate streaming.
    step = max(1, len(template) // 10)
    for i in range(0, len(template), step):
        yield template[i:i + step]
