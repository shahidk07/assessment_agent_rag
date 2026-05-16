# Phase 12 Testing Guide

## Overview

This guide explains how to run the Phase 12 testing suite for the SHL Assessment Recommender system.

## Prerequisites

Ensure the following are installed:

```bash
pip install pytest pytest-cov httpx
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

## Test Structure

The test suite is organized into five main categories:

### 1. Functional Testing (`TestFunctionalTesting`)
- **Health Endpoint**: Verifies `/health` responds with correct status
- **Chat Endpoint**: Tests valid/invalid request schemas
- **Response Schema**: Validates response contains required fields
- **Integration**: Tests frontend-backend communication
- **Hallucination Prevention**: Ensures only SHL URLs are recommended

### 2. Conversation Testing (`TestConversationTesting`)
- **Greeting Handling**: Tests greeting recognition
- **Vague Query Clarification**: Tests clarification requests
- **Refinement Handling**: Tests conversation refinement
- **Lookup Queries**: Tests exact assessment retrieval
- **Refusal Behavior**: Tests off-topic refusal
- **Conversation Continuity**: Tests multi-turn conversation state

### 3. Retrieval Testing (`TestRetrievalTesting`)
- **Semantic Relevance**: Tests semantic search quality
- **Exact Lookup Accuracy**: Tests direct assessment lookup
- **Recommendation Quality**: Tests multi-criteria recommendations
- **Hallucination Prevention**: Tests no fabricated assessments
- **SHL-Only Validation**: Ensures all URLs are from SHL catalog

### 4. Example Scenarios (`TestExampleScenarios`)
- **Scenario 1**: Vague query → clarification
- **Scenario 2**: Refinement → updated recommendations
- **Scenario 3**: Lookup → exact assessment retrieval
- **Scenario 4**: Refusal → off-topic handling

### 5. Edge Cases & Performance (`TestEdgeCases`, `TestPerformanceReliability`)
- Empty/long/special character queries
- Response time validation
- Sequential request handling
- State isolation

## Running Tests

### Run All Tests
```bash
pytest tests/test_phase12_evaluation.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_phase12_evaluation.py::TestFunctionalTesting -v
```

### Run Specific Test
```bash
pytest tests/test_phase12_evaluation.py::TestFunctionalTesting::test_health_endpoint -v
```

### Run with Coverage
```bash
pytest tests/test_phase12_evaluation.py --cov=app --cov-report=html
```

### Run with Detailed Output
```bash
pytest tests/test_phase12_evaluation.py -vv --tb=long
```

### Run Specific Test Category
```bash
# Functional tests only
pytest tests/test_phase12_evaluation.py::TestFunctionalTesting -v

# Conversation tests only
pytest tests/test_phase12_evaluation.py::TestConversationTesting -v

# Retrieval tests only
pytest tests/test_phase12_evaluation.py::TestRetrievalTesting -v

# Example scenarios
pytest tests/test_phase12_evaluation.py::TestExampleScenarios -v

# Edge cases
pytest tests/test_phase12_evaluation.py::TestEdgeCases -v

# Performance tests
pytest tests/test_phase12_evaluation.py::TestPerformanceReliability -v
```

## Expected Test Results

### Passing Tests Indicate
✅ Backend reliability - API endpoints respond correctly
✅ Frontend integration - Response schema is correct
✅ Conversation quality - Intents are classified properly
✅ Retrieval accuracy - Recommendations match user intent
✅ User experience - Conversational flow works end-to-end

### Sample Output
```
tests/test_phase12_evaluation.py::TestFunctionalTesting::test_health_endpoint PASSED
tests/test_phase12_evaluation.py::TestFunctionalTesting::test_chat_endpoint_exists PASSED
tests/test_phase12_evaluation.py::TestFunctionalTesting::test_chat_request_schema_valid PASSED
tests/test_phase12_evaluation.py::TestConversationTesting::test_greeting_handling PASSED
tests/test_phase12_evaluation.py::TestConversationTesting::test_vague_query_clarification PASSED
tests/test_phase12_evaluation.py::TestRetrievalTesting::test_semantic_relevance_java PASSED
tests/test_phase12_evaluation.py::TestExampleScenarios::test_scenario_1_vague_query PASSED
```

## Test Coverage Goals

| Category | Coverage Target | Current Status |
|----------|-----------------|-----------------|
| Functional | 95%+ | ✅ Comprehensive |
| Conversation | 90%+ | ✅ All scenarios |
| Retrieval | 90%+ | ✅ Multiple criteria |
| Edge Cases | 85%+ | ✅ Included |
| Performance | 80%+ | ✅ Baseline tests |

## Debugging Failed Tests

### Test Fails With 422 Status
- Check request schema matches `ChatRequest` model
- Verify all required fields are present
- Ensure field names match exactly

### Test Fails With Assertion About SHL URL
- Check that retrieved assessments have valid `shl.com` URLs
- Verify metadata is properly loaded from FAISS index
- Check that retrieval service isn't hallucinating URLs

### Test Fails With Timeout
- Increase test timeout in pytest configuration
- Check if FAISS index is properly loaded
- Verify LLM API is responding

### Test Fails With Empty Recommendations
- Check retrieval threshold settings
- Verify FAISS index contains assessments
- Check that semantic search is working

## Continuous Integration

To run tests in CI/CD pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v --tb=short

# Generate coverage report
pytest tests/ --cov=app --cov-report=xml
```

## Fixtures Available

### `test_messages`
Sample test messages for various scenarios:
- Vague query
- Technical role
- Lookup query
- Off-topic request

### `sample_chat_payload`
Basic chat payload for single-turn testing

### `conversation_flow`
Multi-turn conversation example

Usage:
```python
def test_example(sample_chat_payload):
    response = client.post("/chat", json=sample_chat_payload)
    assert response.status_code == 200
```

## Test Maintenance

### When Adding New Features
1. Add corresponding test to relevant test class
2. Update test docstrings
3. Run full test suite to ensure no regressions
4. Update this guide if test structure changes

### Regular Updates
- Review test failures weekly
- Update expected responses if LLM behavior changes
- Add new test scenarios based on user feedback
- Maintain >85% code coverage

## Performance Baseline

Expected test execution times:
- Functional Tests: 5-10 seconds
- Conversation Tests: 10-15 seconds
- Retrieval Tests: 10-15 seconds
- Example Scenarios: 10-15 seconds
- Edge Cases: 5-10 seconds
- Performance Tests: 10-20 seconds

**Total: ~60-85 seconds for full test suite**

If tests exceed 2 minutes total, investigate performance bottlenecks.

## Troubleshooting

### FAISS Index Not Found
```
FileNotFoundError: app/data/faiss_index/shl_index.faiss
```
**Solution**: Run Phase 4 (embeddings generation) first

### LLM API Error
```
groq.error.APIError: API request failed
```
**Solution**: Verify GROQ_API_KEY is set in .env

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Kill existing FastAPI process or use different port

## Next Steps

After Phase 12 testing completes successfully:
1. → Phase 13: Deployment
2. → Phase 14: Documentation
3. → Production release

---

**Last Updated**: May 2026
**Test Framework**: Pytest
**Coverage Tool**: pytest-cov
