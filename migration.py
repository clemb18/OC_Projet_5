import pandas as pd
from pymongo import MongoClient, ASCENDING

def clean_data(file_path):
    """Charge et nettoie les données du CSV."""
    print("Début du chargement et du nettoyage des données")
    df = pd.read_csv(file_path)
    
    # 1. Suppression des doublons
    df = df.drop_duplicates()
    
    # 2. Standardisation de la casse
    df['Name'] = df['Name'].str.title()
    
    # 3. Typage des dates
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    
    # 4. Arrondi des montants
    df['Billing Amount'] = df['Billing Amount'].round(2)
    
    print(f"Nettoyage terminé. {df.shape[0]} dossiers médicaux prêts.")
    return df

def insert_to_mongodb(df, db_name="medical_db", collection_name="patients"):
    """Insère le DataFrame nettoyé dans MongoDB."""
    print("Connexion à MongoDB")
    try:
        # 1. Connexion au serveur local
        client = MongoClient('mongodb://mongodb:27017/')
        
        # 2. Sélection de la base et de la collection
        db = client[db_name]
        collection = db[collection_name]
        
        # Sécurité : Vider la collection avant l'insertion
        collection.delete_many({})
        
        # 3. Conversion du DataFrame en dictionnaires
        print("Conversion des données...")
        documents = df.to_dict(orient='records')
        
        # 4. Insertion en masse
        print("Insertion en cours...")
        result = collection.insert_many(documents)
        
        print(f"Migration réussie ! {len(result.inserted_ids)} documents insérés dans la base '{db_name}'.")

        # --- CREATION DES INDEX ---
        print("Création des index d'optimisation...")
        
        # Index 1 : Nom de patients
        collection.create_index([("Name", ASCENDING)])
        
        # Index 2 : Maladie
        collection.create_index([("Medical Condition", ASCENDING)])
        
        # Index 3 : Date d'admission
        collection.create_index([("Date of Admission", ASCENDING)])

        print("Index créés avec succès")
        # --------------------------

        # --- SÉCURITÉ ET UTILISATEURS ---
        print("Configuration de la sécurité")
        
        # 1. Utilisateur Administrateur
        try:
            db.command(
                "createUser", "admin_medical",
                pwd="AdminPassword123!",
                roles=[{"role": "dbOwner", "db": "medical_db"}]
            )
            print("Utilisateur 'admin_medical' créé.")
        except Exception as e:
            print("Note : 'admin_medical' existe déjà ou n'a pas pu être créé.")

        # 2. Utilisateur Read-Only
        try:
            db.command(
                "createUser", "lecture_medical",
                pwd="ReadPassword123!",
                roles=[{"role": "read", "db": "medical_db"}]
            )
            print("Utilisateur 'lecture_medical' créé.")
        except Exception as e:
            print("Note : 'lecture_medical' existe déjà ou n'a pas pu être créé.")
        # --------------------------------

    except Exception as e:
        print(f"Erreur lors de la connexion ou de l'insertion : {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Le fichier source
    csv_file = 'healthcare_dataset.csv'
    
    # Exécution du nettoyage
    df_cleaned = clean_data(csv_file)
    
    # Exécution de l'insertion
    insert_to_mongodb(df_cleaned)