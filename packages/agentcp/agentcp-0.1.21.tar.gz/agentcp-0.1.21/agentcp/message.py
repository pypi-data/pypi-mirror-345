from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union


@dataclass
class Artifact:
    identifier: str
    title: str
    type: Literal[
        "application/vnd.ant.code",
        "text/markdown",
        "text/html",
        "image/svg+xml",
        "application/vnd.ant.mermaid",
        "application/vnd.ant.react",
    ]
    language: Optional[str] = None


@dataclass
class AssistantMessageBlock:
    type: Literal["content", "search", "reasoning_content", "error"]
    status: Literal["success", "loading", "cancel", "error", "reading", "optimizing"]
    timestamp: int
    content: Optional[str] = None
    stream: Optional[bool] = False
    prompt: Optional[str] = None  # Add prompt field to AssistantMessageBlock
    tools: Optional[str] = None
    extra: Optional[Dict[str, Union[str, int, List[dict]]]] = None
    artifact: Optional[Artifact] = None