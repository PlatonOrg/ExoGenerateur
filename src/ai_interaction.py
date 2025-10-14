"""
Fichier pour interragir avec l'ia
"""
import json
import os
import sys
import google.generativeai as genai

from datetime import datetime
from dotenv import load_dotenv
from .write_file import copy_pla_default, create_relative_zip_and_cleanup, get_allow_template, get_groupe, write_next, write_glossaire, write_groupe

GEMINI_API_KEY = None
IA_MODEL = None
MODEL_TYPE = 'gemini-2.5-flash'

########## initialisation et requête

def init_ia():
    """
    initilialise l'envoie de requête à l'ia
    """
    global GEMINI_API_KEY
    global IA_MODEL
    load_dotenv()

    # Récupère la clé API Gemini
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not GEMINI_API_KEY:
        print("Erreur : La clé API Gemini (GOOGLE_API_KEY) n'est pas configurée dans votre fichier .env.", file=sys.stderr)
        print("Veuillez consulter la documentation pour savoir comment l'obtenir et la configurer.", file=sys.stderr)
        exit()

    # Configure l'accès à l'API
    genai.configure(api_key=GEMINI_API_KEY)

    # Initialise le modèle
    try:
        IA_MODEL = genai.GenerativeModel(MODEL_TYPE)
        print(f"Modèle Gemini {MODEL_TYPE} initialisé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du modèle Gemini : {e}", file=sys.stderr)
        print("Vérifiez votre connexion internet et votre clé API.", file=sys.stderr)
        exit()

def ask_gemini(prompt):
    """
    Envoie la question (prompt) au modèle Gemini et retourne sa réponse au format str.
    En cas d'erreur renvoie ""

    paramètre
    - la requête à envoyer

    """
    if not prompt.strip():
        print("Erreur : requête vide", file=sys.stderr)
        return ""

    try:
        print("Une requête à l'ia est en cours de traitement : ", end="")
        reponseBrut = IA_MODEL.generate_content(prompt)
        print("réponse reçue")
        if reponseBrut and reponseBrut.text:
            reponse = reponseBrut.text.strip()

            if reponse.startswith('```json') and reponse.endswith('```'):
                return reponse[len('```json\n'):-len('\n```')].strip()

            elif reponse.startswith('```') and reponse.endswith('```'): #juste '```'
                 return reponse[len('```\n'):-len('\n```')].strip()
            else:
                print(f"Pas de balise {reponseBrut}")
                return reponse # Pas de balises
        else:
            print(f"L'IA n'a pas pu générer une réponse textuelle valide. Raison(s) de blocage : {reponseBrut.prompt_feedback}", file=sys.stderr)
            return ""

    except Exception as e:
        print(f"Une erreur est survenue lors de la communication avec l'IA : {e}", file=sys.stderr)
        return ""

######### glossaire

