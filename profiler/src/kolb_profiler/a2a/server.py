"""FastAPI A2A server — exposes the Kolb Profiler via the A2A protocol."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI

from kolb_profiler.a2a.handler import A2AHandler
from kolb_profiler.a2a.models import (
    AGENT_CARD,
    JSONRPCRequest,
    JSONRPCResponse,
    Message,
    SendTaskParams,
    TextPart,
)
from kolb_profiler.agent.graph import build_graph
from kolb_profiler.clients.mcp import KolbMCPClient
from kolb_profiler.clients.profiler_api import ProfilerAPIClient
from kolb_profiler.config import setting

# ---------------------------------------------------------------------------
# Application state container
# ---------------------------------------------------------------------------

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build LLM, clients and graph once at startup."""
    # LLM — via Hugging Face OpenAI-compatible endpoint.
    llm = ChatOpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=setting.hf_token,
        model=setting.hf_model_id,
        max_tokens=setting.hf_max_new_tokens,
        temperature=setting.hf_temperature,
    )

    mcp_client = KolbMCPClient(setting.mcp_server_url)
    api_client = ProfilerAPIClient(setting.api_base_url)

    # Initialize MCP session
    await mcp_client.initialize()

    graph = build_graph(mcp_client, api_client, llm)
    _state["handler"] = A2AHandler(graph)

    yield
    _state.clear()


app = FastAPI(title="Kolb Profiler A2A", version="0.1.0", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handler() -> A2AHandler:
    h = _state.get("handler")
    if h is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return h


def _error_response(req_id, code: int, message: str) -> JSONRPCResponse:
    return JSONRPCResponse(id=req_id, error={"code": code, "message": message})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/.well-known/agent.json")
def agent_card():
    """A2A agent discovery endpoint."""
    return AGENT_CARD


@app.post("/")
async def rpc_dispatcher(request: JSONRPCRequest) -> JSONResponse:
    """JSON-RPC dispatcher for A2A methods."""
    method = request.method
    req_id = request.id

    if method == "tasks/send":
        try:
            params = SendTaskParams(**request.params)
        except Exception as exc:
            return JSONResponse(
                _error_response(req_id, -32602, str(exc)).model_dump()
            )
        try:
            task = await _handler().send(params.id, params.message, params.metadata)
        except Exception as exc:
            return JSONResponse(
                _error_response(req_id, -32000, f"tasks/send failed: {exc}").model_dump()
            )
        return JSONResponse(JSONRPCResponse(id=req_id, result=task.model_dump()).model_dump())

    elif method == "tasks/get":
        task_id = request.params.get("id")
        task = _handler().get(task_id)
        if task is None:
            return JSONResponse(
                _error_response(req_id, -32001, f"Task {task_id!r} not found").model_dump()
            )
        return JSONResponse(JSONRPCResponse(id=req_id, result=task.model_dump()).model_dump())

    elif method == "tasks/cancel":
        task_id = request.params.get("id")
        task = _handler().cancel(task_id)
        if task is None:
            return JSONResponse(
                _error_response(req_id, -32001, f"Task {task_id!r} not found").model_dump()
            )
        return JSONResponse(JSONRPCResponse(id=req_id, result=task.model_dump()).model_dump())

    else:
        return JSONResponse(
            _error_response(req_id, -32601, f"Method {method!r} not found").model_dump()
        )


@app.get("/health")
def health():
    return {"status": "ok", "agent": "kolb-profiler"}
