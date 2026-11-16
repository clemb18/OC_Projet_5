# 1. Image de base
FROM python:3.10-slim

# 2. Dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Ajout du fichier des dépendances dans le conteneur
COPY requirements.txt .

# 4. Installation pandas et pymongo dans le conteneur
RUN pip install --no-cache-dir -r requirements.txt

# 5. Ajout du reste des fichiers (CSV, migration.py, etc.)
COPY . .

# 6. Commande à exécuter automatiquement au démarrage du conteneur
CMD ["python", "migration.py"]