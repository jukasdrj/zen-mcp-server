# Provider Debugging Workflow

**Purpose:** Systematic approach to debugging provider issues.

---

## 🔍 Common Provider Issues

### 1. Provider Not Found
- Check API key is set
- Verify provider registered in server.py
- Check model name in conf/*.json

### 2. API Call Failures
- Verify API key is valid
- Check rate limits
- Increase timeout settings

### 3. Response Parsing Errors
- Update response parsing logic
- Handle missing fields gracefully
- Add validation

---

## 📚 References

- Providers: `providers/`
- Base Class: `providers/base.py`
- Patterns: `.robit/patterns.md`
