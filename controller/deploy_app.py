import os
import subprocess
import tempfile
import yaml
import sys
import shutil
import uuid
from git import Repo

AWS_REGION = 'us-east-1'
ECR_REPO = '597807258698.dkr.ecr.us-east-1.amazonaws.com/user-apps'

def clone_repo(git_url: str, branch: str = "main") -> str:
    temp_dir = tempfile.mkdtemp()
    print(f"[INFO] Cloning repo {git_url} to {temp_dir}.")
    Repo.clone_from(git_url, temp_dir, branch=branch)
    return temp_dir

def load_config(repo_path: str) -> dict:
    config_path = os.path.join(repo_path, "paas.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError("paas.yaml not found in repo.")
    
    with open(config_path) as f:
        return yaml.safe_load(f)
    
def build_and_push_image(repo_path: str, app_name: str, tag: str) -> str:
    image_uri = f"{ECR_REPO}:{tag}"
    print(f"[INFO] Building image {image_uri}.")
    
    subprocess.run([
        "docker", "build",
        "--platform=linux/amd64",
        "-t", image_uri,
        "."
    ], cwd=repo_path, check=True)

    print(f"[INFO] Pushing image {image_uri} to ECR.")

    subprocess.run([
        "aws", "ecr", "get-login-password", "--region", AWS_REGION
    ], check=True, stdout=subprocess.PIPE)

    subprocess.run(["docker", "push", image_uri], check=True)
    return image_uri

def deploy_with_helm(app_name: str, image: str, port: int) -> None:
    print(f"[INFO] Deploying {app_name} with Helm.")
    subprocess.run([
        "helm", "upgrade", "--install", app_name, "./charts/user-app",
        f"--set=image={image}"
        f"--set=port={port}"
    ], check=True)

def main(git_url: str) -> None:
    repo_path = clone_repo(git_url)
    config = load_config(repo_path)

    app_name = config["app_name"]
    image_build = config.get("image_build", True)
    port = config.get("port", 80)
    image_tag = str(uuid.uuid4())[:8]

    if image_build:
        image = build_and_push_image(repo_path, app_name, image_tag)
    else:
        image = config["image"]

    deploy_with_helm(app_name, image, port)
    shutil.rmtree(repo_path)

    print(f"[DONE] App {app_name} deployed successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] Usage: python3 deploy_app.py <git_repo_url>")
        sys.exit(1)

    main(sys.argv[1])
