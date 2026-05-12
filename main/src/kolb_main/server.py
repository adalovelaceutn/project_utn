from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI

from kolb_main.agent.graph import build_graph
from kolb_main.clients.profile_api import ProfileAPIClient
from kolb_main.clients.tavily_client import TavilyClient
from kolb_main.config import setting
from kolb_main.clients.profiler_a2a import ProfilerA2AClient
from kolb_main.clients.mcp_client import MainMCPClient
from kolb_main.kolb_chat import build_profile_chat_reply
from kolb_main.models import ChatRequest, ChatResponse
from kolb_main.topic_guard import BLOCKED_REPLY, is_topic_allowed

_state: dict[str, object] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    client = ProfilerA2AClient(
        base_url=setting.profiler_a2a_url,
        timeout_seconds=setting.a2a_timeout_seconds,
    )
    llm = None
    if setting.hf_token:
        llm = ChatOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=setting.hf_token,
            model=setting.hf_model_id,
            max_tokens=setting.hf_max_new_tokens,
            temperature=setting.hf_temperature,
        )

    _state["graph"] = build_graph(client)
    _state["mcp"] = MainMCPClient(setting.mcp_server_url)
    _state["profile_api"] = ProfileAPIClient(setting.api_base_url)
    _state["tavily"] = TavilyClient(setting.tavily_api_key, setting.tavily_base_url)
    _state["llm"] = llm
    yield
    _state.clear()


app = FastAPI(title="Kolb Main Agent", version="0.1.0", lifespan=lifespan)


def _graph():
    graph = _state.get("graph")
    if graph is None:
        raise HTTPException(status_code=503, detail="Main agent not ready")
    return graph

def _mcp():
    mcp = _state.get("mcp")
    if mcp is None:
        raise HTTPException(status_code=503, detail="MCP client not ready")
    return mcp


def _profile_api() -> ProfileAPIClient:
    client = _state.get("profile_api")
    if client is None:
        raise HTTPException(status_code=503, detail="Profile API client not ready")
    return client


def _llm() -> ChatOpenAI | None:
    return _state.get("llm")


def _tavily() -> TavilyClient | None:
    return _state.get("tavily")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid4())
    profile = await _profile_api().get_kolb_profile_by_username_optional(request.user.username)

    if profile is not None:
        allowed = await is_topic_allowed(
            message=request.message,
            profile=profile,
            llm=_llm(),
        )
        if not allowed:
            return ChatResponse(
                session_id=session_id,
                task_id=session_id,
                state="blocked",
                reply=BLOCKED_REPLY,
                profile=profile,
                persisted_profile_id=profile.get("id"),
            )

        reply = await build_profile_chat_reply(
            message=request.message,
            profile=profile,
            mcp_client=_mcp(),
            llm=_llm(),
            tavily_client=_tavily(),
        )
        return ChatResponse(
            session_id=session_id,
            task_id=session_id,
            state="completed",
            reply=reply,
            profile=profile,
            persisted_profile_id=profile.get("id"),
        )

    graph = _graph()
    result = await graph.ainvoke(
        {
            "session_id": session_id,
            "task_id": session_id,
            "incoming_message": request.message,
            "user_context": request.user.model_dump(),
            "profiler_metadata": request.user.to_profiler_metadata(),
            "a2a_task": None,
            "reply": None,
            "state": None,
            "profile": None,
            "persisted_profile_id": None,
        },
        {"configurable": {"thread_id": session_id}},
    )

    return ChatResponse(
        session_id=session_id,
        task_id=result["task_id"],
        state=result["state"],
        reply=result["reply"] or "No hubo respuesta del agente.",
        profile=result.get("profile"),
        persisted_profile_id=result.get("persisted_profile_id"),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": "kolb-main"}
    
@app.get("/theory/{style}")
async def get_theory(style: str) -> dict:
    """Obtiene información teórica del perfil Kolb desde el MCP."""
    try:
        mcp = _mcp()
        theory = await mcp.get_profile_theory(style)
        return theory
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/theory-general")
async def get_theory_general() -> dict:
    """Obtiene teoría general del modelo Kolb desde MCP (no atada a un perfil)."""
    try:
        mcp = _mcp()
        theory = await mcp.get_profile_theory("Convergente")
        return {
            "ejes": theory.get("ejes", {}),
            "descripcion_modelo": theory.get("descripcion_modelo", ""),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))