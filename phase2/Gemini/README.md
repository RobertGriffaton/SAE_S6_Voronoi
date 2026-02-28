# Générateur de Diagrammes de Voronoï

Cette application génère et affiche des diagrammes de Voronoï à partir d'un ensemble de points 2D. Elle a été conçue pour la SAÉ du semestre 6 (BUT Informatique) avec une architecture MVC, un développement dirigé par les tests (TDD), et une conformité stricte aux principes SOLID.

## Fonctionnalités
- Chargement d'un fichier texte contenant des coordonnées de points.
- Calcul mathématique optimisé via `scipy.spatial.Voronoi`.
- Affichage vectoriel via une interface graphique interactive `Tkinter`.
- Exportation du diagramme aux formats `SVG` et `PNG`.

## Architecture
L'architecture sépare les responsabilités (SRP) :
- **Modèles (`src/models`)** : Représentation immutable du domaine (`Point`, `VoronoiResult`).
- **Utilitaires (`src/utils`)** : Lecture robuste des fichiers (gestion des exceptions).
- **Services (`src/services`)** : Encapsulation de la logique mathématique (`VoronoiGenerator`) et utilisation du patron de conception **Stratégie** pour les exports (`SvgExportStrategy`, `ImageExportStrategy`).
- **Interface Utilisateur (`src/ui`)** : Fenêtre principale `Tkinter` orchestrant les interactions (MVC-like Controller/View).

## Guide d'Installation

1. **Prérequis** : Vous devez avoir Python 3.9+ installé.
2. **Création d'un environnement virtuel** :
   ```bash
   python -m venv .venv
   ```
3. **Activation de l'environnement virtuel** :
   - Sur Windows (PowerShell/CMD) :
     ```bash
     .\.venv\Scripts\activate
     ```
   - Sur Linux / macOS :
     ```bash
     source .venv/bin/activate
     ```
4. **Installation des dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## Guide de Lancement

1. **Générer des points de test** (Optionnel) :
   ```bash
   python generate_test_points.py
   ```
   *Ce script générera un fichier `test_points.txt` valide contenant 30 points.*

2. **Lancer l'application** :
   ```bash
   python -m src.ui.main_window
   ```
   - Cliquez sur **"Load Points File"** et sélectionnez le fichier texte (ex: `test_points.txt`).
   - Le diagramme s'affiche sur la zone de dessin.
   - Cliquez sur **"Export SVG"** ou **"Export Image"** pour sauvegarder le résultat.

## Suite de Tests (TDD)
L'application est entièrement couverte par des tests unitaires (Pattern AAA).
Pour lancer les tests :
```bash
pytest tests/
```
