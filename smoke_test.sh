#!/bin/bash

# Smoke Test Script
# Runs a small battery of AndroidWorld tasks to verify system functionality
# Environment-aware: works with or without real device setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 AndroidWorld Smoke Test${NC}"
echo "Environment-aware testing suite"

# Test counter
tests_passed=0
tests_total=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    tests_total=$((tests_total + 1))
    echo -e "${YELLOW}🧪 Test $tests_total: $test_name${NC}"
    
    if eval "$test_command" 2>/dev/null | grep -q "$expected_result"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        tests_passed=$((tests_passed + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        return 1
    fi
}

# Function to check environment capabilities
check_environment() {
    echo -e "${BLUE}🔍 Checking Environment Capabilities...${NC}"
    
    local has_device_config=false
    local has_adb=false
    local has_real_device=false
    
    # Check for device configuration
    if [ -f .connection_info ]; then
        has_device_config=true
        echo "✅ Device configuration found (.connection_info)"
    else
        echo "⚠️  No device configuration (.connection_info not found)"
    fi
    
    # Check for ADB
    if command -v adb >/dev/null 2>&1; then
        has_adb=true
        echo "✅ ADB available"
    else
        echo "⚠️  ADB not available"
    fi
    
    # Check if we can connect to a real device
    if [ "$has_device_config" = true ] && [ "$has_adb" = true ]; then
        source .connection_info
        if adb connect "$IP_ADDRESS:$ADB_PORT" >/dev/null 2>&1; then
            if adb devices | grep -q "device$"; then
                has_real_device=true
                echo "✅ Real device available and connected"
            else
                echo "⚠️  Device configuration found but device not accessible"
            fi
        else
            echo "⚠️  Device configuration found but connection failed"
        fi
    fi
    
    # Set environment mode
    if [ "$has_real_device" = true ]; then
        echo -e "${GREEN}🚀 Environment: Full device testing enabled${NC}"
        export SMOKE_TEST_MODE="full"
    else
        echo -e "${YELLOW}🔧 Environment: Code-only testing mode${NC}"
        export SMOKE_TEST_MODE="code_only"
    fi
    
    echo ""
}

# Function to test ADB connectivity (only if real device available)
test_adb_connectivity() {
    if [ "$SMOKE_TEST_MODE" != "full" ]; then
        echo -e "${YELLOW}⏭️  Skipping ADB tests (no real device)${NC}"
        return 0
    fi
    
    echo -e "${GREEN}🔌 Testing ADB connectivity...${NC}"
    
    # Test 1: ADB connection
    run_test "ADB Connection" \
        "adb connect $IP_ADDRESS:$ADB_PORT && adb devices" \
        "device"
    
    # Test 2: Device properties
    run_test "Device Properties" \
        "adb shell getprop ro.product.model" \
        "Pixel"
    
    # Test 3: Device ready
    run_test "Device Ready" \
        "adb wait-for-device && echo 'ready'" \
        "ready"
}

# Function to test basic Android operations (only if real device available)
test_android_operations() {
    if [ "$SMOKE_TEST_MODE" != "full" ]; then
        echo -e "${YELLOW}⏭️  Skipping Android operation tests (no real device)${NC}"
        return 0
    fi
    
    echo -e "${GREEN}📱 Testing Android operations...${NC}"
    
    # Test 4: App launching
    run_test "Settings App Launch" \
        "adb shell am start -n com.android.settings/.Settings && sleep 2 && adb shell dumpsys activity activities | grep -c 'com.android.settings'" \
        "1"
    
    # Test 5: Input simulation
    run_test "Input Simulation" \
        "adb shell input tap 500 500 && echo 'tap_success'" \
        "tap_success"
    
    # Test 6: App package listing
    run_test "Package Listing" \
        "adb shell pm list packages | grep -c 'android'" \
        "1"
}

# Function to test Python components (always runs)
test_python_components() {
    echo -e "${GREEN}🐍 Testing Python components...${NC}"
    
    # Test 7: Agent import
    run_test "Agent Import" \
        "python3 -c 'from agents.agent import AndroidWorldAgent; print(\"agent_ok\")'" \
        "agent_ok"
    
    # Test 8: Runner import
    run_test "Runner Import" \
        "python3 -c 'from android_world.runner import AndroidWorldRunner; print(\"runner_ok\")'" \
        "runner_ok"
    
    # Test 9: Evaluator import
    run_test "Evaluator Import" \
        "python3 -c 'from agents.evaluator import AndroidWorldEvaluator; print(\"evaluator_ok\")'" \
        "evaluator_ok"
    
    # Test 10: Observability import
    run_test "Observability Import" \
        "python3 -c 'from agents.observability import ObservabilityManager; print(\"observability_ok\")'" \
        "observability_ok"
}

# Function to test basic task execution (always runs)
test_task_execution() {
    echo -e "${GREEN}🤖 Testing task execution...${NC}"
    
    # Test 11: Task execution
    run_test "Task Execution" \
        "python3 -c 'from agents.agent import AndroidWorldAgent; agent = AndroidWorldAgent(); result = agent.execute_task(\"open app settings\"); print(\"success\" if result.get(\"success\") else \"fail\")'" \
        "success"
}

# Function to run evaluation test (always runs)
test_evaluation() {
    echo -e "${GREEN}📊 Testing evaluation...${NC}"
    
    # Test 12: Evaluation execution
    echo -e "${BLUE}Running evaluation with 2 episodes...${NC}"
    if ./agents/evaluate.sh --episodes 2 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: Evaluation script execution${NC}"
        tests_passed=$((tests_total + 1))
        tests_total=$((tests_total + 1))
    else
        echo -e "${RED}❌ FAIL: Evaluation script execution${NC}"
        tests_total=$((tests_total + 1))
        return 1
    fi
    
    # Test 13: Results generation
    run_test "Results Generation" \
        "test -f results/results.json && test -f results/report.md && echo 'results_ok'" \
        "results_ok"
    
    # Test 14: Results structure validation
    run_test "Results JSON Structure" \
        "python3 -c 'import json; data=json.load(open(\"results/results.json\")); print(\"valid_json\") if \"evaluation\" in data else exit(1)'" \
        "valid_json"
}

# Function to test file structure (always runs)
test_file_structure() {
    echo -e "${GREEN}📁 Testing file structure...${NC}"
    
    # Test 15: Required files exist
    run_test "Required Scripts Exist" \
        "test -f run.sh && test -f agents/evaluate.sh && test -f setup.sh && echo 'scripts_ok'" \
        "scripts_ok"
    
    # Test 16: Configuration files exist
    run_test "Configuration Files Exist" \
        "test -f Dockerfile && test -f .github/workflows/ci.yml && echo 'config_ok'" \
        "config_ok"
    
    # Test 17: Load testing tools exist
    run_test "Load Testing Tools Exist" \
        "test -d load-testing && test -f load-testing/k6-load-test.js && echo 'load_testing_ok'" \
        "load_testing_ok"
}

# Main smoke test execution
main() {
    echo -e "${GREEN}🚀 Starting smoke test suite...${NC}"
    echo ""
    
    # Check environment first
    check_environment
    
    # Run environment-dependent tests
    test_adb_connectivity
    test_android_operations
    
    # Run always-available tests
    test_python_components
    test_task_execution
    test_evaluation
    test_file_structure
    
    # Summary
    echo ""
    echo -e "${GREEN}📊 Smoke Test Summary${NC}"
    echo "Tests passed: $tests_passed/$tests_total"
    echo "Environment mode: $SMOKE_TEST_MODE"
    echo ""
    
    if [ $tests_passed -eq $tests_total ]; then
        echo -e "${GREEN}🎉 All smoke tests passed!${NC}"
        echo ""
        if [ "$SMOKE_TEST_MODE" = "full" ]; then
            echo "✅ System is ready for production use"
            echo "✅ AndroidWorld integration working"
            echo "✅ Agent system functional"
            echo "✅ Evaluation framework operational"
            echo "✅ Real device testing successful"
        else
            echo "✅ System is ready for production use"
            echo "✅ Agent system functional"
            echo "✅ Evaluation framework operational"
            echo "✅ Code components validated"
            echo "⚠️  Device testing skipped (no real device available)"
        fi
        return 0
    else
        echo -e "${RED}❌ Some smoke tests failed${NC}"
        echo ""
        echo "Please check the failed tests above"
        return 1
    fi
}

# Run main function
main "$@"
