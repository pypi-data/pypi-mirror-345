# portfolio_ai/installer.py
import os
import subprocess

def run_setup():
    print("Cloning Django project...")
    subprocess.run(["git", "clone", "https://github.com/in2itsaurabh/AI_Powered_Portfolio_Website.git"])
    os.chdir("AI_Powered_Portfolio_Website")  # Adjust if necessary

    print("Creating virtual environment...")
    subprocess.run(["python3", "-m", "venv", "venv"])
    subprocess.run(["source", "venv/bin/activate"], shell=True)

    print("Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    print("Running migrations...")
    subprocess.run(["python", "manage.py", "migrate"])

    print("Opening in VS Code...")
    subprocess.run(["code", "."])

    print("Starting Django server...")
    subprocess.run(["python", "manage.py", "runserver"])
