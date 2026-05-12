from __future__ import annotations

import operator
from typing import Annotated, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class InterviewState(TypedDict):
    # Student identification
    student_id: str

    # Interview progress
    history: list[dict]           # {scenario_id, scenario_title, option_id, dimension, raw_response}
    current_scenario: Optional[dict]
    current_question: Optional[str]   # LLM-formatted question shown to student
    position: int
    remaining: int
    partial_scores: dict          # running tally {EC, OR, CA, EA}

    # LLM conversation (managed by add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Final output
    kolb_profile: Optional[dict]
    persisted_profile_id: Optional[str]

    # Error
    error: Optional[str]
