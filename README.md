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

## Sécurité, Authentification et Rôles Utilisateurs
L'authentification MongoDB est activée dès l'initialisation du serveur via les variables d'environnement `MONGO_INITDB_ROOT_USERNAME` et `MONGO_INITDB_ROOT_PASSWORD`. 
Le script de migration (`migration.py`) s'authentifie avec ce compte `root` (`authSource=admin`) pour insérer les données et créer deux utilisateurs applicatifs sur la base `medical_db` selon le principe du moindre privilège :
- **`admin_medical` (Rôle : `dbOwner`)** : Utilisateur administrateur possédant tous les droits sur `medical_db` (lecture, écriture, gestion des index et des collections).
- **`lecture_medical` (Rôle : `read`)** : Utilisateur strictement restreint à la consultation des données de `medical_db`.

### Gestion des Secrets (`.env`)
Afin de prévenir toute fuite d'informations sensibles sur ce dépôt public, aucun identifiant n'est écrit en clair dans le code. Le projet utilise `python-dotenv` pour charger les secrets depuis un fichier `.env` local (strictement ignoré par Git via `.gitignore`).

**Configuration requise avant lancement :**
Créez un fichier `.env` à la racine du projet (au même niveau que `docker-compose.yml`) avec les variables suivantes :

```env
MONGO_ROOT_USER=root_admin
MONGO_ROOT_PASS=votre_mot_de_passe_root
MONGO_ADMIN_PASS=votre_mot_de_passe_admin
MONGO_READ_PASS=votre_mot_de_passe_lecture
```

## Architecture Docker Compose
L'environnement est orchestré via `docker-compose.yml`, garantissant une reproductibilité et une isolation complètes:
- **Réseau isolé (`medical_network`)** : Réseau privé de type `bridge` permettant la communication interne sécurisée entre les conteneurs.
- **Service `mongodb` (`mongodb_conteneur`)** : Héberge le serveur MongoDB avec authentification activée, persistance des données via le volume `db_data`, et un **`healthcheck`** (`mongosh --eval "db.adminCommand('ping')"`) vérifiant la disponibilité réelle de la base.
- **Service `migration_app` (`python_migration`)** : Attend que MongoDB atteigne l'état `service_healthy` avant d'exécuter le script Python de nettoyage, d'insertion et de création des utilisateurs.

### Préparation des données (Fichier CSV)
Le conteneur Python utilise un volume monté vers votre répertoire local pour lire les données sources.
**Placez simplement le fichier `healthcare_dataset.csv` à la racine du projet** (au même niveau que `docker-compose.yml`).

### Commandes d'exécution
1. Assurez-vous que le port local `27017` est libre.
2. Lancez l'infrastructure complète en arrière-plan :
   ```
   docker compose up --build -d
   ```
3. Vérifiez l'état de santé (`healthy`) du conteneur MongoDB et les logs de migration :
   ```
   docker compose ps
   docker compose logs migration_app
   ```
4. Pour arrêter les conteneurs :
   ```
   docker compose down
   ```
   *(Pour repartir d'une base vierge et réinitialiser les utilisateurs, ajoutez l'option `-v` : `docker compose down -v`)*

## Tests d'Intégrité, Opérations CRUD et Sécurité
Un script automatisé (`test_crud.py`) valide l'ensemble de l'architecture en utilisant des connexions authentifiées (`authSource=medical_db`):
1. **Intégrité volumétrique** : Vérifie que le nombre de documents insérés dans MongoDB correspond exactement au nombre de lignes uniques du fichier CSV source.
2. **Manipulation CRUD (`admin_medical`)** : Valide les opérations complètes de Création (`insert_one`), Lecture (`find_one`), Mise à jour (`update_one`) et Suppression (`delete_one`).
3. **Validation du moindre privilège (`lecture_medical`)** : Confirme que la lecture est autorisée mais que toute tentative d'insertion, de modification ou de suppression est immédiatement rejetée par MongoDB (`OperationFailure`).

Une fois l'infrastructure démarrée, exécutez la suite de tests dans le réseau Docker avec la commande :

```
docker compose run --rm migration_app python test_crud.py
```
