import os
import subprocess

# Contenu du fichier .gitignore
gitignore_content = """
# Environnements virtuels
venv/
new_venv/

# Fichiers temporaires de Python
*.pyc
__pycache__/

# Caches de tests et outils de vérification
.mypy_cache/
.pytest_cache/

# Configurations locales
.env
.vscode/

# Fichiers journaux
*.log
"""

# Crée ou écrase le fichier .gitignore
with open(".gitignore", "w") as f:
    f.write(gitignore_content)

# Exécute la commande Git pour supprimer les fichiers déjà suivis mais qui devraient être ignorés
# sans les supprimer physiquement du disque
subprocess.run(["git", "rm", "-r", "--cached", "."])

# Ajouter de nouveau tous les fichiers (ceux qui ne sont pas ignorés)
subprocess.run(["git", "add", "."])

# Faire un commit propre
subprocess.run(["git", "commit", "-m", "Clean repo by removing unnecessary files"])

# Pousser les changements vers le dépôt distant
subprocess.run(["git", "push"])
