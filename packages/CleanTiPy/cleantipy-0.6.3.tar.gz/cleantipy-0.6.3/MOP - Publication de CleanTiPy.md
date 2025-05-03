# Mode Opératoire - Publication de CleanTiPy

Ce document est une compilation de lignes de commande pour créer et publier le package CleanTiPy

## Création du package

modifier le numéro de version dans pyproject.toml

puis

```bash
cd C:\Users\leiba\Documents\CleanTiPy
py -m build
```

## Installation à partir du package local

Dans l'environnement voulu (par défaut ou virtuel)

```bash
pip install .
```

## Création de la documentation (local)

```bash
cd .\docs\
.\make html 
```

ou

```bash
sphinx-build -M html docs/source docs/build/html
```

## Upload sur Pypi

```bash
py -m twine upload -r pypitest dist/* --verbose
```

Pour spécifier un numéro de version :

```bash
py -m twine upload -r pypi .\dist\cleantipy-0.6.2.* --verbose
```

## GitHub - Release

Aller sur github pour déclarer une nouvelle version (release) et indiquer les changements

## Documentation sur ReadTheDocs

Se connecter après publication d'une nouvelle version et vérifier la compilation