def extract_glossaire(fileContent, infoGeneral):
    """
    Extrait le glossaire à partir d'un texte en utilisant les règles strictes 
    de formatage des termes, définitions et traductions. Le contexte est fourni par infoGeneral.
    
    paramètres:
    - fileContent: le texte du fichier contenant le glossaire à extraire
    - infoGeneral: Un dictionnaire contenant les informations contextuelles ('matiere', 'theme', 'indicationSup')

    return: 
    - le glossaire au format JSON (string)
    """
    # Intégration de la logique de construction du sujet et des langues à partir de infoGeneral
    # Utilisation de .get() pour gérer les clés "theme" et "indicationSup" manquantes sans erreur.
    sujet = "matière : " + infoGeneral["matiere"]
    if infoGeneral.get("theme") is not None:
        sujet += " , thème : " + infoGeneral["theme"]

    if infoGeneral.get("indicationSup") is not None:
        sujet += " , indications supplémentaires : " + infoGeneral["indicationSup"]
    
    # Définition des langues basée sur infoGeneral et la langue de traduction fixée
    langueDefinition = infoGeneral["matiere"] # Ex: "Anglais", basé sur la matière
    langueTraduction = "Francais" # Fixé

    # Instructions système détaillées pour assurer la cohérence et le formatage strict
    system_instruction_content = f"""Tu es un expert linguistique et terminologue de renom, spécialisé dans l'extraction de glossaires techniques et conceptuels. Ton rôle est d'extraire un glossaire complet et précis à partir du texte fourni. Pour chaque terme pertinent que tu identifieras, tu devras fournir:
                1.  Le terme lui-même.
                    ***RÈGLE ABSOLUE POUR LE 'TERM' : Le 'term' doit être un unique mot de dictionnaire, ou un nom composé très court (maximum 2-3 mots si inséparable, comme "Artificial Intelligence"). AUCUNE phrase, AUCUNE question, AUCUNE réponse, AUCUNE expression verbale avec "to" + verbe + complément, AUCUNE expression idiomatique longue.***

                    ***RÈGLE DE CASSE POUR LE 'TERM' : Le 'term' DOIT commencer par une MINUSCULE, sauf s'il s'agit d'un NOM PROPRE (ex: "France", "Paris") ou d'un ACRONYME (ex: "NATO", "AI"). Pour tout autre terme, y compris les noms communs ou composés, il DOIT commencer par une minuscule. N'utilise JAMAIS de majuscule pour un nom commun, même s'il apparaît en début de phrase dans une définition.***

                    **ACCEPTE UNIQUEMENT LES TERMES DE CE TYPE ET CASSE :**
                    * **Mots uniques (minuscule) :** "name", "hello", "hi", "greeting", "origin", "meet", "fine", "introduce", "travel", "speak", "locomotive", "age", etc.
                    * **Noms propres (majuscule initiale) :** "France", "Paris", "Gemini".
                    * **Acronymes (tout en majuscules) :** "NATO", "AI".
                    * **Noms composés très courts (max 3 mots, formant un seul concept, minuscule initiale) :** "handshake", "thank you", "artificial intelligence", "decision-making", "user interface".

                    **REJETTE ABSOLUMENT ET NE DOIS JAMAIS GÉNÉRER CES TYPES DE 'TERM' :**
                    * **Phrases ou questions :** "My name is...", "How are you?", "I'm fine, thank you", "And you?", "Nice to meet you", "It's a pleasure to meet you", "Pleased to meet you".
                    * **Expressions verbales longues ou avec compléments :** "To introduce oneself", "To meet someone", "Come from".

                2.  Une définition concise et claire, rédigée en {langueDefinition}.
                    ***CONTRAINTE DE DÉFINITION : La définition DOIT être simple à comprendre, complète, et ne DOIT PAS contenir le terme qu'elle définit afin d'éviter toute circularité et de garantir une explication autonome.***
                    ***RÈGLE ABSOLUE DE NUANCE ET DE DIVERSITÉ DES TRADUCTIONS : Si des termes sont sémantiquement très proches ou peuvent partager des traductions identiques dans la langue cible (ex: 'travel' et 'voyage' en Anglais se traduisant par 'voyage' en Français), tu DOIS ABSOLUMENT fournir des définitions et des traductions qui mettent en évidence leurs nuances spécifiques, contextes d'usage, ou différences subtiles. Chaque terme doit avoir une définition unique et, si possible, une traduction qui le distingue clairement des autres. Pour les cas de traductions identiques, ajoute une précision entre parenthèses dans la traduction pour forcer la distinction (ex: "voyage (déplacement général)" pour 'travel' et "voyage (longue durée, aventure)" pour 'journey'). C'est CRUCIAL pour la génération d'exercices de quiz ultérieurs.***

                3.  Des traductions pour ce terme. L'objet 'translation' DOIT toujours inclure les clés '{langueDefinition}' et '{langueTraduction}'. Si un terme est déjà dans l'une de ces langues, la valeur de sa traduction pour cette langue peut être le terme lui-même (si universellement reconnu) ou une chaîne vide. Pour les autres cas, fournis la traduction la plus courante et appropriée, **en respectant strictement la RÈGLE ABSOLUE DE NUANCE ET DE DIVERSITÉ DES TRADUCTIONS mentionnée ci-dessus.**

                Assure-toi que la sortie est un tableau JSON STRICTEMENT conforme au format spécifié, où chaque entrée représente un terme du glossaire. Maintiens une cohérence parfaite dans la structure des clés de l'objet 'translation' pour toutes les entrées. Concentre-toi sur les termes clés et les concepts fondamentaux extraits du texte.
                """

    prompt = {
        "model": MODEL_TYPE,
        "messages": [
            {
                "role": "system",
                "content": system_instruction_content
            },
            {
                "role": "user",
                "content": f"""Extrais un glossaire des termes clés trouvés dans le texte suivant, en respectant toutes les règles de formatage spécifiées dans les instructions système.

    Le contexte de cette extraction est le suivant : "**{sujet}**".

    La langue principale pour les définitions est le **{langueDefinition}**.

    Le format de sortie DOIT être une liste JSON de dictionnaires, comme ceci :

    ```json
    [
        {{
            "term": "[Terme extrait (mot unique ou expression nominale max 3 mots, avec minuscule sauf nom propre/acronyme)]",
            "definition": "[Définition du terme dans la langue souhaitée]",
            "translation": {{
                "{langueDefinition}": "[Terme en langue de définition, ou sa traduction]",
                "{langueTraduction}": "[Traduction du terme dans la langue opposée, ou le terme si déjà dans cette langue)]"
            }}
        }},
        // ... autres termes
    ]
    ```

    Voici le texte à analyser :
    
    {fileContent}
    """
            }
        ],
        "response_format": { "type": "json_object" },
        "temperature": 0.1 
    }
    return ask_gemini(json.dumps(prompt))

