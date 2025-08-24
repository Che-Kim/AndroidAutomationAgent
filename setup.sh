#!/bin/bash

# AndroidWorld Agent Challenge - Quick Setup Script
# This script helps reviewers quickly set up their environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AndroidWorld Agent Challenge - Quick Setup${NC}"
echo "=================================================="
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}✅ Setup cancelled. Using existing .env file.${NC}"
        exit 0
    fi
fi

# Copy env.example to .env
echo -e "${BLUE}📋 Creating .env file from template...${NC}"
cp env.example .env
echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo ""

# Check if Genymotion API key is set
if [ -z "$GENYMOTION_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GENYMOTION_API_KEY environment variable not set.${NC}"
    echo ""
    echo -e "${BLUE}📝 To get your Genymotion API key:${NC}"
    echo "   1. Go to: https://cloud.geny.io/account/api-keys"
    echo "   2. Create a new API key"
    echo "   3. Copy the key and set it in your .env file"
    echo ""
    echo -e "${BLUE}🔧 Quick setup options:${NC}"
    echo "   Option A: Edit .env file manually and set GENYMOTION_API_KEY"
    echo "   Option B: Export environment variable: export GENYMOTION_API_KEY='your-key'"
    echo "   Option C: Use mock key for local testing (edit .env file)"
    echo ""
    
    read -p "Do you want to edit the .env file now? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${BLUE}✅ Setup completed. Remember to set your API key before running!${NC}"
        exit 0
    fi
fi

# Offer to edit .env file
if command -v nano >/dev/null 2>&1; then
    echo -e "${BLUE}📝 Opening .env file in nano editor...${NC}"
    echo "   Update GENYMOTION_API_KEY with your actual key"
    echo "   Press Ctrl+X, then Y, then Enter to save"
    echo ""
    read -p "Press Enter to continue..."
    nano .env
elif command -v vim >/dev/null 2>&1; then
    echo -e "${BLUE}📝 Opening .env file in vim editor...${NC}"
    echo "   Update GENYMOTION_API_KEY with your actual key"
    echo "   Press ESC, then :wq, then Enter to save"
    echo ""
    read -p "Press Enter to continue..."
    vim .env
else
    echo -e "${YELLOW}⚠️  No text editor found. Please edit .env file manually.${NC}"
    echo "   Update GENYMOTION_API_KEY with your actual key"
fi

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "   1. Ensure Docker is running: docker --version"
echo "   2. Create Genymotion devices: ./infra/create_devices.sh"
echo "   3. Build and run: docker build -t candidate/android-world ."
echo "   4. Evaluate: ./agents/evaluate.sh --episodes 50"
echo ""
echo -e "${BLUE}📚 For more details, see README.md${NC}"
echo ""
echo -e "${GREEN}🎉 Happy testing!${NC}"
