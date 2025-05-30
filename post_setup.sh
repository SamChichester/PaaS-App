#!/bin/bash

set -e

echo "[INFO] Adding Helm repos..."
helm repo add traefik https://helm.traefik.io/traefik
helm repo add jetstack https://charts.jetstack.io
helm repo update

echo "[INFO] Installing Traefik Ingress Controller..."
helm upgrade --install traefik traefik/traefik \
  --namespace traefik --create-namespace

echo "[INFO] Installing cert-manager..."
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

echo "[INFO] Applying ClusterIssuer..."
kubectl apply -f ./cert-manager/cluster-issuer.yaml
