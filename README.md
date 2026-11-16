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