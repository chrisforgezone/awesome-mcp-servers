"""
Tech QA Agent · 最小版 MCP Server
演示组合拳：知识库「目录」做 Resource，「语义检索」做 Tool。

依赖：uv pip install -p /Users/chris/Desktop/harness/.venv/bin/python3 "mcp[cli]" chromadb
运行：python tech_qa_server.py
调试：mcp dev tech_qa_server.py:mcp
注意：首次运行 chromadb 会下载一个小的 embedding 模型（约几十 MB，一次性）。
"""

import chromadb
from chromadb.config import Settings
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tech_qa")

# ── 一个最小知识库（真实项目里这些来自文档 / 工单 / wiki）──────────
KB = [
    {"id": "q1", "cat": "auth", "title": "登录接口返回 401 如何排查",
     "text": "登录接口返回 401 通常是 token 过期或签名错误。先确认请求头 "
             "Authorization 是否携带有效 token，再核对服务端时钟与签名密钥。"},
    {"id": "q2", "cat": "env", "title": "如何重置测试环境数据库",
     "text": "重置测试环境数据库：停掉应用，运行 reset_db.sh 清空并重建表结构，"
             "再执行 seed 脚本灌入基础数据。切勿在生产执行。"},
    {"id": "q3", "cat": "pay", "title": "支付回调超时的处理",
     "text": "支付回调超时时网关会重试三次。回调接口必须做幂等：用订单号去重，"
             "已处理过的回调直接返回成功，避免重复发货。"},
    {"id": "q4", "cat": "perf", "title": "接口压测的基本步骤",
     "text": "接口压测：先定义目标 QPS 与 P99 延迟，用 k6 或 locust 逐步加压，"
             "观察错误率与资源占用，出现拐点即为容量上限。"},
]

# 建集合并灌库（默认 embedding 会自动把 documents 向量化）
# 关掉遥测：否则它的输出可能污染 stdio 上的 JSON-RPC 流
_client = chromadb.Client(Settings(anonymized_telemetry=False))
_collection = _client.get_or_create_collection(name="tech_qa_kb")
_collection.add(
    ids=[d["id"] for d in KB],
    documents=[d["text"] for d in KB],
    metadatas=[{"cat": d["cat"], "title": d["title"]} for d in KB],
)


# ── 原语 1：Resource —— 知识库「目录」。只读，让人/模型先看有什么 ──────
@mcp.resource("kb://index")
def kb_index() -> str:
    """技术 QA 知识库目录：列出所有可检索条目的标题与分类。"""
    lines = [f"- [{d['cat']}] {d['title']}" for d in KB]
    return f"知识库目录（共 {len(KB)} 条）：\n" + "\n".join(lines)


# ── 原语 2：Tool —— 语义检索。由模型在运行时决定「搜什么」──────────────
@mcp.tool()
def search_kb(query: str, k: int = 2) -> str:
    """在技术 QA 知识库中做语义检索。
    用户提出技术问题时，必须先调用本工具检索知识库，并依据检索结果作答，
    不要凭自己的知识直接回答。

    Args:
        query: 检索问题，例如 "登录报 401"
        k: 返回最相关的条数，默认 2
    """
    res = _collection.query(query_texts=[query], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    if not docs:
        return "知识库未命中相关内容。"
    blocks = [f"【{m['title']}（{m['cat']}）】\n{d}" for d, m in zip(docs, metas)]
    return "\n\n".join(blocks)


if __name__ == "__main__":
    mcp.run()