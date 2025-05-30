# PaaS App

This is a project I am doing to get familiar with Terraform, Kubernetes, and AWS EKS.

## Commands

### Build AWS Infrastructure

Change into the `terraform` directory

```
cd terraform
```

Initialize Terraform

```
terraform init
```

Create EKS cluster and VPC

```
caffeinate terraform apply
```

### Setup EKS Cluster

Update KubeConfig

```
aws eks --region us-east-1 update-kubeconfig --name <CLUSTER-NAME>
```

Run the post setup script to install traefik and cert-manager

```
./post_setup.sh
```

### Deploy An App

```
python3 controller/deploy_app.py <GITHUB-URL>
```
