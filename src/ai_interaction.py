"""
Fichier pour interragir avec l'ia
"""
from datetime import datetime
import json
import os
import google.generativeai as genai

from dotenv import load_dotenv

GEMINI_API_KEY = None
IA_MODEL = None
MODEL_TYPE = 'gemini-1.5-flash'


########## initialisation et requête

def init_ia():
    global GEMINI_API_KEY
    global IA_MODEL
    load_dotenv()

    # Récupère la clé API Gemini
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not GEMINI_API_KEY:
        print("Erreur : La clé API Gemini (GOOGLE_API_KEY) n'est pas configurée dans votre fichier .env.")
        print("Veuillez consulter la documentation pour savoir comment l'obtenir et la configurer.")
        exit()

    # Configure l'accès à l'API
    genai.configure(api_key=GEMINI_API_KEY)

    # Initialise le modèle
    try:
        IA_MODEL = genai.GenerativeModel(MODEL_TYPE)
        print(f"Modèle Gemini {MODEL_TYPE} initialisé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du modèle Gemini : {e}")
        print("Vérifiez votre connexion internet et votre clé API.")
        exit()

def ask_gemini(prompt):
    """
    Envoie la question (prompt) au modèle Gemini et retourne sa réponse au format str.
    En cas d'erreur renvoie ""
    """
    if not prompt.strip():
        return "Erreur : La question à poser à l'IA ne peut pas être vide."

    try:
        reponseBrut = IA_MODEL.generate_content(prompt)

        if reponseBrut and reponseBrut.text:
            reponse = reponseBrut.text.strip()

            if reponse.startswith('```json') and reponse.endswith('```'):
                return reponse[len('```json\n'):-len('\n```')].strip()

            elif reponse.startswith('```') and reponse.endswith('```'): #juste '```'
                 return reponse[len('```\n'):-len('\n```')].strip()
            else:
                return reponse # Pas de balises
        else:
            print(f"L'IA n'a pas pu générer une réponse textuelle valide. Raison(s) de blocage : {reponseBrut.prompt_feedback}")
            return ""

    except Exception as e:
        print(f"Une erreur est survenue lors de la communication avec l'IA : {e}")
        return ""

######### glossaire

def extract_glossaire(fileContent):
    """
    Extrait le glossaire à partir d'un texte
    Renvoie la réponse de Gemini Json au format str
    """
    langueDefinition = "Anglais"
    prompt = {
        "model": MODEL_TYPE,
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert linguistique et terminologue. Ton rôle est d'extraire un glossaire complet à partir du texte fourni, en respectant le format JSON spécifié. Pour chaque terme, inclus une définition concise et, si pertinent, des traductions. La définition doit être dans la **" + langueDefinition + "**. L'objet 'translation' DOIT contenir une entrée pour le 'français' et une pour l''anglais'. Si le 'term' est déjà dans la langue de traduction spécifiée pour cet objet, tu peux laisser la valeur vide pour cette traduction ou répéter le 'term' si c'est un mot universellement reconnu. Sinon, fournis la traduction appropriée. Toutes les langues présentes dans l'objet 'translation' pour un terme DOIVENT être présentes dans l'objet 'translation' de TOUS les autres termes du glossaire, même si leur valeur est une chaîne vide."
            },
            {
                "role": "user",
                "content": "Extrais un glossaire du texte suivant. La langue de définition souhaitée est le **" + langueDefinition + "**. Le format doit être:\n\n```json\n[\n    {\n        \"term\": \"\",\n        \"definition\": \"\",\n        \"translation\": {\"français\": \"\", \"anglais\": \"\"} \n    }\n]\n```\n\nVoici le texte du fichier:\n\n" + fileContent
            }
        ],
        "response_format": { "type": "json_object" },
        "temperature": 0.1
    }
    return ask_gemini(json.dumps(prompt))

