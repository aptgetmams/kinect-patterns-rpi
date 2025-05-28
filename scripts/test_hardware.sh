#!/bin/bash

echo "🔍 Test du matériel Kinect Patterns"

# Test USB
echo "USB Devices:"
lsusb | grep -E "(Xbox|Kinect|045e)" || echo "❌ Kinect non détectée"

# Test Python
echo -e "\n🐍 Test Python:"
python3 -c "
import sys
print(f'Python: {sys.version}')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except:
    print('❌ NumPy manquant')

try:
    import cv2
    print(f'✅ OpenCV: {cv2.__version__}')
except:
    print('❌ OpenCV manquant')

try:
    import freenect
    print('✅ Freenect disponible')
except:
    print('⚠️  Freenect non disponible (mode webcam)')
"

# Test webcam
echo -e "\n📷 Test webcam:"
if ls /dev/video* >/dev/null 2>&1; then
    echo "✅ Périphériques vidéo détectés:"
    ls -la /dev/video*
else
    echo "❌ Aucun périphérique vidéo"
fi

# Test permissions
echo -e "\n👤 Permissions utilisateur:"
groups pi | grep -E "(video|plugdev)" || echo "⚠️  Permissions manquantes"

echo -e "\n✅ Test terminé"
