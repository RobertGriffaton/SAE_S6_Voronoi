# Voronoi Tk Application

Application Python pour charger des points `x,y`, calculer un diagramme de Voronoi, afficher le résultat avec Tkinter et exporter en SVG/PNG.

Le rendu affiche des cellules Voronoï colorées et remplies, avec arêtes et sites visibles.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,image]
```

Si vous ne souhaitez pas l'export PNG, vous pouvez installer seulement:

```bash
pip install -e .[dev]
```

## Exécuter l'application

```bash
python -m voronoi_app.main
```

## Exécuter les tests

```bash
pytest -q
```

## Format du fichier d'entrée

Une coordonnée par ligne:

```text
10,20
30.5,40
-2,15
```

Exemple prêt à l'emploi: `examples/points_sample.txt`
