# deploy-todo-chatbot.ps1
# PowerShell script to deploy the Todo Chatbot application to Minikube using Helm

Write-Host "🚀 Starting Todo Chatbot deployment..." -ForegroundColor Green

# Check if required tools are installed
$requiredTools = @("minikube", "kubectl", "helm", "docker")

foreach ($tool in $requiredTools) {
    try {
        Invoke-Expression "$tool version" | Out-Null
        Write-Host "✅ $tool is installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $tool is not installed. Aborting." -ForegroundColor Red
        exit 1
    }
}

# Start Minikube if not already running
Write-Host "🔄 Checking Minikube status..." -ForegroundColor Yellow
try {
    minikube status | Out-Null
    Write-Host "✅ Minikube is already running" -ForegroundColor Green
}
catch {
    Write-Host "🐳 Starting Minikube..." -ForegroundColor Yellow
    minikube start
}

# Enable registry addon
Write-Host "📦 Enabling registry addon..." -ForegroundColor Yellow
minikube addons enable registry

# Build Docker images
Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow

# Change to backend directory and build
Set-Location "../backend"
docker build -t todo-backend:latest .

# Change to frontend directory and build
Set-Location "../frontend"
docker build -t todo-frontend:latest .

# Load images into Minikube
Write-Host "📥 Loading images into Minikube..." -ForegroundColor Yellow
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Navigate back to helm charts directory
Set-Location "../helm-charts"

# Install the Helm chart
Write-Host "🚢 Installing Todo Chatbot with Helm..." -ForegroundColor Yellow
helm uninstall todo-chatbot 2>$null  # Remove previous installation if exists
helm install todo-chatbot ./todo-chatbot

Write-Host "✅ Todo Chatbot deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 To access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: Use 'minikube service todo-chatbot-frontend' to get the URL" -ForegroundColor Cyan
Write-Host "   Backend:  Use 'minikube service todo-chatbot-backend' to get the URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 To view logs:" -ForegroundColor Cyan
Write-Host "   Frontend: kubectl logs -l app.kubernetes.io/component=frontend" -ForegroundColor Cyan
Write-Host "   Backend:  kubectl logs -l app.kubernetes.io/component=backend" -ForegroundColor Cyan