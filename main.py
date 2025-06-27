import os
import shutil

from src.ai_interaction import create_dated_output_folder, generate_data, generate_glossaire, init_ia
from src.user_interaction import ask_general_info,get_glossaire


# --- Configuration ---
DEFAULT_FILES_DIR = "default"      # Dossier contenant les fichiers par défaut
TARGET_PARENT_DIR = "modeles"      # Dossier pour les prompts
README_FILENAME = "README.md"      # Nom du fichier README à ne pas copier (son contenu)


def create_component_folder(folderName):
    """
    Crée un nouveau dossier pour générer des exercices
    """
    if not os.path.isdir(DEFAULT_FILES_DIR):
        print(f"Erreur : Le répertoire cible '{TARGET_PARENT_DIR}' n'a pas été trouvé.")
        print("Veuillez créer un dossier '{TARGET_PARENT_DIR}' à la racine de votre projet.")
        return

    if not os.path.isdir(TARGET_PARENT_DIR):
        print(f"Erreur : Le répertoire '{DEFAULT_FILES_DIR}' n'a pas été trouvé à la racine du projet.")
        print(f"Veuillez vous assurer d'avoir un dossier 'default/' contenant vos fichiers par défaut.")
        return

    newPath = os.path.join(TARGET_PARENT_DIR, folderName)

    if os.path.exists(newPath):
        print(f"Erreur : Le dossier '{newPath}' existe déjà. Veuillez choisir un nom différent ou supprimer le dossier existant.")
        return

    try:
        os.makedirs(newPath)
        print(f"Dossier '{newPath}' créé avec succès.")

        # copie les fichiers du dossier default
        for item_name in os.listdir(DEFAULT_FILES_DIR):
            source_path = os.path.join(DEFAULT_FILES_DIR, item_name)
            destination_path = os.path.join(newPath, item_name)

            if os.path.isfile(source_path):
                if item_name == README_FILENAME:
                    open(destination_path, 'a').close()
                else:
                    shutil.copy2(source_path, destination_path)
            elif os.path.isdir(source_path):
                # copie les sous-dossier de default
                shutil.copytree(source_path, destination_path)
                print(f"Dossier copié : {item_name}")
        
        print(f"ous les fichiers ont été créés.")

    except Exception as e:
        print(f"Une erreur est survenue lors de la création/copie des fichiers : {e}")

def display_help():
    """
    affiche les commandes
    """
    print("Commandes:")
    print("  addComponent <nom_du_composant>    - Crée un nouveau dossier pour un nouveau composant.")
    print("  exit                               - Quitte le script.")
    print("  generate                           - Génère les exercices")
    print("  glossaire                          - Génère le glossaire")
    print("  help                               - Affiche les commandes.")
    print("-------------------------------------------------------------------------------")    

if __name__ == "__main__":
    display_help()
    init_ia()
    while True:
        try:
            ligneDeCommande = input("saisir commande: ").strip()
            partie = ligneDeCommande.split(maxsplit=1) # sépare la commande de ses arguments
            if not partie:
                continue
            commande = partie[0]
            if commande == "addComponent":
                if len(partie) < 2:
                    print("Erreur: Nom de dossier manquant. Utilisation : generate <nom_du_dossier>")
                else:
                    nomDossier = partie[1]
                    if not nomDossier.replace('_', '').replace('-', '').isalnum():
                        print("Erreur: Nom de dossier invalide. Utilisez des caractères alphanumériques, des tirets ou des tirets bas.")
                    else:
                        create_component_folder(nomDossier)
            elif commande == "exit":
                break

            elif commande == "help":
                display_help()

            elif commande == "glossaire":
                infoGeneralPrompt = ask_general_info()
                glossaire = generate_glossaire(infoGeneralPrompt)
                print("glossaire généré")
                pathDirectory = create_dated_output_folder('Exercice')
                os.makedirs(pathDirectory + '/data', exist_ok=True)
                with open(pathDirectory + '/data/glossaire.txt', 'w', encoding='utf-8') as f:
                    f.write(glossaire)

            elif commande == "generate":
                infoGeneralPrompt = ask_general_info()
                glossaire = get_glossaire(infoGeneralPrompt)
                print("glossaire généré")
                generate_data(glossaire,infoGeneralPrompt)
                
            else:
                print(f"commande inconnue: '{commande}'. Utilisez help pour plus d'information")

        except KeyboardInterrupt: # gére Ctrl+C
            print() # saut de ligne à la fin du programme
            break
        except Exception as e:
            print(f"Erreur: {e}")