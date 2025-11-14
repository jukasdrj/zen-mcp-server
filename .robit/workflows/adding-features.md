# Feature Development Workflow

**Purpose:** Systematic approach to adding new features to Zen MCP Server.

---

## 📋 Phase 1: Planning (30 min)

### 1. Define Requirements
- What problem does this solve?
- Who will use this feature?
- What tools/providers are affected?
- Any breaking changes?

### 2. Design Review
- Review `.robit/architecture.md` for alignment
- Check `.robit/patterns.md` for applicable patterns
- Identify reusable components
- Plan testing strategy

---

## 🔧 Phase 2: Implementation (2-4 hours)

### 1. Create Branch
```bash
git checkout -b feature/my-feature
```

### 2. Implement Core Logic
- Follow `.robit/patterns.md`
- Add type hints
- Use Pydantic models
- Async for I/O

### 3. Add Tests

### 4. Run Quality Checks
```bash
./code_quality_checks.sh
```

---

## ✅ Phase 3: Testing (30 min)

### 1. Unit Tests
```bash
pytest tests/ -v -m "not integration"
```

### 2. Simulator Tests
```bash
python communication_simulator_test.py --quick
```

### 3. Manual Testing
- Test happy path
- Test error cases
- Test with different models

---

## 📝 Phase 4: Documentation (15 min)

### Update Files
- `.robit/context.md` - Add to relevant section
- `docs/` - Create feature documentation
- `CHANGELOG.md` - Add entry

---

## 📚 References

- Patterns: `.robit/patterns.md`
- Architecture: `.robit/architecture.md`
- Code Review: `.robit/prompts/code-review.md`