def generate_glossaire(infoGeneral):
    """
    génère un glossaire

    paramètre
    - information général sur l'activité

    return
    - le glossaire
    """
    sujet = "matière : " + infoGeneral["matiere"]
    if infoGeneral["theme"] is not None:
        sujet += " , thème : " + infoGeneral["theme"]

    if infoGeneral["indicationSup"] is not None:
        sujet += " , indications supplémentaires : " + infoGeneral["indicationSup"]
    
    langueDefinition = infoGeneral["matiere"] # Ex: "Anglais"
    langueTraduction = "Francais" # Ex: "Francais"

    prompt = {
        "model": MODEL_TYPE,
        "messages": [
            {
                "role": "system",
                "content": f"""Tu es un expert linguistique et terminologue de renom, spécialisé dans la création de glossaires techniques et conceptuels. Ton rôle est de générer un glossaire complet et précis sur le sujet spécifié par l'utilisateur. Pour chaque terme pertinent que tu identifieras ou créeras, tu devras fournir:
                1.  Le terme lui-même.
                    ***RÈGLE ABSOLUE POUR LE 'TERM' : Le 'term' doit être un unique mot de dictionnaire, ou un nom composé très court (maximum 2-3 mots si inséparable, comme "Artificial Intelligence"). AUCUNE phrase, AUCUNE question, AUCUNE réponse, AUCUNE expression verbale avec "to" + verbe + complément, AUCUNE expression idiomatique longue.***

                    ***RÈGLE DE CASSE POUR LE 'TERM' : Le 'term' DOIT commencer par une MINUSCULE, sauf s'il s'agit d'un NOM PROPRE (ex: "France", "Paris") ou d'un ACRONYME (ex: "NATO", "AI"). Pour tout autre terme, y compris les noms communs ou composés, il DOIT commencer par une minuscule. N'utilise JAMAIS de majuscule pour un nom commun, même s'il apparaît en début de phrase dans une définition.***

                    **ACCEPTE UNIQUEMENT LES TERMES DE CE TYPE ET CASSE :**
                    * **Mots uniques (minuscule) :** "name", "hello", "hi", "greeting", "origin", "meet", "fine", "introduce", "travel", "speak", "locomotive", "age", etc.
                    * **Noms propres (majuscule initiale) :** "France", "Paris", "Gemini".
                    * **Acronymes (tout en majuscules) :** "NATO", "AI".
                    * **Noms composés très courts (max 3 mots, formant un seul concept, minuscule initiale) :** "handshake", "thank you", "artificial intelligence", "decision-making", "user interface".

                    **REJETTE ABSOLUMENT ET NE DOIS JAMAIS GÉNÉRER CES TYPES DE 'TERM' :**
                    * **Phrases ou questions :** "My name is...", "How are you?", "I'm fine, thank you", "And you?", "Nice to meet you", "It's a pleasure to meet you", "Pleased to meet you".
                    * **Expressions verbales longues ou avec compléments :** "To introduce oneself", "To meet someone", "Come from".

                2.  Une définition concise et claire, rédigée en {langueDefinition}.
                    ***CONTRAINTE DE DÉFINITION : La définition DOIT être simple à comprendre, complète, et ne DOIT PAS contenir le terme qu'elle définit afin d'éviter toute circularité et de garantir une explication autonome.***
                    ***RÈGLE ABSOLUE DE NUANCE ET DE DIVERSITÉ DES TRADUCTIONS : Si des termes sont sémantiquement très proches ou peuvent partager des traductions identiques dans la langue cible (ex: 'travel' et 'voyage' en Anglais se traduisant par 'voyage' en Français), tu DOIS ABSOLUMENT fournir des définitions et des traductions qui mettent en évidence leurs nuances spécifiques, contextes d'usage, ou différences subtiles. Chaque terme doit avoir une définition unique et, si possible, une traduction qui le distingue clairement des autres. Pour les cas de traductions identiques, ajoute une précision entre parenthèses dans la traduction pour forcer la distinction (ex: "voyage (déplacement général)" pour 'travel' et "voyage (longue durée, aventure)" pour 'journey'). C'est CRUCIAL pour la génération d'exercices de quiz ultérieurs.***

                3.  Des traductions pour ce terme. L'objet 'translation' DOIT toujours inclure les clés '{langueDefinition}' et '{langueTraduction}'. Si un terme est déjà dans l'une de ces langues, la valeur de sa traduction pour cette langue peut être le terme lui-même (si universellement reconnu) ou une chaîne vide. Pour les autres cas, fournis la traduction la plus courante et appropriée, **en respectant strictement la RÈGLE ABSOLUE DE NUANCE ET DE DIVERSITÉ DES TRADUCTIONS mentionnée ci-dessus.**

                Assure-toi que la sortie est un tableau JSON STRICTEMENT conforme au format spécifié, où chaque entrée représente un terme du glossaire. Maintiens une cohérence parfaite dans la structure des clés de l'objet 'translation' pour toutes les entrées. Concentre-toi sur les termes clés et les concepts fondamentaux du sujet.
                """
            },
            {
                "role": "user",
                "content": f'''Génère un glossaire sur le sujet suivant : "**{sujet}**".
    La langue principale pour les définitions est le **{langueDefinition}**.

    Le format de sortie DOIT être une liste JSON de dictionnaires, comme ceci :

    ```json
    [
        {{
            "term": "[Terme généré (mot unique ou expression nominale max 3 mots, avec minuscule sauf nom propre/acronyme)]",
            "definition": "[Définition du terme dans la langue souhaitée]",
            "translation": {{
                "{langueDefinition}": "[Terme en langue de définition, ou sa traduction]",
                "{langueTraduction}": "[Traduction du terme dans la langue opposée, ou le terme si déjà dans cette langue)]"
            }}
        }},
        // ... autres termes
    ]
    '''
            }
        ],
        "response_format": { "type": "json_object" },
        "temperature": 0.5
    }

    return ask_gemini(json.dumps(prompt))
