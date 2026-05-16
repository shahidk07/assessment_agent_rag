#!/bin/bash
# Phase 12 Test Runner Script
# Usage: ./run_tests.sh [all|functional|conversation|retrieval|scenarios|edge|performance|coverage]

set -e

TESTS_DIR="tests"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Default to all tests if no argument provided
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    all)
        print_header "Running All Tests"
        pytest "$TESTS_DIR" -v
        print_success "All tests completed"
        ;;
    
    functional)
        print_header "Running Functional Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestFunctionalTesting" -v
        print_success "Functional tests completed"
        ;;
    
    conversation)
        print_header "Running Conversation Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestConversationTesting" -v
        print_success "Conversation tests completed"
        ;;
    
    retrieval)
        print_header "Running Retrieval Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestRetrievalTesting" -v
        print_success "Retrieval tests completed"
        ;;
    
    scenarios)
        print_header "Running Example Scenarios"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestExampleScenarios" -v
        print_success "Example scenarios completed"
        ;;
    
    edge)
        print_header "Running Edge Case Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestEdgeCases" -v
        print_success "Edge case tests completed"
        ;;
    
    performance)
        print_header "Running Performance Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestPerformanceReliability" -v
        print_success "Performance tests completed"
        ;;
    
    coverage)
        print_header "Running Tests with Coverage Report"
        pytest "$TESTS_DIR" \
            --cov=app \
            --cov-report=html \
            --cov-report=term-missing \
            -v
        print_success "Coverage report generated in htmlcov/index.html"
        ;;
    
    quick)
        print_header "Running Quick Smoke Tests"
        pytest "$TESTS_DIR/test_phase12_evaluation.py::TestFunctionalTesting::test_health_endpoint" \
                "$TESTS_DIR/test_phase12_evaluation.py::TestExampleScenarios::test_scenario_1_vague_query" \
                -v
        print_success "Quick smoke tests passed"
        ;;
    
    *)
        print_info "Phase 12 Test Runner"
        echo ""
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all           - Run all tests (default)"
        echo "  functional    - Run functional tests only"
        echo "  conversation  - Run conversation tests only"
        echo "  retrieval     - Run retrieval tests only"
        echo "  scenarios     - Run example scenario tests only"
        echo "  edge          - Run edge case tests only"
        echo "  performance   - Run performance tests only"
        echo "  coverage      - Run all tests with coverage report"
        echo "  quick         - Run quick smoke tests"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                # Run all tests"
        echo "  ./run_tests.sh functional     # Run functional tests only"
        echo "  ./run_tests.sh coverage       # Run with coverage"
        echo ""
        exit 1
        ;;
esac

echo ""
print_success "Test run completed"
