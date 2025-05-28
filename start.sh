#!/bin/bash

cd "$(dirname "$0")"

echo "🚀 Démarrage Kinect Patterns Generator"

# Vérification des dépendances
python3 -c "import cv2, numpy" || {
    echo "❌ Dépendances manquantes"
    exit 1
}

# Test de la Kinect (optionnel)
if lsusb | grep -i "xbox\|kinect" > /dev/null; then
    echo "✅ Kinect détectée"
    KINECT_MODE="kinect"
else
    echo "⚠️  Kinect non détectée - mode webcam"
    KINECT_MODE="webcam"
fi

# Démarrage
export KINECT_MODE="$KINECT_MODE"
python3 src/main.py