######### prompt dans modeles

def find_exo_prompt():
    """
    Cherche les fichier prompt.txt dans modeles et tout ses sous-repertoire

    return 
    - la liste des chemins vers les fichiers "prompt.txt"
    """
    directory = "modeles"
    paths = []
    fileName = "prompt.txt"

    if not os.path.exists(directory):
        print(f"Erreur : Le répertoire '{directory}' n'existe pas.", file=sys.stderr)
        return paths

    for root, _, files in os.walk(directory):
        if fileName in files:
            relative_path = os.path.relpath(os.path.join(root, fileName), directory)
            paths.append(relative_path)
            
    return paths

######## génération des données des exercices

def create_folder(newFolder):
    """
    créer un dossier
    
    paramètres
    - nom du dossier
    
    return 
    - True si aucun problème, False sinon
    """
    try:
        os.makedirs(newFolder)
        print(f"Dossier créé : '{newFolder}'")
        return True
    except FileExistsError:
        print(f"Attention : Le dossier '{newFolder}' existe déjà. Utilisation du dossier existant.", file=sys.stderr)
    except Exception as e:
        print(f"Erreur inattendue lors de la création du dossier : {e}", file=sys.stderr)
    return False

def create_dated_output_folder(name, generateGlossaire=False):
    """
    créer un dossier de type [name]_[timestamp] pour y mettre toutes les données des exercices

    paramètre
    - nom à donner au dossier avant le timestamp
    - boolean True pour la génération d'un glossaire, False pour la génération d'une activité 
    """
    directory2 = "./output"
    os.makedirs(directory2, exist_ok=True)

    now = datetime.now()
    
    # Format du nom de dossier : [matiere]_AAAA-MM-JJ_HH-MM-SS
    folderName = f"{name.replace(' ', '_')}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
    newFolderPLA = os.path.join(directory2, folderName)
    if not create_folder(newFolderPLA) :
        return ""
    
    if generateGlossaire:
        return newFolderPLA
    
    if not create_folder(newFolderPLA+"/includes") :
        return ""
    return newFolderPLA

