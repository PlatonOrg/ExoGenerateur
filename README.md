# ExoGenerateur
Repository for generating exercises with the help of AI

# Installation
Clone the repository and run the install script :

```bash
git clone https://github.com/PlatonOrg/ExoGenerateur.git
cd ExoGenerateur
./bin/install.sh
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
generate [name of the composant]
create [name of a componant]


# Technical ducumentation

## Codebase Structure
- default : default files needed to generate the exercice
- modeles : folder with every componant that can be use to generate an exercice
- src     : folder for python files needed to run the interface
- main.py : main file to run the interface
