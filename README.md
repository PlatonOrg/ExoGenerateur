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

commande :
generate                        : create all the exercice data
glossaire                       : generate a glossaire 
create [name of a componant]    : create a new folder for a new type of exercice


# Technical documentation

## Codebase Structure
- /default      : default files needed to generate the exercice
- /modeles      : prompt use to generate exercices
- /src          : folder for python files needed to run the interface
- main.py       : main file to run the interface
- /bin          : folder with file needed to install environement 
- /local_file   : folder for local file
- /output       : folder with all generate exercice by yser