def generalPrompt(glossaire, generalInfo):
    """
    Génère le prompt général pour la création d'exercices regroupés deux par deux.

    paramètres :
    - le glossaire à utiliser
    - les informations général

    return
    - le prompt général
    """
    langue = generalInfo.get('langueInst', generalInfo['matiere'])
    matiere = generalInfo['matiere']
    personnalite = generalInfo.get('personnalite', 'None')
    theme = generalInfo.get('theme', 'None')
    cible = generalInfo.get('cible', 'None')
    indicationSup = generalInfo.get('indicationSup', 'None')

    # Le prompt général de base
    return f"""Tu es un concepteur d'exercices pédagogiques expert, spécialisé dans la création d'activités interactives basées sur des glossaires thématiques. Ton objectif est de générer des exercices adaptés, en utilisant les informations fournies.

---

**Contexte de l'exercice :**

Voici un glossaire que tu devras utiliser pour créer les exercices. Chaque entrée contient un terme, sa définition, et des traductions :

```json
{glossaire}
```

Informations supplémentaires pour la personnalisation des exercices :

Ces détails aident à affiner le ton, le thème, la cible et les spécificités des exercices. S'ils sont absents, tu devras t'adapter au contexte général fourni par le glossaire.

    - Matière : {matiere}
    - Personnalité (ton/style) : {personnalite}
    - Thème spécifique : {theme}
    - Cible (public visé) : {cible}
    - Indications supplémentaires : {indicationSup}
    - Langue des instructions (langueInst) : {langue}

Consignes pour la génération des exercices :

En t'appuyant sur le glossaire et les informations supplémentaires ci-dessus, crée un ou plusieurs exercices distincts.

Tu dois générer UN SEUL fichier JSON final. Ce JSON doit contenir une clé racine nommée "exercices". La valeur de cette clé doit être une liste d'objets JSON, où chaque objet de la liste représente un exercice complet.

Chaque exercice dans la liste doit suivre le format JSON exact spécifié dans les sections "Instructions pour l'Exercice X" ci-dessous.

Tu dois impérativement générer le JSON strictement selon ces instructions, en remplissant les données requises avec les informations pertinentes issues du glossaire et en respectant la matière, la personnalité, le thème, la cible, et les indications supplémentaires dans la mesure du possible pour les instructions et le contenu de l'exercice.

Assure-toi que les termes et définitions extraits du glossaire sont exactement ceux fournis, sans aucune modification ou paraphrase, à moins que les instructions de format ne spécifient explicitement une transformation.
"""

def get_content(lstPrompt, index):
    """
    Donne le prompt pour les exercices, les regrouper par 2 quand c'est possible

    paramètres
    - liste des emplacements de tous les prompts
    - index du prompt à traiter dans la liste des prompts    
    
    return
    - booleen True si erreur sinon False
    - la liste des noms des prompts utilisés
    - le contenu des prompts utilisés
    """
    fileContents = []
    fileNames = []

    pathComplete1 = os.path.join("modeles", lstPrompt[index])
    fileName1 = lstPrompt[index].replace(os.sep, '_').replace('_prompt.txt', '')
    fileNames.append(fileName1)
    try:
        with open(pathComplete1, 'r', encoding='utf-8') as f:
            fileContents.append(f.read())
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{pathComplete1}' n'a pas été trouvé. Passage au prompt suivant.", file=sys.stderr)
        return True, fileNames,fileContents
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier '{pathComplete1}' : {e}", file=sys.stderr)
        return True,  fileNames,fileContents

    if index + 1 < len(lstPrompt):
        pathComplete2 = os.path.join("modeles", lstPrompt[index+1])
        fileName2 = lstPrompt[index+1].replace(os.sep, '_').replace('_prompt.txt', '')
        fileNames.append(fileName2)
        try:
            with open(pathComplete2, 'r', encoding='utf-8') as f:
                fileContents.append(f.read())
        except FileNotFoundError:
            print(f"Erreur: Le fichier '{pathComplete2}' n'a pas été trouvé. Traitement du premier prompt seul.", file=sys.stderr)
            return True, fileNames,fileContents
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier '{pathComplete2}' : {e}", file=sys.stderr)
            return True, fileNames,fileContents
        
    return False, fileNames,fileContents

