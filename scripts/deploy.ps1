# Multiagent Demo Deployment Script for Windows PowerShell
# This script helps deploy the multiagent demo to Azure

param(
    [string]$SubscriptionId = "",
    [string]$TenantId = "",
    [string]$ClientId = "",
    [string]$ClientSecret = "",
    [string]$OpenAIEndpoint = "",
    [string]$AIFoundryEndpoint = "",
    [string]$CopilotEndpoint = ""
)

Write-Host "🚀 Starting Multiagent Demo Deployment" -ForegroundColor Green

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if Azure Developer CLI is installed
if (-not (Get-Command azd -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure Developer CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging in to Azure..." -ForegroundColor Blue
az login

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "📋 Setting subscription to: $SubscriptionId" -ForegroundColor Blue
    az account set --subscription $SubscriptionId
} else {
    $currentSubscription = az account show --query "id" -o tsv
    Write-Host "📋 Using current subscription: $currentSubscription" -ForegroundColor Blue
}

# Initialize azd environment
Write-Host "🏗️ Initializing Azure Developer CLI environment..." -ForegroundColor Blue
azd init --template multiagent-demo

# Collect configuration if not provided
if (-not $TenantId) {
    $TenantId = Read-Host "Azure Tenant ID"
}

if (-not $ClientId) {
    $ClientId = Read-Host "Azure Client ID"
}

if (-not $ClientSecret) {
    $ClientSecret = Read-Host "Azure Client Secret" -AsSecureString
    $ClientSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientSecret))
}

# Set azd environment variables
Write-Host "⚙️ Setting up environment variables..." -ForegroundColor Blue
azd env set AZURE_TENANT_ID $TenantId
azd env set AZURE_CLIENT_ID $ClientId
azd env set AZURE_CLIENT_SECRET $ClientSecret

# Optional endpoints
if (-not $OpenAIEndpoint) {
    $OpenAIEndpoint = Read-Host "Azure OpenAI Endpoint (optional, press Enter to skip)"
}

if (-not $AIFoundryEndpoint) {
    $AIFoundryEndpoint = Read-Host "AI Foundry Endpoint (optional, press Enter to skip)"
}

if (-not $CopilotEndpoint) {
    $CopilotEndpoint = Read-Host "Copilot Studio Endpoint (optional, press Enter to skip)"
}

if ($OpenAIEndpoint) {
    azd env set AZURE_OPENAI_ENDPOINT $OpenAIEndpoint
}

if ($AIFoundryEndpoint) {
    azd env set AZURE_AI_FOUNDRY_ENDPOINT $AIFoundryEndpoint
}

if ($CopilotEndpoint) {
    azd env set COPILOT_STUDIO_ENDPOINT $CopilotEndpoint
}

# Deploy to Azure
Write-Host "🚀 Deploying to Azure..." -ForegroundColor Green
azd up

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your multiagent demo is now running on Azure!" -ForegroundColor Cyan
Write-Host "📊 You can monitor the deployment in the Azure Portal" -ForegroundColor Cyan
Write-Host "🔗 Frontend URL: Check the azd output above" -ForegroundColor Cyan
Write-Host "🔗 Backend URL: Check the azd output above" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure Azure AD application permissions" -ForegroundColor White
Write-Host "2. Set up RBAC roles and permissions" -ForegroundColor White
Write-Host "3. Test the application with different user accounts" -ForegroundColor White
Write-Host "4. Monitor performance and usage in Application Insights" -ForegroundColor White

# Optional: Open Azure Portal
$openPortal = Read-Host "Would you like to open the Azure Portal? (y/N)"
if ($openPortal -eq 'y' -or $openPortal -eq 'Y') {
    Start-Process "https://portal.azure.com"
}
