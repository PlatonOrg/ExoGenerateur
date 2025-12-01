

from itertools import repeat
import json
import os
import shutil
import sys

from .ai_interaction import create_dated_output_folder
from .write_file import copy_pla_default, create_zip

def writeFile(pathDirectory,content):
    """
    ajoute le glossaire dans le fichier next.py
    
    paramètres:
    - chemin vers le fichier next.py à écrire
    - le glossaire utilisé pour les exercices   
    """
    jsonToWrite = json.dumps(content, indent=2)
    with open(pathDirectory, 'a', encoding='utf-8') as f:
        f.write(jsonToWrite)

def loadJson(path):
    """
    Charge le json de path
    paramètres : 
    - path  : chemin du fichier

    return : 
    - le contenue du fichier.
    """
    try : 
        return json.load(open(path,'r'))
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage du JSON {path}, erreur :\n{e}", file=sys.stderr)

def mergeGlossaire(dirOne, dirTwo,dirDst):
    """
    fusionne les glossaires de deux activités
    paramètres:
    -dirOne : dossier de la première activité
    -dirTwo : dossier de la seconde activité
    -dirDst : dossier des activité fusionnées
    """
    pathData = '/includes/glossaire.json'
    dataOne = loadJson(dirOne + pathData)
    dataTwo = loadJson(dirTwo + pathData)
    dataOne.extend(dataTwo)
    writeFile(dirDst + pathData,dataOne)
    
def mergeAllExercice(dirOne, dirTwo,dirDst):
    """
    fusionne toutes les données des exercices
    paramètres:
    -dirOne : dossier de la première activité
    -dirTwo : dossier de la seconde activité
    -dirDst : dossier des activité fusionnées
    """
    mergeExercice(dirOne,dirTwo,dirDst,'/includes/definition.json')
    mergeExercice(dirOne,dirTwo,dirDst,'/includes/traduction.json')
    mergeExercice(dirOne,dirTwo,dirDst,'/includes/utilisation.json')

def getMergeDirectory(message): 
    while True:
        path = input(message)
        if not os.path.exists(path):
            print(f"Erreur : le dossier '{path}' est introuvable")
        else :
            return path

def merge(): 
    """
    fusionne deux activités en une

    paramètres:
    -dirOne : dossier de la première activité
    -dirTwo : dossier de la seconde activité 
    """
    dirOne = getMergeDirectory("Saisir le nom du dossier : ")
    dirTwo = getMergeDirectory("Saisir le nom du second dossier : ")
    dirDst = create_dated_output_folder('Merge')
    copy_pla_default(dirDst)
    # copy of next.py
    try:
        shutil.copy2(os.path.join(dirOne, 'next.py'), os.path.join(dirDst, 'next.py'))
        print(f"'next.py' copié avec succès vers '{dirDst}'.")

    except FileNotFoundError:
        print(f"Erreur : le fichier  {dirDst}/next.py n'a pas été trouvé dans {dirOne}", file=sys.stderr)
    except Exception as e:
        print(f"Une erreur est survenue lors de la copie de next.py : {e}", file=sys.stderr)
    mergeGlossaire(dirOne,dirTwo,dirDst)
    mergeAllExercice(dirOne,dirTwo,dirDst)
    create_zip(dirDst,dirDst + ".zip")

def mergeExercice(dirOne, dirTwo,dirDst,pathData):
    """
    fusionne les données des exercices d'un groupe
    paramètres:
    -dirOne : dossier de la première activité
    -dirTwo : dossier de la seconde activité
    -dirDst : dossier des activité fusionnées
    -pathData : chemin vers le json du groupe
    """
    dataOne = loadJson(dirOne + pathData)
    dataTwo = loadJson(dirTwo + pathData)
    try : 
        for exerciceIndex in range(0,len(dataOne)):
            dataOne[exerciceIndex]["exercice"]["questions"].extend(dataTwo[exerciceIndex]["exercice"]["questions"])
    except Exception as e:
        print(f"Un problème est survenu lors de la fusion des éléments de : {pathData}\n : {e}",file=sys.stderr) 
    writeFile(dirDst + pathData,dataOne)



if __name__ == "__main__":
    dirOne = './output/Activite_2025-10-07_16-50-32'
    dirTwo = './output/Activite_2025-11-24_12-01-26'
    merge(dirOne,dirTwo)
