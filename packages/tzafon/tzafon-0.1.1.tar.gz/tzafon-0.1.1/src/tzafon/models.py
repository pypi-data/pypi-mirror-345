from __future__ import annotations
import json
import base64
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any, Self


class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    GOTO = "goto"
    SCREENSHOT = "screenshot"
    SET_VIEWPORT_SIZE = "set_viewport_size"


@dataclass(slots=True)
class Command:
    action_type: ActionType
    # optional payload
    x: Optional[float] = None
    y: Optional[float] = None
    text: Optional[str] = None
    delta_x: Optional[int] = None
    delta_y: Optional[int] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    timeout: int = 5000  # ms

    @classmethod
    def load(cls, body: bytes) -> Self:
        data = json.loads(body.decode("utf-8"))
        action_str = data.pop("action_type", None)
        if action_str is None:
            raise ValueError("Command missing 'action_type'")
        try:
            action_enum = ActionType(action_str)
        except ValueError as e:
            raise ValueError(f"Unknown action_type '{action_str}'") from e
        return cls(action_type=action_enum, **data)

    def dump(self) -> bytes:
        d = asdict(self)
        d["action_type"] = self.action_type.value
        d = {k: v for k, v in d.items() if v is not None}
        return json.dumps(d).encode("utf-8")


@dataclass(slots=True)
class Result:
    success: bool
    image: Optional[bytes] = None  # jpeg bytes
    error_message: Optional[str] = None

    @classmethod
    def load(cls, body: bytes) -> Self:
        data = json.loads(body.decode("utf-8"))
        img_b64 = data.get("image")
        img = base64.b64decode(img_b64) if img_b64 else None
        return cls(
            success=data.get("success", False),
            image=img,
            error_message=data.get("error_message"),
        )

    def dump(self) -> bytes:
        d: Dict[str, Any] = {
            "success": self.success,
            "error_message": self.error_message,
            "image": base64.b64encode(self.image).decode() if self.image else None,
        }
        return json.dumps({k: v for k, v in d.items() if v is not None}).encode()

    def __str__(self) -> str:
        ok = "✅" if self.success else "❌"
        img = "🖼️" if self.image else "—"
        return f"<Result {ok} image:{img} msg:{self.error_message!r}>"
