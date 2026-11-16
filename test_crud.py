import pandas as pd
from pymongo import MongoClient

def run_automated_tests(csv_path):
    print("--- 1. AUTOMATISATION DES TESTS D'INTÉGRITÉ ---")
    
    # 1. État AVANT migration (calculé sur le CSV en appliquant la même règle de dédoublonnage)
    df = pd.read_csv(csv_path)
    df_unique = df.drop_duplicates()
    expected_count = len(df_unique)
    print(f"[Test Avant Migration] Le fichier source contient {expected_count} lignes uniques.")
    
    # 2. État APRÈS migration (Interrogation de MongoDB)
    client = MongoClient('mongodb://host.docker.internal:27017/')
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
    print("\n--- 2. MANIPULATION CRUD SUR MONGODB ---")
    client = MongoClient('mongodb://host.docker.internal:27017/')
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

if __name__ == "__main__":
    csv_file = 'healthcare_dataset.csv'
    run_automated_tests(csv_file)
    demonstrate_crud()