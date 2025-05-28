# Kinect Patterns Generator pour Raspberry Pi

Générateur de patterns visuels réactifs au mouvement humain utilisant une Kinect V1 sur Raspberry Pi 3B+.

# Prérequis matériels

- Raspberry Pi 3B+ 
- Carte SD 16Go (classe 10)
- Kinect V1 (Xbox 360) + adaptateur secteur
- Hub USB alimenté (recommandé)
- Écran HDMI

# Installation automatique

git clone https://github.com/votre-username/kinect-patterns-rpi.git
cd kinect-patterns-rpi
chmod +x install.sh
sudo ./install.sh

# Démarrage
./start.sh

# Contrôles pendant l'exécution:

Q - Quitter

P - Changer de pattern (Feu/Eau/Arc-en-ciel/Étoiles)

ESPACE - Reset des particules

# Test du matériel
./scripts/test_hardware.sh

# Vérification des logs
journalctl -f -u kinect-patterns

Patterns disponibles
Feu - Particules orange/rouge avec effet de chaleur
Eau - Particules bleues fluides
Arc-en-ciel - Couleurs cycliques
Étoiles - Particules blanches scintillantes

# Performance
Optimisé pour fonctionner à ~30 FPS sur Raspberry Pi 3B+ avec:
Résolution: 640x480
Max 150 particules simultanées
Détection de mouvement temps réel
Structure
src/main.py - Application principale
src/motion_detector.py - Détection de mouvement
src/pattern_generator.py - Génération des patterns
scripts/ - Scripts d'installation et test
