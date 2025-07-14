import os

def list_files_in_folder(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        print("📂 Fichiers dans le dossier :")
        for file in files:
            print(f" - {file}")
        return files
    except FileNotFoundError:
        print("❌ Dossier non trouvé.")
        return []
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