def get_promptAsk(basePrompt, fileContents):
    """
    donne le prompt complet pour la requête à l'ia

    paramètres
    - le prompt de base
    - liste contenant 1 prompt pour 1 exercice ou 2 pour 2 exercices

    return
    - prompt complet pour l'ia
    """
    promptAsk = basePrompt + "\n\n"
    if len(fileContents) == 2:
        promptAsk += "\n---"
        promptAsk += f"\n### Instructions de format et type d'exercice 1 :\n\n{fileContents[0]}"
        promptAsk += "\n---"
        promptAsk += f"\n### Instructions de format et type d'exercice 2 :\n\n{fileContents[1]}"
    elif len(fileContents) == 1:
        promptAsk += "\n---"
        promptAsk += f"\n### Instructions de format et type d'exercice 1 :\n\n{fileContents[0]}"
    return promptAsk

def generate_data(glossaire, generalInfo):
    """
    Génère les données pour tous les exercices en regroupant les prompts deux par deux. et complete le fichier next.py

    paramètres
    - le glossaire à utiliser
    - information générale sur l'activité
    """
    # initialisation des données
    lstPrompt = find_exo_prompt()   # cherche les prompt.txt dans modeles
    saveGroup = 1                   # groupe des exercices ) sauvegarder 1-définition, 2-traduction, 2-utilation
    indexInGroup = 0                # index de l'exercice dans le groupe
    lstGroupe = []                  # liste des exercices dans le groupe

    if not lstPrompt:
        print("Aucun fichier 'prompt.txt' trouvé dans le répertoire 'modeles'. Aucune donnée générée.", file=sys.stderr)
        return
    
    basePrompt = generalPrompt(glossaire, generalInfo)
    print("Prompt général complété.")

    pathPLADirectory = create_dated_output_folder('Activite')
    if pathPLADirectory == "":
        return # erreur création des dossiers

    pathNext_py = pathPLADirectory + "/next.py"
    includePLAPath = pathPLADirectory + "/includes"


    write_glossaire(includePLAPath + "/glossaire.json",glossaire)

    # parcours les prompts et génère les exercices
    for i in range(0, len(lstPrompt), 2):

        erreur,fileNames,fileContents = get_content(lstPrompt,i)
        if erreur:
            continue # il y a eu un problème lors de la récupération des données

        promptAsk = get_promptAsk(basePrompt,fileContents)

        try:
            reponse = ask_gemini(promptAsk)
            reponseJson = json.loads(reponse)
            if "exercices" in reponseJson and isinstance(reponseJson["exercices"], list):
                if len(reponseJson["exercices"]) == len(fileNames):
                    for idx, exercise_data in enumerate(reponseJson["exercices"]):

                        groupe = get_groupe(fileNames[idx])
                        if groupe != saveGroup :
                            write_groupe(includePLAPath,lstGroupe,saveGroup)
                            lstGroupe = [{
                                "template" : get_allow_template(fileNames[idx]),
                                "exercice": exercise_data
                            }]
                            saveGroup = groupe
                            indexInGroup = 0
                        else :
                            lstGroupe.append({
                                "template" : get_allow_template(fileNames[idx]),
                                "exercice": exercise_data
                            })

                        name = "'"+fileNames[idx] + ".json'"
                        print(f"Exercice {name:<40} généré (index : {indexInGroup})")
                        indexInGroup += 1

                else:
                    print(f"Erreur : Le nombre d'exercices générés par Gemini ({len(reponseJson['exercices'])}) ne correspond pas au nombre de prompts envoyés ({len(fileNames)})", file=sys.stderr)
                    print(f"Le fichier qui devait être généré était : {fileNames}", file=sys.stderr)
            else:
                print(f"Erreur : Le format de la réponse est invalide pour les prompts {', '.join(fileNames)}. La clé 'exercices' est manquante ou n'est pas une liste.", file=sys.stderr)
                print(f"Réponse complète reçue:\n{reponse}", file=sys.stderr)

        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON de la réponse complète : {e}. Réponse reçue:\n{reponse}", file=sys.stderr)
            
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse Gemini : {e}", file=sys.stderr)

    write_groupe(includePLAPath,lstGroupe,saveGroup)
    write_next(pathNext_py)
    copy_pla_default(pathPLADirectory)
    print("\nfin de la génération des exercices\n")
    create_relative_zip_and_cleanup(pathPLADirectory,pathPLADirectory + ".zip")