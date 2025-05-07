import os
import subprocess
import sys
import shutil

def run_setup():
    repo_url = "https://github.com/in2itsaurabh/AI_Powered_Portfolio_Website.git"
    project_folder = "AI_Powered_Portfolio_Website"
    venv_folder = "venv"

    # Clone the repo
    print("📥 Cloning Django project...")
    if os.path.exists(project_folder):
        print("⚠️ Project folder already exists. Skipping clone.")
    else:
        subprocess.run(["git", "clone", repo_url])

    os.chdir(project_folder)

    # Create virtual environment
    print("🐍 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", venv_folder])

    # Activate the virtual environment
    venv_python = os.path.join(venv_folder, "bin", "python")  # Linux/macOS
    if not os.path.exists(venv_python):
        venv_python = os.path.join(venv_folder, "Scripts", "python.exe")  # Windows

    if not os.path.exists(venv_python):
        print("❌ Could not find Python in the virtual environment.")
        return

    # Install dependencies
    print("📦 Installing requirements...")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])

    # Run Django migrations
    print("🛠️ Running Django migrations...")
    subprocess.run([venv_python, "manage.py", "migrate"])

    # Open in VS Code if available
    print("🧠 Opening project in VS Code...")
    if shutil.which("code"):
        subprocess.run(["code", "."])
    else:
        print("⚠️ VS Code not found. Skipping editor launch.")

    # Start the server
    print("🚀 Starting Django development server...")
    subprocess.run([venv_python, "manage.py", "runserver"])
