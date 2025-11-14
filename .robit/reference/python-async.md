# Python Async/Await Best Practices

**Python Version:** 3.9+
**Last Updated:** November 2025

---

## 🎯 When to Use Async

**Use async for:**
- Network I/O (API calls, HTTP requests)
- File I/O (large files)
- Database queries
- Multiple concurrent operations

**Don't use async for:**
- CPU-bound tasks (use multiprocessing)
- Simple synchronous operations
- When not calling async functions

---

## 🔧 Basic Patterns

### Defining Async Functions

```python
# Async function
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Calling async function
result = await fetch_data("https://api.example.com/data")
```

### Async Context Managers

```python
# ✅ CORRECT: Async context manager
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as response:
        result = await response.text()

# ❌ WRONG: Sync context manager with async
with aiohttp.ClientSession() as session:  # Error!
    response = await session.get(url)
```

---

## 🚨 Common Pitfalls

### 1. Forgetting await

```python
# ❌ WRONG: Coroutine not awaited
response = provider.generate(request)  # Returns coroutine, not result!

# ✅ CORRECT: Await coroutine
response = await provider.generate(request)
```

### 2. Mixing Sync/Async

```python
# ❌ WRONG: Sync function calling async
def execute(self, request):
    response = await provider.generate(request)  # Error!

# ✅ CORRECT: Async all the way
async def execute(self, request):
    response = await provider.generate(request)
```

### 3. Blocking Operations in Async

```python
# ❌ WRONG: Blocking sync call
async def process():
    data = requests.get(url)  # Blocks event loop!
    
# ✅ CORRECT: Async HTTP client
async def process():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
```

---

## 🚀 Zen MCP Patterns

### Provider Generate Method

```python
class MyProvider(ModelProvider):
    async def generate(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.5,
        **kwargs
    ) -> ModelResponse:
        async with self.session.post(self.api_url, json={
            "messages": messages,
            "model": model,
            "temperature": temperature
        }) as response:
            content = await response.text()
            return ModelResponse(content=content)
```

### Tool Execute Method

```python
class MyTool(SimpleTool):
    async def execute_impl(self, request: MyToolRequest) -> dict:
        # Call async provider
        response = await self.call_model(
            request.prompt,
            request.model
        )
        return {"success": True, "response": response}
```

---

## 📚 References

- Python Async: https://docs.python.org/3/library/asyncio.html
- aiohttp: https://docs.aiohttp.org/
- Patterns: `.robit/patterns.md`
