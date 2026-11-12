# Projet 5 : Migration de données médicales vers MongoDB

## Contexte
Mission pour DataSoluTech visant à migrer un dataset de données médicales vers une solution NoSQL (MongoDB) pour répondre à des enjeux de scalabilité, incluant une conteneurisation via Docker.

## Logique de nettoyage et préparation des données
Avant l'insertion dans MongoDB, les données brutes ont été nettoyées à l'aide de Pandas :
- **Doublons** : Suppression de 534 lignes strictement identiques.
- **Standardisation** : Application d'une casse harmonisée (Title Case) sur les noms des patients.
- **Typage temporel** : Conversion des dates d'admission et de sortie au format `datetime` pour permettre les requêtes dans MongoDB.
- **Formatage financier** : Arrondi des montants de facturation à deux décimales.