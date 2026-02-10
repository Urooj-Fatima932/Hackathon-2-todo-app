# Installation Guide for Todo Chatbot Deployment

## Installing Required Tools on Windows

### 1. Install Chocolatey (Package Manager)
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2. Install Docker Desktop
```powershell
choco install docker-desktop
```
After installation:
- Restart your computer
- Launch Docker Desktop
- Go to Settings > Features in development > Enable "Docker AI (Gordon)" (Beta feature)

### 3. Install Minikube
```powershell
choco install minikube
```

### 4. Install kubectl
```powershell
choco install kubernetes-cli
```

### 5. Install Helm
```powershell
choco install kubernetes-helm
```

### 6. Install kubectl-ai plugin (if available)
```bash
# Check if kubectl-ai is available
kubectl ai --help
```

If not available, you can install it following the official documentation.

### 7. Verify installations
```bash
docker --version
minikube version
kubectl version --client
helm version
docker ai "What can you do?"
```

## Alternative Installation Methods

### Using winget (Windows Package Manager):
```powershell
winget install Docker.DockerDesktop
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
winget install Helm.Helm
```

### Manual Installation:
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Minikube: https://minikube.sigs.k8s.io/docs/start/
- kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
- Helm: https://helm.sh/docs/intro/install/

## Post-Installation Steps

1. Start Minikube:
```bash
minikube start
```

2. Verify cluster status:
```bash
kubectl cluster-info
```

3. Check Docker AI capabilities:
```bash
docker ai "What can you do?"
```