# Todo Chatbot Deployment Guide

## Prerequisites

Before deploying the Todo Chatbot application, ensure you have the following tools installed:

1. Docker Desktop (with Docker AI enabled)
2. Minikube
3. kubectl
4. Helm

Follow the installation guide in `docs/installation-guide.md` if you haven't installed these tools yet.

## Building Docker Images

Before deploying with Helm, you need to build the Docker images for both frontend and backend applications:

### Backend Image
```bash
cd backend
docker build -t todo-backend:latest .
```

### Frontend Image
```bash
cd frontend
docker build -t todo-frontend:latest .
```

## Starting Minikube

Start your local Kubernetes cluster:

```bash
minikube start
```

Enable the Docker container registry in Minikube so it can access your locally built images:

```bash
minikube addons enable registry
```

Load your images into Minikube:

```bash
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

## Deploying with Helm

Navigate to the helm-charts directory:

```bash
cd helm-charts
```

Install the Todo Chatbot application:

```bash
helm install todo-chatbot ./todo-chatbot
```

To upgrade the deployment:

```bash
helm upgrade todo-chatbot ./todo-chatbot
```

To uninstall:

```bash
helm uninstall todo-chatbot
```

## Verifying the Deployment

Check if all pods are running:

```bash
kubectl get pods
```

Check the services:

```bash
kubectl get services
```

## Accessing the Application

To access the frontend application, you'll need to expose it. You can either:

### Option 1: Port Forwarding
```bash
kubectl port-forward svc/todo-chatbot-frontend 3000:3000
```

Then visit `http://localhost:3000` in your browser.

### Option 2: Using Minikube Tunnel (for LoadBalancer services)
```bash
minikube tunnel
```

## Using kubectl-ai and kagent

If you have kubectl-ai and kagent installed, you can use AI-assisted Kubernetes operations:

```bash
# Deploy with AI assistance
kubectl-ai "deploy the todo frontend with 2 replicas"

# Scale the backend
kubectl-ai "scale the backend to handle more load"

# Check pod status
kubectl-ai "check why the pods are failing"

# Analyze cluster health
kagent "analyze the cluster health"

# Optimize resource allocation
kagent "optimize resource allocation"
```

## Troubleshooting

If you encounter issues:

1. Check pod status:
   ```bash
   kubectl get pods
   ```

2. View pod logs:
   ```bash
   kubectl logs <pod-name>
   ```

3. Describe a pod for detailed information:
   ```bash
   kubectl describe pod <pod-name>
   ```

4. Check services:
   ```bash
   kubectl get services
   ```

5. Verify ingress (if configured):
   ```bash
   kubectl get ingress
   ```