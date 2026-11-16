# Projet 5 : Migration de données médicales vers MongoDB

## Contexte
Mission pour DataSoluTech visant à migrer un dataset de données médicales vers une solution NoSQL (MongoDB) pour répondre à des enjeux de scalabilité, incluant une conteneurisation via Docker.

## Logique de nettoyage et préparation des données
Avant l'insertion dans MongoDB, les données brutes ont été nettoyées à l'aide de Pandas :
- **Doublons** : Suppression de 534 lignes strictement identiques.
- **Standardisation** : Application d'une casse harmonisée (Title Case) sur les noms des patients.
- **Typage temporel** : Conversion des dates d'admission et de sortie au format `datetime` pour permettre les requêtes dans MongoDB.
- **Formatage financier** : Arrondi des montants de facturation à deux décimales.

## Optimisation et Indexation
Pour répondre aux exigences de performance, trois index spécifiques ont été créés automatiquement lors de la migration :
- **`Name` (Ascendant)** : Accélère les recherches nominatives directes.
- **`Medical Condition` (Ascendant)** : Optimise le filtrage par type de pathologie.
- **`Date of Admission` (Ascendant)** : Facilite les requêtes chronologiques.

## Sécurité et Rôles Utilisateurs
Pour sécuriser l'accès aux données médicales, deux utilisateurs sont créés directement via le script de migration :
- **`admin_medical` (Rôle : dbOwner)** : Utilisateur administrateur possédant tous les droits sur la base `medical_db` (lecture, écriture, gestion des index et des collections).
- **`lecture_medical` (Rôle : read)** : Utilisateur restreint à la consultation des données de `medical_db`.

## Tests d'Intégrité et Opérations CRUD
Un script dédié (`test_crud.py`) permet de garantir la fiabilité de la base de données :
- **Intégrité volumétrique** : Comparaison automatisée du nombre d'enregistrements entre le fichier CSV source nettoyé et la collection MongoDB.
- **Manipulation CRUD** : Démonstration automatisée des requêtes de base (Création, Lecture, Mise à jour, Suppression) via `pymongo` pour valider l'opérabilité de la base.

## Étape 2 : Docker Compose
L'environnement de production est entièrement conteneurisé via `docker-compose.yml`, garantissant une reproductibilité totale.

### Architecture
L'application repose sur deux services interconnectés dans un réseau privé :
- **Service `mongodb`** : Héberge le serveur de base de données. Il utilise un volume persistant (`db_data`) pour éviter la perte des données.
- **Service `migration_app`** : Exécute le script Python de nettoyage et d'insertion de manière éphémère.

### Préparation des données (Fichier CSV)
Le conteneur Python utilise un pont vers votre ordinateur pour lire les données. 
**Placez simplement votre fichier source `healthcare_dataset.csv` à la racine du projet** (au même niveau que le fichier `docker-compose.yml`). Le script le lira automatiquement lors de son exécution sans avoir besoin de recompiler l'image Docker.

### Commandes d'exécution
1. Assurez-vous que le port local `27017` est libre (aucun MongoDB local en cours d'exécution).
2. Lancez l'infrastructure complète (construction des images, création des volumes, et exécution de la migration) en arrière-plan :

**docker compose up --build -d**

3. Pour voir les logs du script de migration et confirmer le succès :

**docker compose logs -f migration_app**

4. Pour éteindre le serveur MongoDB et nettoyer l'environnement une fois terminé :

**docker compose down**

### Lancement des tests automatisés
Un script dédié (`test_crud.py`) permet de garantir l'intégrité volumétrique (comparaison CSV/MongoDB) et de valider les opérations CRUD (Create, Read, Update, Delete).

Une fois l'infrastructure lancée (MongoDB en cours de fonctionnement), exécutez ce script de test de manière isolée dans le conteneur avec la commande suivante :

**docker compose run --rm migration_app python test_crud.py**
