#!/bin/bash

# Genymotion Device Provisioning Script
# Creates and configures Android emulators for AndroidWorld testing

set -e

# Configuration
GENYMOTION_API_URL="https://cloud.geny.io/api/v1"
DEVICE_TEMPLATE="Google Pixel 2 - 8.0 - API 26 - 1080x1920"
DEVICE_NAME="androidworld-test-$(date +%s)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Genymotion Device Provisioning${NC}"

# Check for required environment variables
if [ -z "$GENYMOTION_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GENYMOTION_API_KEY not set${NC}"
    echo "Please set your Genymotion API key:"
    echo "export GENYMOTION_API_KEY='your-api-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "GENYMOTION_API_KEY=your-api-key-here"
    exit 1
fi

# Function to create device
create_device() {
    echo -e "${GREEN}📱 Creating device: $DEVICE_NAME${NC}"
    
    # Create device using Genymotion API
    response=$(curl -s -X POST "$GENYMOTION_API_URL/devices" \
        -H "Authorization: Bearer $GENYMOTION_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$DEVICE_NAME\",
            \"template\": \"$DEVICE_TEMPLATE\",
            \"region\": \"us-east-1\"
        }")
    
    if [ $? -eq 0 ]; then
        device_id=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$device_id" ]; then
            echo -e "${GREEN}✅ Device created with ID: $device_id${NC}"
            echo "$device_id" > .device_id
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Failed to create device${NC}"
    echo "Response: $response"
    return 1
}

# Function to wait for device to be ready
wait_for_device() {
    local device_id=$1
    local max_wait=300  # 5 minutes
    local wait_time=0
    
    echo -e "${YELLOW}⏳ Waiting for device to be ready...${NC}"
    
    while [ $wait_time -lt $max_wait ]; do
        status=$(curl -s -X GET "$GENYMOTION_API_URL/devices/$device_id" \
            -H "Authorization: Bearer $GENYMOTION_API_KEY" \
            | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✅ Device is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Device status: $status (${wait_time}s)${NC}"
        sleep 10
        wait_time=$((wait_time + 10))
    done
    
    echo -e "${RED}❌ Device did not become ready within $max_wait seconds${NC}"
    return 1
}

# Function to get device connection info
get_connection_info() {
    local device_id=$1
    
    echo -e "${GREEN}🔌 Getting connection information...${NC}"
    
    response=$(curl -s -X GET "$GENYMOTION_API_URL/devices/$device_id" \
        -H "Authorization: Bearer $GENYMOTION_API_KEY")
    
    if [ $? -eq 0 ]; then
        adb_port=$(echo "$response" | grep -o '"adb_port":[0-9]*' | cut -d':' -f2)
        ip_address=$(echo "$response" | grep -o '"ip_address":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$adb_port" ] && [ -n "$ip_address" ]; then
            echo -e "${GREEN}✅ Connection info:${NC}"
            echo "  IP: $ip_address"
            echo "  ADB Port: $adb_port"
            echo ""
            echo "To connect via ADB:"
            echo "adb connect $ip_address:$adb_port"
            echo ""
            echo "Connection info saved to .connection_info"
            echo "IP_ADDRESS=$ip_address" > .connection_info
            echo "ADB_PORT=$adb_port" >> .connection_info
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Failed to get connection information${NC}"
    return 1
}

# Function to connect via ADB
connect_adb() {
    if [ -f .connection_info ]; then
        source .connection_info
        
        echo -e "${GREEN}🔌 Connecting via ADB...${NC}"
        
        # Check if ADB is available
        if ! command -v adb &> /dev/null; then
            echo -e "${YELLOW}⚠️  ADB not found. Please install Android SDK.${NC}"
            return 1
        fi
        
        # Connect to device
        adb connect "$IP_ADDRESS:$ADB_PORT"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ADB connection successful${NC}"
            adb devices
            return 0
        else
            echo -e "${RED}❌ ADB connection failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ No connection info available${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${GREEN}🚀 Starting device provisioning...${NC}"
    
    # Create device
    if create_device; then
        device_id=$(cat .device_id)
        
        # Wait for device to be ready
        if wait_for_device "$device_id"; then
            # Get connection info
            if get_connection_info "$device_id"; then
                # Connect via ADB
                connect_adb
                
                echo -e "${GREEN}🎉 Device provisioning completed successfully!${NC}"
                echo ""
                echo "Next steps:"
                echo "1. Run: ./run.sh"
                echo "2. Check device status: adb devices"
                echo "3. Run evaluation: ./agents/evaluate.sh --episodes 5"
                
                return 0
            fi
        fi
    fi
    
    echo -e "${RED}❌ Device provisioning failed${NC}"
    return 1
}

# Run main function
main "$@"
