#!/usr/bin/env bash
#
# Run test suite for poker-agent
#
# Usage:
#   ./scripts/run_tests.sh           # Run all tests
#   ./scripts/run_tests.sh core      # Run only core tests
#   ./scripts/run_tests.sh -v        # Run with verbose output
#   ./scripts/run_tests.sh --cov     # Run with coverage report

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running poker-agent test suite${NC}"
echo "========================================"

# Default options
PYTEST_ARGS=""
TEST_PATH="tests/"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        core)
            TEST_PATH="tests/core/"
            echo -e "${YELLOW}Running core tests only${NC}"
            shift
            ;;
        tools)
            TEST_PATH="tests/tools/"
            echo -e "${YELLOW}Running tools tests only${NC}"
            shift
            ;;
        database)
            TEST_PATH="tests/database/"
            echo -e "${YELLOW}Running database tests only${NC}"
            shift
            ;;
        -v|--verbose)
            PYTEST_ARGS="$PYTEST_ARGS -v"
            shift
            ;;
        --cov|--coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=term-missing"
            echo -e "${YELLOW}Running with coverage report${NC}"
            shift
            ;;
        -k)
            PYTEST_ARGS="$PYTEST_ARGS -k $2"
            echo -e "${YELLOW}Running tests matching: $2${NC}"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./scripts/run_tests.sh [core|tools|database] [-v] [--cov] [-k pattern]"
            exit 1
            ;;
    esac
done

# Run pytest with uv
echo ""
uv run pytest $TEST_PATH $PYTEST_ARGS

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
fi

exit $EXIT_CODE
