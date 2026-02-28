# 🔷 Voronoï Diagram Viewer

> Application Python de génération et visualisation de diagrammes de Voronoï.  
> Développée dans le cadre de la **SAÉ S6 — BUT Informatique**.  
> **Cette application a été intégralement générée avec l'IA Claude Sonnet 4.6 (Anthropic)**, dans le cadre de la Phase 2 de la SAÉ, qui consiste à comparer le développement assisté par différentes IA génératives.

---

## 📋 Table des matières

1. [Présentation du projet](#-présentation-du-projet)
2. [Architecture du projet](#-architecture-du-projet)
3. [Choix techniques](#-choix-techniques)
4. [Installation](#-installation)
5. [Lancer l'application](#-lancer-lapplication)
6. [Lancer les tests](#-lancer-les-tests)
7. [Utiliser l'interface graphique](#-utiliser-linterface-graphique)
8. [Format du fichier de points](#-format-du-fichier-de-points)
9. [Exporter le diagramme](#-exporter-le-diagramme)
10. [Résultats des tests](#-résultats-des-tests)

---

## 🎯 Présentation du projet

Un **diagramme de Voronoï** est une partition du plan en cellules à partir d'un ensemble de points (appelés *sites* ou *générateurs*). Chaque cellule contient tous les points du plan plus proches du site associé que de tout autre site.

Cette application permet de :
- **Charger** un fichier texte contenant une liste de coordonnées `x,y`
- **Calculer** le diagramme de Voronoï associé
- **Visualiser** le résultat dans une interface graphique Tkinter
- **Exporter** le diagramme au format **SVG** ou **PNG**

---

## 🗂 Architecture du projet

```
voronoi_app/
│
├── main.py                        # Point d'entrée de l'application
├── requirements.txt               # Dépendances Python
├── README.md                      # Ce fichier
│
├── resources/
│   └── sample_points.txt          # Fichier d'exemple de points
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                      # Logique métier (calcul)
│   │   ├── __init__.py
│   │   ├── models.py              # Structures de données : Point, BoundingBox, VoronoiDiagram
│   │   └── voronoi_engine.py      # Moteur de calcul (Facade sur SciPy)
│   │
│   ├── io/                        # Lecture des fichiers d'entrée
│   │   ├── __init__.py
│   │   └── point_file_reader.py   # Parser de fichiers de coordonnées
│   │
│   ├── export/                    # Exporteurs (pattern Strategy)
│   │   ├── __init__.py
│   │   ├── exporter_base.py       # Interface abstraite DiagramExporter
│   │   ├── svg_exporter.py        # Export au format SVG
│   │   └── image_exporter.py      # Export au format PNG (via Pillow)
│   │
│   └── ui/                        # Interface graphique
│       ├── __init__.py
│       ├── app.py                 # Fenêtre principale Tkinter
│       └── canvas_renderer.py     # Rendu du diagramme sur Canvas
│
└── tests/
    ├── __init__.py
    ├── conftest.py                # Fixtures partagées entre les tests
    ├── test_models.py             # Tests des modèles de données
    ├── test_point_file_reader.py  # Tests du parseur de fichiers
    ├── test_voronoi_engine.py     # Tests du moteur de calcul
    └── test_exporters.py          # Tests des exporteurs SVG et PNG
```

---

## ⚙️ Choix techniques

### Algorithme : Fortune via SciPy

Le calcul du diagramme de Voronoï utilise **`scipy.spatial.Voronoi`**, qui encapsule l'algorithme de Fortune via la bibliothèque Qhull.

- **Complexité** : O(n log n) en temps, O(n) en espace
- **Fiabilité** : Qhull est une bibliothèque C éprouvée, sans cas limites bugués
- **Conformité KISS** : évite une implémentation from scratch de ~1000 lignes

### Design Patterns appliqués

| Pattern | Classe(s) | Justification |
|---|---|---|
| **Strategy** | `DiagramExporter` → `SVGExporter`, `ImageExporter` | Ajouter un format (ex: PDF) = 1 nouvelle classe, 0 modification du code existant (OCP) |
| **Facade** | `VoronoiEngine` | Cache les internals SciPy derrière une API claire orientée domaine |
| **Repository** | `PointFileReader` | Isole le parsing de fichier du reste de la logique (SRP) |

### Principes respectés

- **SOLID** — chaque classe a une responsabilité unique, les modules sont ouverts à l'extension
- **KISS** — pas de complexité inutile, chaque ligne a une raison d'être
- **Clean Code** — nommage explicite en anglais, fonctions courtes, pas de Magic Numbers
- **TDD** — les tests couvrent tous les cas nominaux et tous les cas d'erreur
- **AAA** — tous les tests suivent le pattern Arrange / Act / Assert
- **Nommage des tests** — format `Should_<résultat>_given_<contexte>`

---

## 💾 Installation

### Prérequis

- **Python 3.10+** (testé sur Python 3.13)
- **pip**

### Étapes

**1. Télécharger et décompresser le projet**, puis ouvrir un terminal dans le dossier `voronoi_app/` (celui qui contient `main.py`).

**2. Installer les dépendances :**

```powershell
pip install -r requirements.txt
```

Les dépendances installées sont :

| Bibliothèque | Usage |
|---|---|
| `scipy` | Calcul du diagramme de Voronoï (algorithme de Fortune) |
| `numpy` | Manipulation des tableaux de coordonnées |
| `Pillow` | Export PNG de l'image |
| `pytest` | Framework de tests |
| `pytest-mock` | Utilitaires de mock pour les tests |

---

## ▶️ Lancer l'application

Depuis le dossier `voronoi_app/` (celui qui contient `main.py`) :

```powershell
python main.py
```

L'interface graphique s'ouvre. Elle affiche une fenêtre vide avec la barre de menu **File** en haut.

---

## 🧪 Lancer les tests

> ⚠️ Sur Windows, ne pas utiliser `pytest` directement dans PowerShell. Toujours passer par le module Python :

```powershell
python -m pytest tests/ -v
```

Pour obtenir un résumé court (sans détail des tests) :

```powershell
python -m pytest tests/
```

Pour n'exécuter qu'un seul fichier de tests :

```powershell
python -m pytest tests/test_voronoi_engine.py -v
```

Pour n'exécuter qu'un seul test précis :

```powershell
python -m pytest tests/test_voronoi_engine.py::TestVoronoiEngine::test_Should_return_VoronoiDiagram_given_four_valid_points -v
```

---

## 🖥️ Utiliser l'interface graphique

### Étape 1 — Ouvrir un fichier de points

Cliquer sur **File** dans la barre de menu, puis **Open points file…**

![menu File](resources/menu_open.png)

Une boîte de dialogue s'ouvre. Naviguer jusqu'à un fichier `.txt` ou `.csv` contenant des coordonnées (voir la section [Format du fichier de points](#-format-du-fichier-de-points)).

Un fichier d'exemple est disponible dans `resources/sample_points.txt`.

### Étape 2 — Visualiser le diagramme

Une fois le fichier chargé, le diagramme de Voronoï s'affiche dans la fenêtre principale :
- Les **points rouges** représentent les sites (points générateurs)
- Les **lignes bleues** représentent les arêtes du diagramme de Voronoï

Le diagramme s'adapte automatiquement à la taille de la fenêtre. Redimensionner la fenêtre redessine le diagramme.

### Étape 3 — Exporter (optionnel)

Voir la section [Exporter le diagramme](#-exporter-le-diagramme).

### Barre de statut

En bas de la fenêtre, une barre de statut indique en permanence :
- Au démarrage : `Open a points file to get started.`
- Après chargement : `Loaded N point(s) from 'nom_du_fichier.txt'.`
- Après export : `Diagram exported to 'nom_du_fichier.svg'.`

### Raccourcis clavier

| Raccourci | Action |
|---|---|
| `Ctrl + O` | Ouvrir un fichier de points |
| `Ctrl + Q` | Quitter l'application |

---

## 📄 Format du fichier de points

Le fichier doit être un fichier texte (`.txt` ou `.csv`) avec **une coordonnée par ligne**, au format `x,y`.

### Règles

- Séparateur : virgule `,`
- Coordonnées entières ou décimales (point `.` comme séparateur décimal)
- Les coordonnées négatives sont acceptées
- Les **lignes vides** sont ignorées
- Les **lignes commençant par `#`** sont traitées comme des commentaires et ignorées
- Les **espaces autour des valeurs** sont tolérés

### Exemple valide

```
# Exemple de fichier de points
2,4
5.3,4.5
18,29
12.5,23.7
7,10
-3.5,8
```

### Fichier d'exemple fourni

Le fichier `resources/sample_points.txt` est inclus dans le projet et peut être utilisé directement pour tester l'application.

### Erreurs de format

Si le fichier contient une ligne invalide, l'application affiche un message d'erreur indiquant le numéro de ligne concerné. Les cas d'erreur gérés sont :

- Ligne non parseable (ex: `abc,def`)
- Trop de valeurs sur une ligne (ex: `1,2,3`)
- Fichier vide ou ne contenant que des commentaires
- Fichier introuvable

---

## 💾 Exporter le diagramme

Une fois un diagramme chargé et affiché, deux formats d'export sont disponibles via **File** :

### Export SVG

**File → Export as SVG…**

- Format vectoriel, redimensionnable sans perte de qualité
- Idéal pour intégrer dans un rapport, un site web ou une présentation
- Le fichier généré est un SVG standard, ouvrable dans tout navigateur ou éditeur vectoriel (Inkscape, Illustrator…)

### Export PNG

**File → Export as PNG…**

- Format image raster
- Idéal pour un usage dans un document Word, une présentation PowerPoint, etc.
- La résolution dépend de la taille du diagramme (les points très espacés génèrent des images plus grandes)

Dans les deux cas, une boîte de dialogue permet de choisir le nom et l'emplacement du fichier de sortie.

---

## ✅ Résultats des tests

L'application embarque **45 tests unitaires** couvrant l'ensemble des modules :

| Fichier de tests | Nb de tests | Ce qui est testé |
|---|---|---|
| `test_models.py` | 13 | `Point` (création, immuabilité, hashabilité, NaN/infini), `BoundingBox` (dimensions, construction depuis points) |
| `test_point_file_reader.py` | 11 | Parsing valide, lignes vides, commentaires, espaces, erreurs de format, fichier vide, fichier introuvable |
| `test_voronoi_engine.py` | 11 | Diagramme valide, conservation des sites, points insuffisants, doublons, 100 points aléatoires, points colinéaires |
| `test_exporters.py` | 10 | Extension de fichier, création SVG/PNG, XML valide, présence des marqueurs sites et arêtes, image Pillow valide |

**Résultat attendu :**

```
45 passed in ~0.3s
```