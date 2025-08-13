#!/bin/bash
# kurbeScript.sh  - Start and verify local Kubernetes cluster

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Minikube is not installed."
    exit 1
fi

#Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed"
    exit 1
fi

echo "Starting Minikube..."
minikube start

echo "Verifying Kubernetes cluster status..."
kubectl cluster-info

echo "Listing pods in all namespaces..."
kubectl get pods --all-namespaces

echo "Done."
