import os
import subprocess

def run_command(command):
    """Helper function to run shell commands."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

def init_git_repo(repo_name, github_username):
    # Initialiser un nouveau dépôt Git localement
    run_command('git init')
    
    # Ajouter tous les fichiers du projet
    run_command('git add .')

    # Faire un premier commit
    run_command('git commit -m "Initial commit"')

    # Ajouter le dépôt GitHub en tant que remote
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"
    run_command(f'git remote add origin {remote_url}')

    # Pousser les changements sur GitHub
    run_command('git branch -M main')
    run_command('git push -u origin main')

if __name__ == "__main__":
    # Nom du dépôt et du compte GitHub
    repo_name = "task_model"
    github_username = input("Entre ton nom d'utilisateur GitHub: ")

    # Initialiser le dépôt Git
    init_git_repo(repo_name, github_username)
