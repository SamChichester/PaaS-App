#!/bin/bash

set -e

echo "[INFO] Adding Helm repos..."
helm repo add traefik https://helm.traefik.io/traefik
helm repo add jetstack https://charts.jetstack.io
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
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

echo "[INFO] Installing Prometheus + Grafana (kube-prometheus-stack)..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.ingress.enabled=true \
  --set grafana.ingress.annotations."cert-manager\.io/cluster-issuer"=letsencrypt-prod \
  --set grafana.ingress.annotations."traefik\.ingress\.kubernetes\.io/router\.entrypoints"=websecure \
  --set grafana.ingress.hosts[0]=grafana.paas.samchichester.com \
  --set grafana.ingress.tls[0].hosts[0]=grafana.paas.samchichester.com \
  --set grafana.ingress.tls[0].secretName=grafana-tls \
  --set prometheus.prometheusSpec.maximumStartupDurationSeconds=300

echo "Post Setup Complete!"
