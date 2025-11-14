# Adding a New Provider to Zen MCP Server

**Purpose:** Step-by-step guide for integrating new AI providers.

---

## 📋 Step-by-Step Process

### Step 1: Create Provider Class

**Location:** `providers/myprovider.py`

```python
from providers.base import ModelProvider
from providers.shared import ModelCapabilities, ModelResponse, ProviderType

class MyProvider(ModelProvider):
    MODEL_CAPABILITIES = {
        "my-model": ModelCapabilities(
            model_name="my-model",
            friendly_name="My Provider (My Model)",
            aliases=["mymodel"],
            intelligence_score=15,
            description="Model description",
            context_window=100000,
            max_output_tokens=8192,
            supports_extended_thinking=True,
            supports_images=True,
            supports_temperature=True
        )
    }
    
    def get_provider_type(self) -> ProviderType:
        return ProviderType.CUSTOM
    
    async def generate(self, messages, model, **kwargs) -> ModelResponse:
        # Provider-specific API calls
        return ModelResponse(content="...")
```

---

### Step 2: Create Model Config

**Location:** `conf/myprovider_models.json`

```json
{
  "_README": {
    "description": "Model metadata for My Provider"
  },
  "models": [
    {
      "model_name": "my-model",
      "friendly_name": "My Provider (My Model)",
      "aliases": ["mymodel"],
      "intelligence_score": 15,
      "context_window": 100000,
      "max_output_tokens": 8192,
      "supports_extended_thinking": true
    }
  ]
}
```

---

### Step 3: Register Provider

**File:** `server.py`

```python
from providers.myprovider import MyProvider

# In main()
if os.getenv("MYPROVIDER_API_KEY"):
    registry.register_provider(MyProvider(
        api_key=os.getenv("MYPROVIDER_API_KEY")
    ))
```

---

### Step 4: Add Tests

```python
@pytest.mark.integration
def test_myprovider():
    provider = MyProvider(api_key="test-key")
    response = await provider.generate(
        messages=[{"role": "user", "content": "Hello"}],
        model="my-model"
    )
    assert response.content
```

---

### Step 5: Update Documentation

- `.robit/context.md` - Add to provider list
- `docs/myprovider.md` - Provider documentation
- `.env.example` - Add MYPROVIDER_API_KEY

---

## ✅ Checklist

- [ ] Provider class created
- [ ] Model config JSON created
- [ ] Provider registered in server.py
- [ ] Tests added
- [ ] Documentation updated
- [ ] Environment variable documented

---

## 📚 References

- Base class: `providers/base.py`
- Example: `providers/gemini.py`
- Patterns: `.robit/patterns.md`
