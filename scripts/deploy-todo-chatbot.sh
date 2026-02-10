#!/bin/bash
# deploy-todo-chatbot.sh
# Script to deploy the Todo Chatbot application to Minikube using Helm

set -e  # Exit on any error

echo "🚀 Starting Todo Chatbot deployment..."

# Check if required tools are installed
command -v minikube >/dev/null 2>&1 || { echo >&2 "❌ minikube is not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo >&2 "❌ kubectl is not installed. Aborting."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo >&2 "❌ helm is not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo >&2 "❌ docker is not installed. Aborting."; exit 1; }

echo "✅ All required tools are installed"

# Start Minikube if not already running
echo "🔄 Checking Minikube status..."
if ! minikube status >/dev/null 2>&1; then
    echo "🐳 Starting Minikube..."
    minikube start
else
    echo "✅ Minikube is already running"
fi

# Enable registry addon
echo "📦 Enabling registry addon..."
minikube addons enable registry

# Build Docker images
echo "🔨 Building Docker images..."
cd ../backend
docker build -t todo-backend:latest .

cd ../frontend
docker build -t todo-frontend:latest .

# Load images into Minikube
echo "📥 Loading images into Minikube..."
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Navigate back to helm charts directory
cd ../helm-charts

# Install the Helm chart
echo "_chart Installing Todo Chatbot with Helm..."
helm uninstall todo-chatbot 2>/dev/null || true  # Remove previous installation if exists
helm install todo-chatbot ./todo-chatbot

echo "✅ Todo Chatbot deployed successfully!"
echo ""
echo "📋 To access the application:"
echo "   Frontend: Use 'minikube service todo-chatbot-frontend' to get the URL"
echo "   Backend:  Use 'minikube service todo-chatbot-backend' to get the URL"
echo ""
echo "🔧 To view logs: kubectl logs -l app.kubernetes.io/component=frontend"
echo "🔧 To view backend logs: kubectl logs -l app.kubernetes.io/component=backend"