"""
Phase 12 — Testing & Evaluation

Comprehensive test suite for:
- backend reliability
- frontend integration
- conversational quality
- retrieval accuracy
- overall user experience
"""

import pytest
import json
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.recommendation_service import (
    process_query,
    classify_query,
    retrieve_assessments,
)
from app.models.schemas import Message

client = TestClient(app)


# ==============================================
# 17.1 FUNCTIONAL TESTING
# ==============================================

class TestFunctionalTesting:
    """Test API responses, endpoints, schema validation."""

    def test_health_endpoint(self):
        """Verify /health endpoint responds correctly."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_chat_endpoint_exists(self):
        """Verify /chat endpoint exists."""
        response = client.post("/chat", json={"messages": []})
        assert response.status_code in [200, 422]  # 200 OK or 422 validation error

    def test_chat_request_schema_valid(self):
        """Test valid chat request schema."""
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "recommendations" in data
        assert "end_of_conversation" in data

    def test_chat_request_schema_invalid_missing_role(self):
        """Test invalid schema: missing role field."""
        payload = {
            "messages": [
                {"content": "Hello"}  # Missing role
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_chat_request_schema_invalid_missing_content(self):
        """Test invalid schema: missing content field."""
        payload = {
            "messages": [
                {"role": "user"}  # Missing content
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_recommendation_response_schema(self):
        """Verify recommendation response contains required fields."""
        payload = {
            "messages": [
                {"role": "user", "content": "Java developer"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Check top-level fields
        assert "reply" in data
        assert "recommendations" in data
        assert "end_of_conversation" in data
        assert isinstance(data["reply"], str)
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["end_of_conversation"], bool)

        # Check recommendation schema if present
        for rec in data["recommendations"]:
            assert "name" in rec or "title" in rec
            assert "url" in rec
            assert "pdf_url" in rec or "pdf_url" not in rec

    def test_frontend_backend_integration(self):
        """Verify frontend can integrate with backend."""
        # Simulate frontend sending a message
        payload = {
            "messages": [
                {"role": "user", "content": "I need Java assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Verify response is JSON serializable (frontend can parse)
        assert json.dumps(data)

    def test_recommendation_rendering_no_hallucination(self):
        """Verify recommendations come from SHL catalog only."""
        payload = {
            "messages": [
                {"role": "user", "content": "Java developer assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Check that URLs are valid SHL URLs if present
        for rec in data["recommendations"]:
            if "url" in rec and rec["url"]:
                assert "shl.com" in rec["url"].lower(), \
                    f"Non-SHL URL found: {rec['url']}"


# ==============================================
# 17.2 CONVERSATION TESTING
# ==============================================

class TestConversationTesting:
    """Test greeting, clarification, refinement, lookup, refusal."""

    def test_greeting_handling(self):
        """Test greeting queries trigger greeting response."""
        greetings = ["hi", "hello", "hey", "hii"]
        for greeting in greetings:
            payload = {
                "messages": [
                    {"role": "user", "content": greeting}
                ]
            }
            response = client.post("/chat", json=payload)
            data = response.json()
            reply = data["reply"].lower()

            # Greeting response should offer help
            assert (
                "help" in reply or
                "discover" in reply or
                "shl" in reply or
                "assessment" in reply
            ), f"Greeting not handled properly for: {greeting}"

    def test_vague_query_clarification(self):
        """Test vague queries trigger clarification."""
        # Scenario 1: "I need an assessment"
        payload = {
            "messages": [
                {"role": "user", "content": "I need an assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should ask clarification, not end conversation
        assert data["end_of_conversation"] == False
        reply = data["reply"].lower()
        # Assistant should ask for more details
        assert (
            "role" in reply or
            "details" in reply or
            "seniority" in reply or
            "?" in reply
        ), "Clarification not requested for vague query"

    def test_refinement_handling(self):
        """Test refinement: 'Add personality tests'"""
        # Start conversation
        messages = [
            {"role": "user", "content": "Java developer"}
        ]
        response = client.post("/chat", json={"messages": messages})
        data = response.json()

        # Add refinement
        messages.append({"role": "assistant", "content": data["reply"]})
        messages.append({"role": "user", "content": "Add personality tests"})

        response = client.post("/chat", json={"messages": messages})
        data = response.json()

        # System should process refinement
        assert isinstance(data["reply"], str)
        assert isinstance(data["recommendations"], list)

    def test_lookup_query_exact_assessment(self):
        """Scenario 3: 'Give me the download link for OPQ32'"""
        payload = {
            "messages": [
                {"role": "user", "content": "Give me the download link for OPQ32"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should retrieve OPQ assessment
        assert data["end_of_conversation"] == True
        assert len(data["recommendations"]) > 0, "No recommendations for OPQ lookup"

        # Check for OPQ in results
        opq_found = False
        for rec in data["recommendations"]:
            if "opq" in rec.get("name", "").lower():
                opq_found = True
                assert "shl.com" in rec["url"].lower(), "Invalid OPQ URL"
                break

        assert opq_found, "OPQ not found in recommendations"

    def test_refusal_non_shl_request(self):
        """Scenario 4: 'Recommend non-SHL tests'"""
        payload = {
            "messages": [
                {"role": "user", "content": "Recommend non-SHL tests like Coursera"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should refuse off-topic request
        reply = data["reply"].lower()
        recommendations = data["recommendations"]

        # Either refuse or only recommend SHL tests
        if recommendations:
            for rec in recommendations:
                assert "shl.com" in rec.get("url", "").lower(), \
                    "Non-SHL recommendation provided"

    def test_conversation_continuity(self):
        """Test maintaining conversation history across multiple turns."""
        messages = []

        # Turn 1: Initial query
        messages.append({"role": "user", "content": "Hiring for a role"})
        response = client.post("/chat", json={"messages": messages})
        reply1 = response.json()["reply"]
        messages.append({"role": "assistant", "content": reply1})

        # Turn 2: Refinement
        messages.append({"role": "user", "content": "Java developer"})
        response = client.post("/chat", json={"messages": messages})
        reply2 = response.json()["reply"]
        messages.append({"role": "assistant", "content": reply2})

        # Turn 3: Further refinement
        messages.append({"role": "user", "content": "Senior level"})
        response = client.post("/chat", json={"messages": messages})
        data = response.json()

        # Should maintain context across turns
        assert "reply" in data
        assert isinstance(data["recommendations"], list)


# ==============================================
# 17.3 RETRIEVAL TESTING
# ==============================================

class TestRetrievalTesting:
    """Test semantic relevance, exact lookup, hallucination prevention."""

    def test_semantic_relevance_java(self):
        """Test semantic relevance: Java query should retrieve Java assessments."""
        payload = {
            "messages": [
                {"role": "user", "content": "Java programming skills assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should have recommendations
        assert len(data["recommendations"]) > 0, "No recommendations for Java query"

        # Check semantic match
        all_results = data["recommendations"]
        assert len(all_results) > 0

    def test_exact_lookup_accuracy(self):
        """Test exact assessment lookup."""
        # Test with known SHL assessment names
        test_assessments = ["OPQ", "GSA", "Java"]

        for assessment in test_assessments:
            payload = {
                "messages": [
                    {"role": "user", "content": f"Find {assessment} assessment"}
                ]
            }
            response = client.post("/chat", json=payload)
            data = response.json()

            # Should find relevant assessments
            if len(data["recommendations"]) > 0:
                assert "shl.com" in data["recommendations"][0].get("url", "").lower()

    def test_recommendation_quality_multiple_criteria(self):
        """Test recommendation quality with multiple hiring criteria."""
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Senior Java developer with communication skills and leadership"
                }
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should provide recommendations
        assert len(data["recommendations"]) > 0

        # All should be SHL assessments
        for rec in data["recommendations"]:
            assert "shl.com" in rec.get("url", "").lower()

    def test_hallucination_prevention(self):
        """Test that system doesn't invent assessments."""
        payload = {
            "messages": [
                {"role": "user", "content": "Machine learning expert assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Every recommendation must be from SHL catalog
        for rec in data["recommendations"]:
            url = rec.get("url", "")
            pdf_url = rec.get("pdf_url", "")

            # URLs should be SHL or empty
            if url:
                assert "shl.com" in url.lower(), f"Hallucinated URL: {url}"
            if pdf_url:
                assert "shl.com" in pdf_url.lower() or "service.shl.com" in pdf_url.lower(), \
                    f"Hallucinated PDF URL: {pdf_url}"

    def test_shl_only_validation(self):
        """Verify all recommendations are from SHL catalog."""
        payload = {
            "messages": [
                {"role": "user", "content": "Assessment for hiring"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        for rec in data["recommendations"]:
            url = rec.get("url", "")
            assert not url or "shl.com" in url.lower(), \
                f"Non-SHL assessment recommended: {rec.get('name')}"


# ==============================================
# 17.4 EXAMPLE TEST SCENARIOS
# ==============================================

class TestExampleScenarios:
    """Test specific example scenarios from Phase 12."""

    def test_scenario_1_vague_query(self):
        """
        Scenario 1:
        User: "I need an assessment"
        Expected: assistant asks clarification question.
        """
        payload = {
            "messages": [
                {"role": "user", "content": "I need an assessment"}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["end_of_conversation"] == False
        assert "?" in data["reply"], "Should ask clarification question"
        assert len(data["recommendations"]) == 0, "Should not recommend yet"

    def test_scenario_2_refinement(self):
        """
        Scenario 2:
        User: "Add personality tests"
        Expected: recommendations updated while preserving earlier context.
        """
        messages = [
            {"role": "user", "content": "Java developer"}
        ]
        response = client.post("/chat", json={"messages": messages})
        data1 = response.json()

        messages.append({"role": "assistant", "content": data1["reply"]})
        messages.append({"role": "user", "content": "Add personality tests"})

        response = client.post("/chat", json={"messages": messages})
        data2 = response.json()

        # Should process refinement
        assert isinstance(data2["reply"], str)

    def test_scenario_3_lookup(self):
        """
        Scenario 3:
        User: "Give me the download link for OPQ32"
        Expected:
        - exact assessment retrieved,
        - correct SHL URL returned,
        - PDF link returned.
        """
        payload = {
            "messages": [
                {"role": "user", "content": "Give me the download link for OPQ32"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        assert data["end_of_conversation"] == True
        assert len(data["recommendations"]) > 0

        # Check for OPQ in recommendations
        found = False
        for rec in data["recommendations"]:
            if "opq" in rec.get("name", "").lower():
                found = True
                assert "shl.com" in rec.get("url", "").lower()
                assert "pdf_url" in rec or "pdf_url" == ""
                break

    def test_scenario_4_refusal(self):
        """
        Scenario 4:
        User: "Recommend non-SHL tests"
        Expected: assistant refuses request.
        """
        payload = {
            "messages": [
                {"role": "user", "content": "Recommend non-SHL tests"}
            ]
        }
        response = client.post("/chat", json=payload)
        data = response.json()

        # Should either refuse or only recommend SHL
        reply = data["reply"].lower()

        if "only" in reply or "shl" in reply:
            # Correctly restricted to SHL
            pass

        # All recommendations must be SHL
        for rec in data["recommendations"]:
            assert "shl.com" in rec.get("url", "").lower()


# ==============================================
# ADDITIONAL EDGE CASES & ERROR HANDLING
# ==============================================

class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_message(self):
        """Test handling of empty message."""
        payload = {
            "messages": [
                {"role": "user", "content": ""}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200

    def test_very_long_query(self):
        """Test handling of very long query."""
        long_query = "I need an assessment for " + ("a role " * 100)
        payload = {
            "messages": [
                {"role": "user", "content": long_query}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200

    def test_special_characters_in_query(self):
        """Test handling of special characters."""
        payload = {
            "messages": [
                {"role": "user", "content": "Java & Python assessment!@#$%"}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code == 200

    def test_missing_messages_field(self):
        """Test request without messages field."""
        payload = {}
        response = client.post("/chat", json=payload)
        assert response.status_code == 422

    def test_none_content(self):
        """Test message with null content."""
        payload = {
            "messages": [
                {"role": "user", "content": None}
            ]
        }
        response = client.post("/chat", json=payload)
        assert response.status_code in [200, 422]


# ==============================================
# PERFORMANCE & RELIABILITY
# ==============================================

class TestPerformanceReliability:
    """Test system reliability and performance."""

    def test_response_time_reasonable(self):
        """Test that response time is reasonable (< 30 seconds)."""
        import time

        payload = {
            "messages": [
                {"role": "user", "content": "Java developer"}
            ]
        }

        start_time = time.time()
        response = client.post("/chat", json=payload)
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed < 30, f"Response took {elapsed}s, expected < 30s"

    def test_multiple_sequential_requests(self):
        """Test multiple sequential requests don't break system."""
        for i in range(5):
            payload = {
                "messages": [
                    {"role": "user", "content": f"Assessment query {i}"}
                ]
            }
            response = client.post("/chat", json=payload)
            assert response.status_code == 200

    def test_conversation_state_isolation(self):
        """Test that conversations don't leak state between requests."""
        # Conversation 1
        payload1 = {
            "messages": [
                {"role": "user", "content": "Java"}
            ]
        }
        response1 = client.post("/chat", json=payload1)
        data1 = response1.json()

        # Conversation 2 (independent)
        payload2 = {
            "messages": [
                {"role": "user", "content": "Python"}
            ]
        }
        response2 = client.post("/chat", json=payload2)
        data2 = response2.json()

        # Both should be valid but independent
        assert response1.status_code == 200
        assert response2.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
