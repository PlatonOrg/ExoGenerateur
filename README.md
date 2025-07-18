# ExoGenerateur
Repository for generating exercises with the help of AI

# Installation
Clone the repository and run the install script :

```bash
git clone https://github.com/PlatonOrg/ExoGenerateur.git
cd ExoGenerateur
./bin/install.sh # creation of virtual env
```

## Requirements:
- [`Gemini api key`](https://aistudio.google.com/apikey)
- [`pip3`](https://pip.pypa.io/en/stable/installing/)
- [`python >= 3.7`](https://www.python.org/)

# Usage


To start working, activate your virtual environment with:

```bash
source venv/bin/activate 
```

then use 
```bash
python main.py
```

## Commande 
- generate                              : create a activity
- glossaire                             : generate a glossaire 
- addExercie [name of a exercice]       : create a new folder for a new type of exercice

## Create an Activity

1. Launch the script and type generate.
2. Enter all required information. A ZIP file will be created in the ./output folder.
3. Open Platon and create a new Activity.
4. Open the activity in the "Editor".
5. In the "Explorer", import the generated ZIP file.
6. Extract all files from the archive.

You can now remove the ZIP file. If there's an issue in the "Exercices" section (e.g., no exercises have been added), try to close and reopen the editor.

## Information
- In "main.pla" keep all Actions disabled otherwise users may cheat (for "Autre question" and "Solution") or functionality are not implemented.


# Technical documentation

## Codebase Structure
- /default      : default files needed to generate the activity
- /modeles      : prompt use to generate exercices
- /src          : folder for python files needed to run the interface
- main.py       : main file to run the interface
- /bin          : folder with file needed to install environement 
- /local_file   : folder for local file
- /output       : folder with all generate exercice by user