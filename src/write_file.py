"""
fichier pour écrire le next.py pour l'activité
"""
# nom du fichier sans le .json : liste des template pouvant être utiliser en fonction de sont groupe
import json
import os
import shutil
import sys
import zipfile

############### INCLUDES
ALLOW_TEMPLATE = {
    # groupe definition
    "definition_picker" : [0],
    "definition_emplacement" : [1],
    "definition_match" : [2,3],

    # groupe utilisation
    "utilisation_synonyme" : [0,1],
    "utilisation_phrase_trou_picker" : [2],
    "utilisation_phrase_ordre" : [3],
    "utilisation_dialogue_theme_picker" : [4],
    "utilisation_erreur" : [5],
    "utilisation_vrai_faux" : [6],

    # groupe traduction
    "traduction_picker" : [0],
    "traduction_match" : [1,2,3]
}

def get_groupe(fileName) :
    """
    donne le numéro du groupe

    paramètre:
    - nom du fichier

    return :
    - numéro du groupe auquel appartient le fichier
    """
    if fileName[0] == "d":
        return 1
    return 2 if fileName[0] == "t" else 3

def get_allow_template(exoType):
    """
    donne la liste des templates pouvant être utilisé suivant le type d'exercice
    paramètre:
    - nom du type d'exercice

    return 
    - la liste des index des templates pouvant être utilisés 
    """
    return ALLOW_TEMPLATE[exoType]

def write_glossaire(pathDirectory,glossaire):
    """
    ajoute le glossaire dans le fichier next.py
    
    paramètres:
    - chemin vers le fichier next.py à écrire
    - le glossaire utilisé pour les exercices   
    """
    with open(pathDirectory, 'a', encoding='utf-8') as f:
        f.write(glossaire)

def write_groupe(path,groupe,numGroup):
    """
    écrit tous les exercices d'un groupe dans une liste pour le fichier next.py

    paramètres
    - le chemin vers le fichier next.py
    - la liste de toutes les données pour tous les exercices du groupe
    - le numéro du groupe
    """
    if numGroup == 1:
        path += "/definition.json"
    elif numGroup == 2:
        path += "/traduction.json"
    elif numGroup == 3 :
        path += "/utilisation.json"
    else:
        print(f"Erreur écriture du next.py : {numGroup} invalide valide pour 1,2 ou 3")   
        return 
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(groupe, f, indent=4, ensure_ascii=False)
        print(f"fichier json écrit avec succès dans '{path}'.")
    except IOError as e:
        print(f"Erreur d'écriture dans le fichier '{path}' : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
          
############### NEXT.PY
def write_next(pathDestination) :
    """
    écrit la partie code dans le next.py

    paramètre
    - chemin vers le fichier next.py
    """
    # récupère les données du fichier par défaut
    path = "./default/pla/next.txt"
    try:
        with open(path,"r") as origine:
            data = origine.read()
    except FileNotFoundError:
        print(f"Erreur écriture du next.py : Erreur : Le fichier source '{path}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur écriture du next.py : Une erreur est survenue lors de la copie du fichier (copie): {e}")

    # écrit les données dans le next.py
    try:
        with open(pathDestination,"a") as desination:
            desination.write(data)
    except FileNotFoundError:
        print(f"Erreur écriture du next.py : Le fichier source '{pathDestination}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur écriture du next.py : Une erreur est survenue lors de la copie du fichier (écriture): {e}")

############### MAIN.PLA
def copy_pla_default(pathPLADirectory):
    """
    copie les fichiers main.pla et readme.md dans le dossier output/PLA qui vient d'être créé

    parametre:
    - chemin vers le dossier en cours de création dans output/PLA
    """
    pathMain = "./default/pla/main.pla"
    pathReadme = "./default/pla/readme.md"
    try:
        shutil.copy2(pathMain, os.path.join(pathPLADirectory, 'main.pla'))
        print(f"'main.pla' copié avec succès vers '{pathPLADirectory}'.")

        # Copie readme.md
        shutil.copy2(pathReadme, os.path.join(pathPLADirectory,'readme.md'))
        print(f"'readme.md' copié avec succès vers '{pathPLADirectory}'.")

    except FileNotFoundError:
        print(f"Erreur : Un des fichiers source ('{pathMain}' ou '{pathReadme}') n'a pas été trouvé.", file=sys.stderr)
    except Exception as e:
        print(f"Une erreur est survenue lors de la copie des fichiers : {e}", file=sys.stderr)


############### ZIP
def create_relative_zip_and_cleanup(source_dir, output_zip_path):
    """
    Args:
        source_dir (str): Le chemin du dossier à ziper (ex: 'Exo').
        output_zip_path (str): Le chemin complet du fichier ZIP à créer (ex: 'Exo_content.zip').
    """
    if not os.path.isdir(source_dir):
        print(f"Erreur : Le dossier source '{source_dir}' n'existe pas.")
        return

    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                relative_path_in_zip = os.path.relpath(root, source_dir)

                if relative_path_in_zip != '.': # '.' signifie le dossier source lui-même
                    zipf.write(root, relative_path_in_zip)

                for file_name in files:
                    full_file_path = os.path.join(root, file_name)
                    arcname = os.path.relpath(full_file_path, source_dir)
                    zipf.write(full_file_path, arcname)

        print(f"Archive '{output_zip_path}' créée avec succès.")

        shutil.rmtree(source_dir)
        print(f"Dossier source '{source_dir}' supprimé avec succès.")

    except FileNotFoundError:
        print(f"Erreur : Un fichier ou dossier n'a pas été trouvé pendant l'opération.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")