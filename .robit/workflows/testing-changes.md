# Testing Changes Workflow

**Purpose:** Comprehensive testing workflow for all code changes.

---

## ✅ Step-by-Step Testing

### Step 1: Unit Tests (Required)

```bash
pytest tests/ -v -m "not integration"
```

### Step 2: Quality Checks (Required)

```bash
./code_quality_checks.sh
```

### Step 3: Simulator Tests (Recommended)

```bash
python communication_simulator_test.py --quick
```

### Step 4: Integration Tests (Optional)

```bash
./run_integration_tests.sh
```

---

## 📚 References

- Testing Guide: `.robit/reference/testing-guide.md`
- Patterns: `.robit/patterns.md`
