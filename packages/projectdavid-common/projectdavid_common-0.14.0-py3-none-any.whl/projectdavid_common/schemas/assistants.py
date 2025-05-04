"""
projectdavid_common.schemas.assistants
-------------------------------------

Assistant - create / read / update models, 0.4-series.

* Adds `platform_tools`  (array of inline tool specs)
* Adds `tool_resources`  (dict keyed by tool-type → resource map)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from projectdavid_common.schemas.vectors import VectorStoreRead


# ────────────────────────────────────────────────────────────────────────────
#  ASSISTANT  •  CREATE
# ────────────────────────────────────────────────────────────────────────────
class AssistantCreate(BaseModel):
    id: Optional[str] = Field(
        None,
        description="Optional pre-generated assistant ID (leave blank for auto).",
    )
    name: str = Field(..., description="Assistant name")
    description: str = Field("", description="Brief description")
    model: str = Field(..., description="LLM model ID")
    instructions: str = Field("", description="System instructions / guidelines for the assistant")

    # ─── tool definitions ────────────────────────────────────────────
    tools: Optional[List[dict]] = Field(
        None, description="OpenAI-style tool specs (name, parameters …)"
    )
    platform_tools: Optional[List[Dict[str, Any]]] = Field(
        None,
        description=(
            "Inline platform tools. "
            "Example: [{'type': 'file_search', 'vector_store_ids': ['vs_123']}]"
        ),
    )
    tool_resources: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description=(
            "Per-tool resource map, keyed by tool type. Example:\n"
            "{\n"
            "  'code_interpreter': { 'file_ids': ['f_abc'] },\n"
            "  'file_search':     { 'vector_store_ids': ['vs_123'] }\n"
            "}"
        ),
    )

    # ─── misc settings ───────────────────────────────────────────────
    meta_data: Optional[dict] = Field(None, description="Free-form metadata")
    top_p: float = Field(1.0, ge=0, le=1, description="top-p sampling value")
    temperature: float = Field(1.0, ge=0, le=2, description="temperature value")
    response_format: str = Field("auto", description="Response format")

    # ─── webhook settings ────────────────────────────────────────────
    webhook_url: Optional[HttpUrl] = Field(
        None,
        description="Endpoint for run.action_required callbacks",
        examples=["https://myapp.com/webhooks/actions"],
    )
    webhook_secret: Optional[str] = Field(
        None,
        min_length=16,
        description="HMAC secret used to sign outgoing webhooks",
        examples=["whsec_ReplaceWithARealSecureSecret123"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Search Assistant",
                "description": "Assistant that can search company docs",
                "model": "gpt-4o-mini",
                "instructions": "Use tools when relevant.",
                "platform_tools": [{"type": "file_search", "vector_store_ids": ["vs_docs"]}],
                "tool_resources": {"file_search": {"vector_store_ids": ["vs_docs"]}},
                "top_p": 0.9,
                "temperature": 0.7,
            }
        }
    )


# ────────────────────────────────────────────────────────────────────────────
#  ASSISTANT  •  READ
# ────────────────────────────────────────────────────────────────────────────
class AssistantRead(BaseModel):
    id: str
    user_id: Optional[str] = None
    object: str
    created_at: int
    name: str
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None

    tools: Optional[List[dict]] = None
    platform_tools: Optional[List[Dict[str, Any]]] = None
    tool_resources: Optional[Dict[str, Dict[str, Any]]] = None

    meta_data: Optional[Dict[str, Any]] = None
    top_p: float
    temperature: float
    response_format: str

    vector_stores: List[VectorStoreRead] = Field(default_factory=list)
    webhook_url: Optional[HttpUrl] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "asst_abc123",
                "user_id": "user_xyz",
                "object": "assistant",
                "created_at": 1710000000,
                "name": "Search Assistant",
                "model": "gpt-4o-mini",
                "platform_tools": [{"type": "file_search", "vector_store_ids": ["vs_docs"]}],
                "tool_resources": {"file_search": {"vector_store_ids": ["vs_docs"]}},
                "top_p": 1.0,
                "temperature": 0.7,
                "response_format": "auto",
            }
        },
    )


# ────────────────────────────────────────────────────────────────────────────
#  ASSISTANT  •  UPDATE
# ────────────────────────────────────────────────────────────────────────────
class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    instructions: Optional[str] = None

    tools: Optional[List[Any]] = None
    platform_tools: Optional[List[Dict[str, Any]]] = None
    tool_resources: Optional[Dict[str, Dict[str, Any]]] = None

    meta_data: Optional[Dict[str, Any]] = None
    top_p: Optional[float] = Field(None, ge=0, le=1)
    temperature: Optional[float] = Field(None, ge=0, le=2)
    response_format: Optional[str] = None

    webhook_url: Optional[HttpUrl] = None
    webhook_secret: Optional[str] = Field(None, min_length=16)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated name",
                "platform_tools": [{"type": "calculator"}],
                "tool_resources": {"code_interpreter": {"file_ids": ["f_new_readme"]}},
            }
        }
    )
