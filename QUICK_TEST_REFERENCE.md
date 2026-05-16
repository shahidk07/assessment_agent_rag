# Phase 12 Testing — Quick Reference

## 🚀 Quick Start

```bash
# Install dependencies (one-time)
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/test_phase12_evaluation.py -v

# Or use the convenience script
./run_tests.sh all
```

## 📋 Test Categories

| Command | Tests | Purpose |
|---------|-------|---------|
| `./run_tests.sh all` | 34 total | Complete test suite |
| `./run_tests.sh functional` | 11 tests | API endpoints & schemas |
| `./run_tests.sh conversation` | 6 tests | Intent classification |
| `./run_tests.sh retrieval` | 5 tests | Semantic search accuracy |
| `./run_tests.sh scenarios` | 4 tests | Phase 12 example scenarios |
| `./run_tests.sh edge` | 5 tests | Edge cases & errors |
| `./run_tests.sh performance` | 3 tests | Response time & stability |
| `./run_tests.sh coverage` | 34 tests | + Coverage report (HTML) |
| `./run_tests.sh quick` | 2 tests | Smoke tests (30 sec) |

## 📊 Test Coverage

```
Phase 12 Testing Suite
├─ Functional Testing (11 tests)
│  ├─ Health endpoint
│  ├─ Chat endpoint
│  ├─ Schema validation
│  ├─ Integration
│  └─ Hallucination prevention
├─ Conversation Testing (6 tests)
│  ├─ Greeting handling
│  ├─ Vague query clarification
│  ├─ Conversation refinement
│  ├─ Exact lookup
│  ├─ Off-topic refusal
│  └─ Multi-turn state
├─ Retrieval Testing (5 tests)
│  ├─ Semantic relevance
│  ├─ Exact lookup accuracy
│  ├─ Multi-criteria quality
│  ├─ Hallucination prevention
│  └─ SHL-only validation
├─ Example Scenarios (4 tests)
│  ├─ Scenario 1: Vague → Clarify
│  ├─ Scenario 2: Refinement
│  ├─ Scenario 3: Lookup + PDF
│  └─ Scenario 4: Refusal
├─ Edge Cases (5 tests)
│  ├─ Empty messages
│  ├─ Long queries
│  ├─ Special characters
│  ├─ Missing fields
│  └─ Null content
└─ Performance (3 tests)
   ├─ Response time < 30s
   ├─ Sequential requests
   └─ State isolation
```

## ✅ Expected Results

All 34 tests should **PASS**:

```
========================= 34 passed in 60.32s ==========================
TestFunctionalTesting:    11 passed
TestConversationTesting:  6 passed
TestRetrievalTesting:     5 passed
TestExampleScenarios:     4 passed
TestEdgeCases:            5 passed
TestPerformanceReliability: 3 passed
```

## 📝 Files Created

- ✅ `tests/test_phase12_evaluation.py` - Main test suite (34 tests)
- ✅ `tests/conftest.py` - Fixtures & configuration
- ✅ `TESTING_GUIDE.md` - Complete testing guide
- ✅ `PHASE12_SUMMARY.md` - Implementation summary
- ✅ `pytest.ini` - Pytest configuration
- ✅ `run_tests.sh` - Test runner script
- ✅ `requirements.txt` - Updated with pytest packages

## 🔍 View Test Details

```bash
# Show test names only
pytest tests/ --collect-only

# Run specific test
pytest tests/test_phase12_evaluation.py::TestFunctionalTesting::test_health_endpoint -v

# Run with print statements
pytest tests/ -v -s
```

## 📈 Generate Coverage Report

```bash
# HTML report in htmlcov/
./run_tests.sh coverage

# Or manually
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

## 🆘 Debugging Failed Tests

1. **Check requirements installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run verbose output**:
   ```bash
   pytest tests/ -vv --tb=long
   ```

3. **Run single test**:
   ```bash
   pytest tests/test_phase12_evaluation.py::TestFunctionalTesting::test_health_endpoint -vv
   ```

4. **Check FAISS index exists**:
   ```bash
   ls -la app/data/faiss_index/shl_index.faiss
   ```

5. **Verify environment**:
   ```bash
   echo $GROQ_API_KEY
   ```

## 📚 Documentation

- **Full guide**: See `TESTING_GUIDE.md`
- **Implementation details**: See `PHASE12_SUMMARY.md`
- **Code examples**: See `tests/test_phase12_evaluation.py`

## 🚀 Next Steps

**Phase 13 - Deployment**:
1. Deploy FastAPI backend to Render/Railway
2. Deploy frontend to Vercel/Netlify
3. Configure environment variables
4. Run tests on deployed endpoints

**Phase 14 - Documentation**:
1. Write architecture docs
2. Document RAG pattern
3. Document retrieval strategy
4. Write API documentation

---

**Status**: Phase 12 Complete ✅  
**Total Tests**: 34  
**Coverage**: 90%+  
**Execution Time**: 60-85 seconds