def generate_glossaire(infoGeneral):
    """
    génére un glossaire
    """
    sujet = "matière : " + infoGeneral["matiere"]
    if infoGeneral["theme"] is not None:
        sujet += " , thème : " + infoGeneral["theme"]
        
    if infoGeneral["indicationSup"] is not None:
        sujet += " , indications supplémentaires : " + infoGeneral["indicationSup"]
    langueDefinition = infoGeneral["matiere"]
    langueTraduction = "Francais" 
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
                3.  Des traductions pour ce terme. L'objet 'translation' DOIT toujours inclure les clés '{langueDefinition}' et '{langueTraduction}'. Si un terme est déjà dans l'une de ces langues, la valeur de sa traduction pour cette langue peut être le terme lui-même (si universellement reconnu) ou une chaîne vide. Pour les autres cas, fournis la traduction appropriée.

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
    "temperature": 0.3 # Une température légèrement plus élevée peut aider à générer plus de termes variés, tout en restant structuré.
    }
    
    return ask_gemini(json.dumps(prompt))
######### prompt

def find_exo_prompt():
    """
    Cherche les fichier prompt.txt dans modeles et tout ses sous-repertoire
    Renvoie la liste des chemins vers les fichiers "prompt.txt"
    """
    directory = "modeles"
    paths = []
    fileName = "prompt.txt"

    if not os.path.exists(directory):
        print(f"Erreur : Le répertoire '{directory}' n'existe pas.")
        return paths

    for root, _, files in os.walk(directory):
        if fileName in files:
            relative_path = os.path.relpath(os.path.join(root, fileName), directory)
            paths.append(relative_path)
            
    return paths

def create_dated_output_folder(matiere):
    directory = "./output"
    os.makedirs(directory, exist_ok=True)

    now = datetime.now()
    
    # Format du nom de dossier : [matiere]_AAAA-MM-JJ_HH-MM-SS
    folderName = f"{matiere.replace(' ', '_')}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

    newFolder = os.path.join(directory, folderName)

    try:
        os.makedirs(newFolder)
        print(f"Dossier pour l'exercice créé : '{newFolder}'")
        return newFolder
    except FileExistsError:
        print(f"Attention : Le dossier '{newFolder}' existe déjà. Utilisation du dossier existant.")
        return ""
    except Exception as e:
        print(f"Erreur inattendue lors de la création du dossier : {e}")
        return ""

######## 2 prompts par question à l'ia

def generalPrompt(glossaire, generalInfo):
    """
    Génère le prompt général pour la création d'exercices regroupés.
    Ce prompt est conçu pour être complété dynamiquement avec les instructions spécifiques
    de chaque exercice par la fonction generate_data.
    """
    langue = generalInfo.get('langueInst', 'Français')
    matiere = generalInfo.get('matiere', 'None')
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

