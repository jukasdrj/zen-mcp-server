# Adding a New Tool to Zen MCP Server

**Purpose:** Step-by-step guide for creating new MCP tools.

---

## 🎯 Before You Start

**Questions:**
1. Is this a Simple tool (single-shot) or Workflow tool (multi-step)?
2. What model capabilities does it need? (thinking, vision, function calling)
3. Will it use conversation continuation?
4. What files/images will it need access to?

---

## 📋 Step-by-Step Process

### Step 1: Choose Tool Type

**Simple Tool** - Use for:
- Single-shot tasks
- Quick questions
- No investigation phases
- Examples: chat, challenge, apilookup

**Workflow Tool** - Use for:
- Multi-step investigation
- Confidence tracking needed
- Expert validation desired
- Examples: debug, codereview, planner

---

### Step 2: Create Tool File

**Location:** `tools/mytool.py`

**Simple Tool Template:**
```python
from pydantic import Field
from tools.shared.base_models import ToolRequest
from tools.simple.base import SimpleTool

class MyToolRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="AI model to use")
    absolute_file_paths: list[str] = Field(default_factory=list)
    working_directory_absolute_path: str = Field(...)

class MyTool(SimpleTool):
    def get_name(self) -> str:
        return "mytool"
    
    def get_description(self) -> str:
        return "Brief description for AI assistants"
    
    def get_request_model(self):
        return MyToolRequest
    
    async def execute_impl(self, request: MyToolRequest) -> dict:
        # Tool logic here
        response = await self.call_model(request.prompt, request.model)
        return {"success": True, "response": response}
```

**Workflow Tool Template:**
```python
from pydantic import Field
from tools.shared.base_models import WorkflowRequest
from tools.workflow.base import WorkflowTool

class MyToolRequest(WorkflowRequest):
    step: str = Field(..., description="Current step")
    step_number: int = Field(..., description="Step number")
    total_steps: int = Field(..., description="Total steps")
    next_step_required: bool = Field(...)
    findings: str = Field(..., description="Findings")
    model: str = Field(..., description="Model to use")

class MyTool(WorkflowTool):
    def get_name(self) -> str:
        return "mytool"
    
    def get_description(self) -> str:
        return "Brief description"
    
    def get_request_model(self):
        return MyToolRequest
    
    async def execute_impl(self, request: MyToolRequest) -> dict:
        if request.step_number == 1:
            return self._step_1_plan(request)
        elif request.next_step_required:
            return self._step_continue(request)
        else:
            return self._step_final(request)
```

---

### Step 3: Create System Prompt

**Location:** `systemprompts/mytool_prompt.py`

```python
MYTOOL_PROMPT = """
You are an expert assistant helping with [specific task].

Your role:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

Guidelines:
- Be systematic and thorough
- Provide specific examples
- Explain your reasoning

For workflow tools, follow investigation phases:
1. Plan approach
2. Execute investigation  
3. Validate findings
"""
```

---

### Step 4: Register Tool

**File:** `server.py`

```python
# Add import
from tools.mytool import MyTool

# Register in main()
server.add_tool(MyTool())
```

---

### Step 5: Add Tests

**Location:** `tests/test_mytool.py`

```python
import pytest
from tools.mytool import MyTool, MyToolRequest

@pytest.mark.vcr(cassette_name="mytool_basic.yaml")
def test_mytool_basic():
    tool = MyTool()
    request = MyToolRequest(
        prompt="Test prompt",
        model="gemini-2.5-pro",
        working_directory_absolute_path="/tmp"
    )
    result = tool.execute(request)
    assert result["success"]
```

---

### Step 6: Update Documentation

**Files to update:**
- `.robit/context.md` - Add tool to list
- `docs/tools/mytool.md` - Create tool documentation
- `CHANGELOG.md` - Note new tool

---

## ✅ Checklist

- [ ] Tool file created (`tools/mytool.py`)
- [ ] System prompt created (`systemprompts/mytool_prompt.py`)
- [ ] Tool registered (`server.py`)
- [ ] Tests added (`tests/test_mytool.py`)
- [ ] Documentation updated
- [ ] Quality checks pass (`./code_quality_checks.sh`)
- [ ] Manual testing complete

---

## 📚 References

- Simple tools: `tools/simple/`
- Workflow tools: `tools/workflow/`
- Patterns: `.robit/patterns.md`
- Context: `.robit/context.md`
