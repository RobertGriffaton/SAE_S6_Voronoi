# Voronoi Diagram Generator

Application Python complète de génération de diagrammes de Voronoï avec interface graphique Tkinter.

## Table des matières

- [Description](#description)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Format de fichier d'entrée](#format-de-fichier-dentrée)
- [Exports supportés](#exports-supportés)

## Description

Cette application génère des diagrammes de Voronoï à partir d'un ensemble de points en entrée. Elle offre :

- Lecture de fichiers de points au format `x,y`
- Calcul du diagramme de Voronoï via l'algorithme de Fortune (complexité O(n log n))
- Visualisation interactive via Tkinter
- Export aux formats SVG et images (PNG, JPEG, etc.)

### Choix de l'algorithme

L'algorithme de **Fortune** (sweep line) est utilisé via `scipy.spatial.Voronoi` pour les raisons suivantes :

- **Complexité optimale** : O(n log n) vs O(n²) pour les approches naïves
- **Robustesse** : Implémentation bien testée et optimisée
- **Efficacité** : Gestion efficace des régions infinies via l'ajout de points lointains

## Architecture

Le projet suit les principes **SOLID** et **Clean Code** :

```
voronoi_app/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Data models (Point, VoronoiCell, BoundingBox, VoronoiDiagram)
│   ├── file_parser.py           # Input file parsing
│   ├── voronoi_calculator.py    # Voronoi computation (Fortune's algorithm)
│   ├── exporters.py             # Export strategies (SVG, Image)
│   └── gui.py                   # Tkinter graphical interface
├── tests/
│   ├── test_models.py           # Tests for data models
│   ├── test_file_parser.py      # Tests for file parser
│   ├── test_voronoi_calculator.py # Tests for Voronoi computation
│   ├── test_exporters.py        # Tests for exporters
│   └── test_integration.py      # Integration tests
├── examples/
│   ├── points.txt               # Example input file
│   └── random_points.txt        # Random points example
├── main.py                      # CLI entry point
├── requirements.txt             # Dependencies
├── pyproject.toml              # Project configuration
└── README.md                    # This file
```

### Design Patterns utilisés

1. **Strategy Pattern** : Pour les exporters (SVGExporter, ImageExporter)
   - Permet d'ajouter facilement de nouveaux formats d'export
   - Interface commune `Exporter` avec méthode `export()`

2. **Factory Pattern** : `ExporterFactory`
   - Crée l'exporter approprié selon l'extension du fichier
   - Facilite l'extension avec de nouveaux formats

3. **Single Responsibility** : Chaque classe a une responsabilité unique
   - `PointFileParser` : lecture de fichiers uniquement
   - `VoronoiCalculator` : calcul uniquement
   - `VoronoiCanvas` : affichage uniquement

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou extraire le projet** :
```bash
cd voronoi_app
```

2. **Créer un environnement virtuel** (recommandé) :
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel** :

Sur Linux/macOS :
```bash
source venv/bin/activate
```

Sur Windows :
```bash
venv\Scripts\activate
```

4. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

### Dépendances

- `scipy>=1.11.0` - Calcul scientifique (algorithme de Voronoï)
- `numpy>=1.24.0` - Manipulation de tableaux
- `Pillow>=10.0.0` - Export d'images
- `pytest>=7.4.0` - Framework de test (développement)
- `pytest-cov>=4.1.0` - Couverture de test (développement)

## Utilisation

### Lancer l'interface graphique

```bash
python main.py
```

ou explicitement :

```bash
python main.py --gui
```

### Mode ligne de commande

**Générer un diagramme SVG** :
```bash
python main.py -i examples/points.txt -o output.svg
```

**Générer une image PNG** :
```bash
python main.py -i examples/points.txt -o output.png
```

**Spécifier les dimensions** :
```bash
python main.py -i examples/points.txt -o output.png --width 1200 --height 800
```

**Afficher l'aide** :
```bash
python main.py --help
```

### Utilisation de l'interface graphique

1. **Charger un fichier** : Cliquer sur "Load Points from File..." et sélectionner un fichier `.txt`
2. **Générer le diagramme** : Cliquer sur "Generate Voronoi Diagram"
3. **Exporter** : Utiliser "Export as SVG..." ou "Export as Image..."

## Tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter avec couverture

```bash
pytest --cov=src --cov-report=html
```

### Exécuter un fichier de test spécifique

```bash
pytest tests/test_models.py
```

### Exécuter avec verbose

```bash
pytest -v
```

### Structure des tests

Les tests suivent le pattern **AAA** (Arrange, Act, Assert) et la convention de nommage :
```python
def test_should_<expected>_given_<condition>(self) -> None:
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

## Format de fichier d'entrée

Le fichier d'entrée doit contenir un point par ligne au format :
```
x,y
```

**Exemple** :
```
# Commentaire
0,0
1,0
0.5,0.866
-2,3
```

**Règles** :
- Une ligne = un point
- Format : `x,y` (coordonnées séparées par une virgule)
- Les lignes commençant par `#` sont des commentaires
- Les lignes vides sont ignorées
- Les espaces autour des coordonnées sont ignorées
- Les nombres décimaux utilisent le point (`.`)

## Exports supportés

| Format | Extension | Description |
|--------|-----------|-------------|
| SVG | `.svg` | Vectoriel, éditable |
| PNG | `.png` | Image raster avec transparence |
| JPEG | `.jpg`, `.jpeg` | Image raster compressée |
| BMP | `.bmp` | Image raster non compressée |
| GIF | `.gif` | Image raster (256 couleurs) |
| TIFF | `.tiff` | Image haute qualité |
| WebP | `.webp` | Format moderne compressé |

## Architecture détaillée

### Module `models.py`

- **Point** : Représentation immuable d'un point 2D avec validation
- **VoronoiCell** : Cellule avec point germe et sommets du polygone
- **BoundingBox** : Boîte englobante avec marges
- **VoronoiDiagram** : Diagramme complet avec métadonnées

### Module `voronoi_calculator.py`

- **VoronoiCalculator** : Calcul via `scipy.spatial.Voronoi`
- Gestion des régions infinies par ajout de points lointains
- Clipping Sutherland-Hodgman pour limiter au bounding box

### Module `file_parser.py`

- **PointFileParser** : Parseur avec validation stricte
- Exceptions spécifiques pour chaque type d'erreur
- Support des commentaires et lignes vides

### Module `exporters.py`

- **Exporter** (ABC) : Interface abstraite
- **SVGExporter** : Export vectoriel avec styles CSS
- **ImageExporter** : Export raster via Pillow
- **ExporterFactory** : Création d'exporters par extension

### Module `gui.py`

- **VoronoiCanvas** : Canvas Tkinter personnalisé
- **VoronoiApp** : Application principale avec contrôles
- Gestion des événements et export via boîtes de dialogue

## Qualité du code

### Principes appliqués

- **KISS** : Chaque ligne a une raison d'être
- **DRY** : Pas de duplication de code
- **SOLID** : Responsabilité unique, ouvert/fermé, etc.
- **Type hints** : Typage complet pour la maintenabilité
- **Docstrings** : Documentation complète des modules, classes et méthodes

### Constantes nommées

Aucun "magic number" - toutes les valeurs sont des constantes :
```python
DEFAULT_BOUNDING_BOX_MARGIN: float = 0.1
MIN_POINTS_REQUIRED: int = 2
DEFAULT_WIDTH: int = 800
# etc.
```

### Gestion des erreurs

Exceptions spécifiques pour chaque cas :
- `FileParserError` : Erreurs de parsing
- `InvalidFormatError` : Format invalide
- `EmptyFileError` : Fichier vide
- `ExportError` : Erreurs d'export

## Auteur

Projet réalisé dans le cadre de la SAÉ S6 - BUT Informatique

## Licence

MIT License
