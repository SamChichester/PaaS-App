import os
import subprocess
from flask import Flask, redirect, url_for, request, jsonify
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
login_manager = LoginManager(app)

github_bp = make_github_blueprint(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    scope="repo"
)
app.register_blueprint(github_bp, url_prefix="/login")

class User(UserMixin):
    def __init__(self, github_username):
        self.id = github_username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/me")
def me():
    if not github.authorized:
        return jsonify({'authorized': False})
    account_info = github.get("/user").json()
    return jsonify({'authorized': True, "username": account_info["login"]})

@app.route("/repos")
@login_required
def list_repos():
    response = github.get("/user/repos")
    return jsonify(response.json())

@app.route("/deploy", methods=["POST"])
@login_required
def deploy():
    repo_url = request.json.get("repo_url")
    if not repo_url:
        return {"error": "Missing repo_url"}, 400
    result = subprocess.run(
        ["python3", "../controller/deploy_app.py", repo_url],
        capture_output=True, text=True
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

@app.route("/login/github/callback")
def github_login_callback():
    if not github.authorized:
        return redirect(url_for("github.login"))
    account_info = github.get("/user").json()
    login_user(User(account_info["login"]))
    return redirect("http://localhost:5173/dashboard")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
