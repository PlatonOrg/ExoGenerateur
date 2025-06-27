"""
Interaction avec l'utilisateur sur le terminal
"""
import os

from src.ai_interaction import generate_glossaire



######## glossaire

def display_help_type():
    print("file         : Vous avez déjà un fichier avec le glossaire")
    print("extract      : Vous avez un fichier dont vous voulez extraire le glossaire")
    print("generate     : L'ia génére elle même les données")

def ask_glossaire_type():
    """
    récuperer le type de glosaire
    """
    typeGlossaire = "" # fichier / extraire / généré 
    while True:
        type = input("type de données pour le glossaire [file | extract | generate]   :").strip()
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
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def get_data(type, infoGeneral):
    """
    renvoie les données du glossaire
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
                return read_text_file(path)

    if type == "generate" :
        return generate_glossaire(infoGeneral)
    raise ValueError(f"Ce format du glossaire n'est pas pris en compte : {type}")

def get_glossaire(infoGeneral):
    """
    récupére le glossaire
    """
    type = ask_glossaire_type()
    glossaire = get_data(type,infoGeneral)
    return glossaire


######## info pour le prompt

def display_help_general_info():
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
        matiere = input("Matière            : ").strip()
        if matiere:
            break
        else:
            print("La matière est obligatoire. Veuillez saisir une valeur.")

    theme =         input("Thème                                   (optionnel): ").strip()
    cible =         input("Cible                                   (optionnel): ").strip()
    personnalite =  input("Personnalité                            (optionnel): ").strip()
    indicationSup = input("Indications supplémentaires pour l'IA   (optionnel): ").strip()

    info = {
        "matiere": matiere,
        "personnalite": personnalite if personnalite else None,
        "theme": theme if theme else None,
        "cible": cible if cible else None,
        "indicationSup": indicationSup if indicationSup else None,
        "langueInst": None,
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
        print(f"{display_key}: {value if value is not None else 'Non fourni'}")

    return info