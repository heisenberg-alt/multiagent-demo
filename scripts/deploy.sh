#!/bin/bash

# Multiagent Demo Deployment Script
# This script helps deploy the multiagent demo to Azure

set -e

echo "🚀 Starting Multiagent Demo Deployment"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if Azure Developer CLI is installed
if ! command -v azd &> /dev/null; then
    echo "❌ Azure Developer CLI is not installed. Please install it first."
    exit 1
fi

# Login to Azure
echo "🔐 Logging in to Azure..."
az login

# Set subscription (optional)
read -p "Enter your Azure subscription ID (or press Enter to use default): " subscription_id
if [ ! -z "$subscription_id" ]; then
    az account set --subscription "$subscription_id"
fi

# Initialize azd environment
echo "🏗️ Initializing Azure Developer CLI environment..."
azd init --template multiagent-demo

# Set environment variables
echo "⚙️ Setting up environment variables..."
echo "Please provide the following configuration values:"

read -p "Azure Tenant ID: " tenant_id
read -p "Azure Client ID: " client_id
read -s -p "Azure Client Secret: " client_secret
echo

# Set azd environment variables
azd env set AZURE_TENANT_ID "$tenant_id"
azd env set AZURE_CLIENT_ID "$client_id"
azd env set AZURE_CLIENT_SECRET "$client_secret"

# Optional: Set additional endpoints
read -p "Azure OpenAI Endpoint (optional): " openai_endpoint
read -p "AI Foundry Endpoint (optional): " ai_foundry_endpoint
read -p "Copilot Studio Endpoint (optional): " copilot_endpoint

if [ ! -z "$openai_endpoint" ]; then
    azd env set AZURE_OPENAI_ENDPOINT "$openai_endpoint"
fi

if [ ! -z "$ai_foundry_endpoint" ]; then
    azd env set AZURE_AI_FOUNDRY_ENDPOINT "$ai_foundry_endpoint"
fi

if [ ! -z "$copilot_endpoint" ]; then
    azd env set COPILOT_STUDIO_ENDPOINT "$copilot_endpoint"
fi

# Deploy to Azure
echo "🚀 Deploying to Azure..."
azd up

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your multiagent demo is now running on Azure!"
echo "📊 You can monitor the deployment in the Azure Portal"
echo "🔗 Frontend URL: Check the azd output above"
echo "🔗 Backend URL: Check the azd output above"
echo ""
echo "Next steps:"
echo "1. Configure Azure AD application permissions"
echo "2. Set up RBAC roles and permissions"
echo "3. Test the application with different user accounts"
echo "4. Monitor performance and usage in Application Insights"
