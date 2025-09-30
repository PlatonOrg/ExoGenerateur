"""
Interaction avec l'utilisateur sur le terminal
"""
import os

from src.ai_interaction import extract_glossaire, generate_glossaire



######## glossaire

def display_help_type():
    """
    affiche l'aide pour la selection du type de données pour le glossaire
    """
    print("file         : Vous avez déjà un fichier avec le glossaire")
    print("extract      : Vous avez un fichier dont vous voulez extraire le glossaire")
    print("generate     : L'ia génére elle même les données")

def ask_glossaire_type():
    """
    récuperer le type de glosaire

    return 
    - le type de glossaire
    """
    typeGlossaire = "" # fichier / extraire / généré 
    while True:
        type = input("type de données pour le glossaire [file | extract | generate] : ").strip()
        if type:
            if(type == "file" or type == "extract" or type == "generate"):
                return type
            elif type == "help":
                display_help_type()
            else:
                print("veillez saisir un des types suivant 'file','extract' ou 'generate'")
        else :
            print("Champs obligatoire veillez saisir 'file','extract' ou 'generate'")
        print("Pour affcher l'aide saisir : help")

def read_text_file(filepath):
    """
    renvoie le contenu d'un fichier

    paramètre 
    - chemin du fichier à lire

    return 
    - son contenu
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def get_data(type, infoGeneral):
    """
    renvoie le glossaire

    paramètres
    - le type de données pour le glossaire
    - information général pour la génération 

    return :
    - le glossaire
    """
    if type == "file":
        while True:
            path = input("Saisir le chemin du fichier   :")
            if not os.path.exists(path):
                print(f"Erreur : le fichier '{path}' est introuvable")
            else :
                return read_text_file(path)

    if type == "extract":
        while True:
            path = input("Saisir le chemin du fichier   :")
            if not os.path.exists(path):
                print(f"Erreur : le fichier '{path}' est introuvable")
            else :
                return extract_glossaire(read_text_file(path), infoGeneral)

    if type == "generate" :
        return generate_glossaire(infoGeneral)
    raise ValueError(f"Ce format du glossaire n'est pas pris en compte : {type}")

def get_glossaire(infoGeneral):
    """
    demande quel type de glossaire on veut et donne le glossaire

    paramètre
    - infomation général sur l'exercice

    return 
    - le glossaiere
    """
    type = ask_glossaire_type()
    glossaire = get_data(type,infoGeneral)
    return glossaire


######## info pour les prompts

def display_help_general_info():
    """
    affiche l'aide pour la génération d'exercice
    """
    print("Obligatoire :")
    print(" matière : la matière de l'exercice (exemple : anglais | Math | C )")
    print(" type d'exercice : le format de l'exercice (exemple : pickers | matchList)")
    print("") # Ligne vide pour la séparation
    print("Optionnel :")
    print(" Pour ajouter plusieurs éléments, il faut les séparer par des virgules (ex: drôle,direct)")
    print(" personnalité : personnalité de l'exercice (exemple : drôle,direct,explique étape par étape)")
    print(" thème : préciser le thème de l'exercice (exemple : école,lecture-écriture de fichier )")
    print(" cible : définie la cible de l'exercice (exemple : licence,collège)")
    print(" indication supplémentaire : indications supplémentaire pour l'IA (exemple : je veux 2 propositions pour chaque choix)")

def ask_general_info():
    """
    Demande des infos générales pour remplir le prompt
    """
    print("\n--- Veuillez fournir les informations suivantes pour l'exercice ---")

    while True:
        matiere =   input("Matière                                                          : ").strip()
        if matiere:
            break
        else:
            print("La matière est obligatoire. Veuillez saisir une valeur.")

    theme =         input("Thème                                   (optionnel - None)       : ").strip()
    cible =         input("Cible                                   (optionnel - étudiant)   : ").strip()
    personnalite =  input("Personnalité                            (optionnel - None)       : ").strip()
    langueInst =    input("Langue des questions                    (optionnel - Français)   : ").strip()
    indicationSup = input("Indications supplémentaires pour l'IA   (optionnel - None)       : ").strip()

    info = {
        "matiere": matiere,
        "personnalite": personnalite if personnalite else None,
        "theme": theme if theme else None,
        "cible": cible if cible else "étudiant",
        "indicationSup": indicationSup if indicationSup else None,
        "langueInst": langueInst if langueInst else "français" ,
    }

    print("\n--- Informations collectées ---")
    for key, value in info.items():
        display_key = key.replace('_', ' ').replace('exo', 'exercice').title()
        if key == 'typeExo':
            display_key = 'Type d\'exercice'
        elif key == 'indicationSup':
            display_key = 'Indications supplémentaires'
        elif key == 'langueInst':
            display_key = 'Langue des questions'
        print(f"{display_key:<30}: {value if value is not None else 'Non fourni'}")
    print("\n")
    return info