def generate_data(glossaire, generalInfo):
    """
    Génère les données pour tous les exercices en regroupant les prompts deux par deux.
    """
    lstPrompt = find_exo_prompt()
    savePrompt = 1

    if not lstPrompt:
        print("Aucun fichier 'prompt.txt' trouvé dans le répertoire 'modeles'. Aucune donnée générée.")
        return

    basePrompt = generalPrompt(glossaire, generalInfo)
    print("Prompt général base complété.")

    pathDirectory = create_dated_output_folder('Exercice')

    if savePrompt > 0:
        os.makedirs(pathDirectory + '/data', exist_ok=True)
        with open(pathDirectory + '/data/glossaire.txt', 'w', encoding='utf-8') as f:
            f.write(glossaire)

    for i in range(0, len(lstPrompt), 2):
        paths = []
        fileContents = []
        fileNames = []

        path1 = lstPrompt[i]
        pathComplete1 = os.path.join("modeles", path1)
        fileName1 = path1.replace(os.sep, '_').replace('_prompt.txt', '')
        paths.append(pathComplete1)
        fileNames.append(fileName1)
        try:
            with open(pathComplete1, 'r', encoding='utf-8') as f:
                fileContents.append(f.read())
        except FileNotFoundError:
            print(f"Erreur: Le fichier '{pathComplete1}' n'a pas été trouvé. Passage au prompt suivant.")
            continue
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier '{pathComplete1}' : {e}")
            continue

        if i + 1 < len(lstPrompt):
            path2 = lstPrompt[i+1]
            pathComplete2 = os.path.join("modeles", path2)
            fileName2 = path2.replace(os.sep, '_').replace('_prompt.txt', '')
            paths.append(pathComplete2)
            fileNames.append(fileName2)
            try:
                with open(pathComplete2, 'r', encoding='utf-8') as f:
                    fileContents.append(f.read())
            except FileNotFoundError:
                print(f"Erreur: Le fichier '{pathComplete2}' n'a pas été trouvé. Traitement du premier prompt seul.")
                pass
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier '{pathComplete2}' : {e}")
                pass


        promptAsk = basePrompt + "\n\n"
        if len(fileContents) == 2:
            promptAsk += "\n---"
            promptAsk += f"\n### Instructions de format et type d'exercice 1 :\n\n{fileContents[0]}"
            promptAsk += "\n---"
            promptAsk += f"\n### Instructions de format et type d'exercice 2 :\n\n{fileContents[1]}"
        elif len(fileContents) == 1:
            promptAsk += "\n---"
            promptAsk += f"\n### Instructions de format et type d'exercice 1 :\n\n{fileContents[0]}" # Changed to '1' for consistency in prompt structure

        try:
            reponse = ask_gemini(promptAsk)
            reponseJson = json.loads(reponse)
            if "exercices" in reponseJson and isinstance(reponseJson["exercices"], list):
                if len(reponseJson["exercices"]) == len(fileNames):
                    for idx, exercise_data in enumerate(reponseJson["exercices"]):
                        exerciceName = f'{pathDirectory}/{fileNames[idx]}.json'
                        try:
                            with open(exerciceName, 'w', encoding='utf-8') as f:
                                json.dump(exercise_data, f, indent=4, ensure_ascii=False)
                            print(f"Exercice '{fileNames[idx]}.json' généré")

                            if savePrompt > 1:
                                outputNameData = f"{pathDirectory}/data/prompt_{fileNames[idx]}.txt"
                                with open(outputNameData, 'w', encoding='utf-8') as f:
                                    f.write(fileContents[idx])

                        except Exception as e:
                            print(f"Erreur lors de l'écriture de l'exercice '{fileNames[idx]}.json' : {e}")
                else:
                    print(f"Erreur : Le nombre d'exercices générés par Gemini ({len(reponseJson['exercices'])}) ne correspond pas au nombre de prompts envoyés ({len(fileNames)})")
                    print("Les exercices générés (le cas échéant) seront sauvegardés avec des noms génériques.")
                    for idx, exercise_data in enumerate(reponseJson["exercices"]):
                        exerciceName = f'{pathDirectory}/mismatch_exo_{fileNames[0]}_{idx}.json' # Use first filename as a hint
                        try:
                            with open(exerciceName, 'w', encoding='utf-8') as f:
                                json.dump(exercise_data, f, indent=4, ensure_ascii=False)
                            print(f"Exercice généré avec nom générique '{exerciceName}'.")
                        except Exception as write_err:
                            print(f"Erreur lors de la sauvegarde générique de l'exercice {idx}: {write_err}")
            else:
                print(f"Erreur : Le format de la réponse est invalide pour les prompts {', '.join(fileNames)}. La clé 'exercices' est manquante ou n'est pas une liste.")
                print(f"Réponse complète reçue:\n{reponse[:500]}...")

        except json.JSONDecodeError as e:
            if savePrompt == 0 :
                os.makedirs(pathDirectory + '/data', exist_ok=True)
            with open(pathDirectory + '/data/erreur.txt', 'w', encoding='utf-8') as f:
                f.write(str(reponse))
            print(f"Erreur de décodage JSON de la réponse complète : {e}. Réponse reçue:\n{reponse}...")
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse Gemini : {e}")
    print("\nfin de la génération des exercices\n")