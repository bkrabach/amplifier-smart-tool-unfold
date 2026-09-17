"""Validated public inputs and the bounded HyperFrames authoring vocabulary."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UnfoldError(Exception):
    def __init__(self, code, message, remedy="Inspect the operation and correct the input."):
        self.code, self.message, self.remedy = code, message, remedy
        super().__init__(message)

    def as_dict(self):
        return {"code": self.code, "message": self.message, "remedy": self.remedy}


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Brief(Strict):
    title: str = Field(min_length=1, max_length=120)
    intent: str = Field(min_length=1, max_length=12000)
    context: str = Field(default="", max_length=30000)
    identity: str = Field(default="", max_length=5000)
    duration: float = Field(default=20, ge=5, le=60)


class Grant(Strict):
    provider: Literal["gemini", "openai", "anthropic"]
    model: str = Field(min_length=1, max_length=150)
    allow_context: bool = False
    allow_frames: bool = False
    vision: bool = False
    max_model_calls: int = Field(default=12, ge=1, le=24)
    max_tool_calls: int = Field(default=30, ge=1, le=60)
    max_renders: int = Field(default=3, ge=1, le=5)
    max_frames: int = Field(default=16, ge=1, le=40)
    max_seconds: int = Field(default=900, ge=30, le=1800)
    max_text_bytes: int = Field(default=5000000, ge=1000, le=5000000)
    max_image_bytes: int = Field(default=16000000, ge=1000, le=40000000)
    max_response_tokens: int = Field(default=12000, ge=1000, le=20000)


class Element(Strict):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    kind: Literal["card", "text", "line", "dot"]
    x: float = Field(ge=0, le=1280)
    y: float = Field(ge=0, le=720)
    width: float = Field(gt=0, le=1280)
    height: float = Field(gt=0, le=720)
    text: str = Field(default="", max_length=250)
    label: str = Field(default="", max_length=60)
    fill: str = Field(default="#142334", pattern=r"^#[0-9a-fA-F]{6}$")
    color: str = Field(default="#edf4f5", pattern=r"^#[0-9a-fA-F]{6}$")
    border: str = Field(default="#345368", pattern=r"^#[0-9a-fA-F]{6}$")
    font_size: int = Field(default=28, ge=16, le=80)
    opacity: float = Field(default=0, ge=0, le=1)
    radius: int = Field(default=14, ge=0, le=100)

    @model_validator(mode="after")
    def fits(self):
        if self.x + self.width > 1280 or self.y + self.height > 720:
            raise ValueError("Element must fit the 1280 × 720 canvas.")
        return self


class Tween(Strict):
    target: str
    at: float = Field(ge=0, le=60)
    duration: float = Field(default=0.5, ge=0, le=10)
    opacity: float | None = Field(default=None, ge=0, le=1)
    x: float | None = Field(default=None, ge=-1280, le=1280)
    y: float | None = Field(default=None, ge=-720, le=720)
    scale: float | None = Field(default=None, ge=0.1, le=3)
    ease: Literal["none", "power2.inOut", "power2.out", "power3.out"] = "power2.inOut"


class Scene(Strict):
    """Internal backend-specific authoring input, not a universal interchange format."""

    title: str = Field(min_length=1, max_length=120)
    duration: float = Field(ge=5, le=60)
    background: str = Field(default="#08131f", pattern=r"^#[0-9a-fA-F]{6}$")
    elements: list[Element] = Field(min_length=1, max_length=70)
    tweens: list[Tween] = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1, max_length=3000)

    @model_validator(mode="after")
    def references(self):
        ids = {element.id for element in self.elements}
        if "root" in ids:
            raise ValueError("The element ID root is reserved by the backend.")
        if len(ids) != len(self.elements):
            raise ValueError("Element IDs must be unique.")
        for tween in self.tweens:
            if tween.target not in ids or tween.at + tween.duration > self.duration:
                raise ValueError("Tween target or timing is invalid.")
        return self
