# Pydantic Request/Response Patterns

**Pydantic Version:** 2.x
**Python:** 3.9+
**Last Updated:** November 2025

---

## 🎯 Why Pydantic?

**Benefits:**
- Automatic type validation
- Clear error messages
- Self-documenting APIs
- IDE autocomplete support
- Eliminates boilerplate validation code

---

## 🔧 Tool Request Models

### Base Classes

**All tool requests inherit from:**
- `ToolRequest` - Simple tools
- `WorkflowRequest` - Workflow tools

```python
from pydantic import Field
from tools.shared.base_models import ToolRequest, WorkflowRequest
```

### Simple Tool Request

```python
class ChatRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="AI model to use")
    absolute_file_paths: list[str] = Field(
        default_factory=list,
        description="Files to include"
    )
    images: list[str] = Field(default_factory=list)
    working_directory_absolute_path: str = Field(...)
    continuation_id: Optional[str] = Field(default=None)
```

### Workflow Tool Request

```python
class DebugRequest(WorkflowRequest):
    step: str = Field(..., description="Investigation step")
    step_number: int = Field(..., ge=1, description="Current step")
    total_steps: int = Field(..., ge=1, description="Total steps")
    next_step_required: bool = Field(...)
    findings: str = Field(..., description="Findings")
    hypothesis: str = Field(..., description="Current theory")
    confidence: Literal[
        "exploring", "low", "medium", "high", 
        "very_high", "almost_certain", "certain"
    ] = Field(default="exploring")
    model: str = Field(...)
```

---

## 🚨 Field Descriptions

**CRITICAL:** Field descriptions are shown to AI assistants!

```python
# ❌ WRONG: No description
prompt: str = Field(...)

# ✅ CORRECT: Clear description
prompt: str = Field(
    ..., 
    description="User question or idea for collaborative thinking"
)

# ✅ BETTER: Detailed with warnings
prompt: str = Field(
    ...,
    description=(
        "User prompt to send to external model. "
        "WARNING: Large inline code must NOT be shared in prompt. "
        "Provide full-path to files on disk as separate parameter."
    )
)
```

---

## ✅ Validation Patterns

### Custom Validators

```python
from pydantic import model_validator

class DebugRequest(WorkflowRequest):
    step_number: int
    total_steps: int
    
    @model_validator(mode="after")
    def validate_step_progression(self) -> "DebugRequest":
        if self.step_number > self.total_steps:
            raise ValueError(
                f"step_number ({self.step_number}) cannot exceed "
                f"total_steps ({self.total_steps})"
            )
        return self
```

### Field Constraints

```python
class MyRequest(ToolRequest):
    # Positive integer
    count: int = Field(..., gt=0)
    
    # Range constraint
    temperature: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # String length
    name: str = Field(..., min_length=1, max_length=100)
    
    # Regex pattern
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

---

## 📚 References

- Pydantic Docs: https://docs.pydantic.dev/
- Base Models: `tools/shared/base_models.py`
- Examples: `tools/chat.py`, `tools/debug.py`
- Patterns: `.robit/patterns.md`
