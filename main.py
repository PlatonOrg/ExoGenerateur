"""
fichier principal
"""

import os
import sys
import time


from src.ai_interaction import create_dated_output_folder, generate_data, generate_glossaire, init_ia
from src.user_interaction import ask_general_info,get_glossaire


# --- Configuration ---
DEFAULT_FILES_DIR = "default"      # Dossier contenant les fichiers par défaut
TARGET_PARENT_DIR = "modeles"      # Dossier pour les prompts
README_FILENAME = "README.md"      # Nom du fichier README à ne pas copier (son contenu)

def display_help_type():
    """
    Affiche l'aide pour les groupes dans modeles
    """
    print("\n")
    print(" - definition  : exercice utilisant la définition d'un ou plusieurs termes.")
    print(" - traduction  : exercice où il faut traduire un ou plusieurs termes.")
    print(" - utilisation : exercice sur l'utilisation des termes.")


def create_component_folder(folderName):
    """
    Crée un nouveau dossier pour générer des exercices
    """
    # vérification des dossiers
    if not os.path.isdir(DEFAULT_FILES_DIR):
        print(f"Erreur : Le répertoire cible '{TARGET_PARENT_DIR}' n'a pas été trouvé.")
        print("Veuillez créer un dossier '{TARGET_PARENT_DIR}' à la racine de votre projet.\n")
        return

    if not os.path.isdir(TARGET_PARENT_DIR):
        print(f"Erreur : Le répertoire '{DEFAULT_FILES_DIR}' n'a pas été trouvé à la racine du projet.")
        print("Veuillez vous assurer d'avoir un dossier 'default/' contenant vos fichiers par défaut.\n")
        return

    # récupération du groupe
    while True:
        type = input("type d'exercice [definition | traduction | utilisation] : ").strip()
        if type:
            if(type == "definition" or type == "traduction" or type == "utilisation"):
                break
            elif type == "help":
                display_help_type()
            else:
                print("veillez saisir un des types suivant 'definition','traduction' ou 'utilisation'\n")
        else :
            print("Champs obligatoire veillez saisir 'definition','traduction' ou 'utilisation'\n")
        print("Pour affcher l'aide saisir : help\n")
    
    # récupération du prompt
    while True:
        content = input("Saisir le prompt :\n")
        while True :
            valide = input("confirmer le prompt [o/n] : ")
            if valide == "o" or valide == "n":
                break
        if valide == "o":
            break

    # création du dossier et du fichier prompt.txt
    newPath = os.path.join(TARGET_PARENT_DIR, type + "/" + folderName)
    try:
        os.makedirs(newPath)
        print(f"Dossier créé : '{newPath}'")

    except FileExistsError:
        print(f"Attention : Le dossier '{newPath}' existe déjà. Utilisation du dossier existant.", file=sys.stderr)
        return
    except Exception as e:
        print(f"Erreur inattendue lors de la création du dossier : {e}", file=sys.stderr)
        return 
    
    with open(newPath + "/prompt.txt", 'w', encoding='utf-8') as f:
        f.write(content)

def display_help():
    """
    affiche les commandes
    """
    print("Commandes:")
    print("  addExercie [nom de l'exercice ]    - Crée un nouveau dossier pour un nouveau exercice.")
    print("  exit                               - Quitte le script.")
    print("  generate                           - Génère les exercices")
    print("  glossaire                          - Génère le glossaire")
    print("  help                               - Affiche les commandes.")
    print("-------------------------------------------------------------------------------")    

def isTimeOK(last_request,isPLA = False):
    """
    Le nombre de requête à  l'ia est limiter à 15 par minutes
    - timestamp de la derniére requête
    - boolean True si on génére une activité, False si c'est juste un glossaire
    """
    timeToWait = 60
    if isPLA :
        timeToWait = 20
    if time.time() - last_request < timeToWait:
        print(f"Merci de patienter encore {timeToWait - (time.time() - last_request)} secondes. (le nombre de requêtes par minutes à l'ia est limité)")
        return False
    return True

if __name__ == "__main__":
    display_help()
    init_ia()
    last_request = 0
    while True:
        try:
            ligneDeCommande = input("saisir commande : ").strip()
            partie = ligneDeCommande.split(maxsplit=1) # sépare la commande de ses arguments
            if not partie:
                continue
            commande = partie[0]
            if commande == "addExercice":
                if len(partie) < 2:
                    print("Erreur: Nom de dossier manquant. Utilisation : addExercice <nom_de_l_exercice>")
                else:
                    nomDossier = partie[1]
                    if not nomDossier.replace('_', ''):
                        print("Erreur: Nom de dossier invalide. Utilisez des caractères alphanumériques, des tirets, des tirets bas ou des barres obligue.")
                    else:
                        create_component_folder(nomDossier)
            elif commande == "exit":
                break

            elif commande == "help":
                display_help()

            elif commande == "glossaire":
                if isTimeOK(last_request):
                    infoGeneralPrompt = ask_general_info()
                    glossaire = get_glossaire(infoGeneralPrompt)
                    pathDirectory = create_dated_output_folder('Glossaire', True)
                    with open(pathDirectory + '/glossaire.json', 'w', encoding='utf-8') as f:
                        f.write(glossaire)
                    print(f"glossaire généré dans {pathDirectory}")

            elif commande == "generate":
                if isTimeOK(last_request,True):
                    last_request = time.time()
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