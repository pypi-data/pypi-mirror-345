# 🎯 Smart Focus AI

[![CI](https://github.com/<Seiiferu/SmartFocusAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Seiiferu/SmartFocusAI/actions)  
[![codecov](https://codecov.io/gh/Seiiferu/SmartFocusAI/branch/master/graph/badge.svg?token=FCA84XJMP7)](https://codecov.io/gh/Seiiferu/SmartFocusAI)
[![PyPI](https://img.shields.io/pypi/v/SmartFocusAI.svg)](https://pypi.org/project/SmartFocusAI)  
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/Seiiferu/SmartFocusAI/app.py)

---

## 📖 Table of Contents

1. [Introduction](#-introduction)  
2. [Architecture](#-architecture)  
3. [Project Structure](#-project-structure)  
4. [Libraries](#-libraries)  
5. [Installation](#-installation)  
6. [Usage](#-usage)  
7. [Deployment](#-deployment)  
8. [Tests & CI](#-tests--ci)  
9. [Contributing](#-contributing)  
10. [License](#-license)

---

## 🧐 Introduction

**Smart Focus AI** est une application Python qui utilise votre webcam pour détecter en temps réel si vous êtes **focalisé·e** ou **distrait·e**, en combinant :

- la direction du regard (gaze) via MediaPipe FaceMesh  
- la détection de frappe clavier (TypingActivityDetector)  
- le comptage de clignements d’yeux (BlinkDetector)  

À la fin de chaque session, elle génère un rapport **CSV** et un résumé **PDF** de vos périodes de focus, typing et distraction.

---

## 🚧 Architecture

Voici un diagramme Mermaid qui présente les composants principaux et leurs interactions :

```mermaid
flowchart LR
  A[Webcam / OpenCV] --> B[FaceMeshDetector]
  B --> C[GazeEstimator]
  B --> D[BlinkDetector]
  E[TypingActivityDetector] --> F[FocusManager]
  C --> F
  D --> F
  F --> G[Streamlit Transformer]
  G --> H[Streamlit UI]
  F --> I[Logger → CSV / PDF]

```

- FaceMeshDetector extrait landmarks faciaux
- GazeEstimator et BlinkDetector traitent ces landmarks
- TypingActivityDetector écoute les frappes clavier
- FocusManager fusionne tous les signaux en un état Focused/Distracted
- Streamlit Transformer superpose l’overlay sur la vidéo
- Logger écrit les données et génère le rapport

## 📁 Projet Structure

- **.github**: GitHub Actions workflows (CI, deploy…).
- **env/**: Virtual env.
- **logd**: CSV datés générés par session.
- **notebooks/**: Notebooks for data exploration.
- **src/**: Main script to run pipeline & Source code (gaze & blink module, objetc & action module, display & overlay, logic).
- **tests/**: Tests & Debug tests & Units/Integrations tests.
- **requirements.txt**: Dependencies pip.
- **setup.py**: Packaging setuptools.
- **.gitignore**: Ignore venv, __pycache__, etc.
<!-- - **streamlit.py**: Streamlit application for interactive display. -->

---

## 📦 Libraries

* **mediapipe** → FaceMesh & iris.
* **numpy** → For mathematical operations and numerical array processing.
* **matplotlib** → For creating classic visualizations (charts, scatter plots, etc.) for PDF.
* **scikit-learn** → ML classifier.
* **pandas** → Logs, analysis, graph.
* **jupyterlab** → For developping and testing your analysis interactively in notebooks.
* **imutils** → OpenCV utilitaires.
* **pytestd** → For unit tests.
* **pynput** → Keyboard/Typing captation(≥ Py 3.10).
<!-- * **fpdf** → For generating PDF reports. -->
* **opencv-python** → Captur & video treatment.
* **pytest** → Units tests.
* **streamlit-webrtc** → WebRTC interface.
* **streamlit** (optional) → For creating an interactive website.
* **pyobjc-framework-AVFoundation** (optional) → popup for MacOS camera persmission.

---

## ⚙️ Installation

1. To clone the repo, run :
```bash
git clone https://github.com/Seiiferu/SmartFocusAI.git
cd smart_focus_ai
```

2. Create and activate Python 3.10+ environment, run :
```bash
python3.10 -m venv env
source env/bin/activate
```

3. Install the idependencies :
```bash
   pip install -r requirements.txt
```

4. Install editable mode :
From the root project, instal the package in development mode by running :
```bash
pip install -e 
```

## 🚀 Usage
<!-- Run to complete the pipeline and generate the visualizations :  -->

1. Run the main script :
```bash
    python main.py
```

2. Web inteface (Streamlit) :
```bash
   streamlit run src/streamlit_app.py
```

---

## ☁️ Deployment



---

## ✅  Tests & CI

In local, execute : :
```bash
pytest --cov=src --cov-report=term-missing
```

---


MIT © 2025 [GeeksterLab]