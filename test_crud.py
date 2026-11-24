import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Chargement des variables d'environnement (.env)
load_dotenv()

ADMIN_PASS = os.getenv("MONGO_ADMIN_PASS")
READ_PASS = os.getenv("MONGO_READ_PASS")

# URIs de connexion authentifiées (via le conteneur 'mongodb' sur le réseau Docker)
ADMIN_URI = f"mongodb://admin_medical:{ADMIN_PASS}@mongodb:27017/?authSource=medical_db"
READ_URI = f"mongodb://lecture_medical:{READ_PASS}@mongodb:27017/?authSource=medical_db"


def run_automated_tests(csv_path):
    print("--- 1. AUTOMATISATION DES TESTS D'INTÉGRITÉ ---")
    
    # 1. État AVANT migration (calculé sur le CSV en appliquant la même règle de dédoublonnage)
    df = pd.read_csv(csv_path)
    df_unique = df.drop_duplicates()
    expected_count = len(df_unique)
    print(f"[Test Avant Migration] Le fichier source contient {expected_count} lignes uniques.")
    
    # 2. État APRÈS migration (Interrogation authentifiée de MongoDB)
    client = MongoClient(ADMIN_URI)
    collection = client['medical_db']['patients']
    
    actual_count = collection.count_documents({})
    print(f"[Test Après Migration] MongoDB contient {actual_count} documents.")
    
    # 3. Validation de l'intégrité
    if expected_count == actual_count:
        print("SUCCÈS : L'intégrité du volume de données est respectée (0 perte).")
    else:
        print("ERREUR : Différence détectée entre le CSV et MongoDB.")
    client.close()


def demonstrate_crud():
    print("\n--- 2. MANIPULATION CRUD SUR MONGODB (ADMIN) ---")
    client = MongoClient(ADMIN_URI)
    collection = client['medical_db']['patients']
    
    # CREATE (Créer un document spécifique)
    print("\n-> CREATE : Insertion d'un patient de test")
    test_patient = {
        "Name": "Patient Test Crud",
        "Age": 45,
        "Gender": "Male",
        "Medical Condition": "Cancer",
        "Billing Amount": 1500.50
    }
    insert_result = collection.insert_one(test_patient)
    print(f"Document inséré avec l'ID : {insert_result.inserted_id}")
    
    # READ (Lire le document)
    print("\n-> READ : Recherche du patient de test")
    patient_found = collection.find_one({"Name": "Patient Test Crud"})
    print(f"Trouvé : {patient_found['Name']}, Facture: {patient_found['Billing Amount']}")
    
    # UPDATE (Mettre à jour)
    print("\n-> UPDATE : Modification de la facture du patient")
    collection.update_one(
        {"Name": "Patient Test Crud"},
        {"$set": {"Billing Amount": 2000.00}}
    )
    patient_updated = collection.find_one({"Name": "Patient Test Crud"})
    print(f"Après mise à jour, la facture est de : {patient_updated['Billing Amount']}")
    
    # DELETE (Supprimer)
    print("\n-> DELETE : Suppression du patient de test pour nettoyer la base")
    collection.delete_one({"Name": "Patient Test Crud"})
    
    # Vérification de la suppression
    check_deleted = collection.find_one({"Name": "Patient Test Crud"})
    if check_deleted is None:
        print("Suppression confirmée. Le document n'existe plus.")
        
    client.close()


def test_read_only_security():
    print("\n--- 3. TEST DE SÉCURITÉ : COMPTE EN LECTURE SEULE ---")
    client = MongoClient(READ_URI)
    collection = client['medical_db']['patients']
    
    # 1. Vérification que la lecture est autorisée
    sample = collection.find_one()
    if sample is not None:
        print(f"[OK] Lecture autorisée pour 'lecture_medical' (Exemple lu : {sample.get('Name')}).")
    
    # 2. Vérification que l'insertion (CREATE) est strictement refusée
    print("\n-> Tentative d'insertion non autorisée avec 'lecture_medical'...")
    try:
        collection.insert_one({"Name": "Intrus Test", "Age": 99})
        print("[ÉCHEC] Faille de sécurité : le compte en lecture seule a pu insérer un document !")
    except OperationFailure as e:
        print(f"[SUCCÈS] Insertion bloquée par MongoDB comme attendu : {e.details.get('errmsg')}")

    # 3. Vérification que la modification (UPDATE) est strictement refusée
    print("\n-> Tentative de modification non autorisée avec 'lecture_medical'...")
    try:
        collection.update_one({"_id": sample["_id"]}, {"$set": {"Age": 99}})
        print("[ÉCHEC] Faille de sécurité : le compte en lecture seule a pu modifier un document !")
    except OperationFailure as e:
        print(f"[SUCCÈS] Modification bloquée par MongoDB comme attendu : {e.details.get('errmsg')}")

    # 4. Vérification que la suppression (DELETE) est strictement refusée
    print("\n-> Tentative de suppression non autorisée avec 'lecture_medical'...")
    try:
        collection.delete_one({"_id": sample["_id"]})
        print("[ÉCHEC] Faille de sécurité : le compte en lecture seule a pu supprimer un document !")
    except OperationFailure as e:
        print(f"[SUCCÈS] Suppression bloquée par MongoDB comme attendu : {e.details.get('errmsg')}")
        
    client.close()


if __name__ == "__main__":
    csv_file = 'healthcare_dataset.csv'
    run_automated_tests(csv_file)
    demonstrate_crud()
    test_read_only_security()