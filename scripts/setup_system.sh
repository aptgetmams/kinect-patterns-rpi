#!/bin/bash

echo "🔧 Configuration système pour Kinect Patterns"

# Vérification privilèges
if [[ $EUID -ne 0 ]]; then
   echo "❌ Ce script doit être exécuté avec sudo"
   exit 1
fi

# Configuration GPU memory
echo "⚙️  Configuration mémoire GPU..."
if ! grep -q "gpu_mem=" /boot/config.txt; then
    echo "gpu_mem=128" >> /boot/config.txt
    echo "✅ Mémoire GPU configurée (128MB)"
else
    sed -i 's/gpu_mem=.*/gpu_mem=128/' /boot/config.txt
    echo "✅ Mémoire GPU mise à jour (128MB)"
fi

# Configuration USB
echo "🔌 Configuration USB..."
if ! grep -q "max_usb_current=1" /boot/config.txt; then
    echo "max_usb_current=1" >> /boot/config.txt
    echo "✅ Courant USB maximal activé"
fi

# Permissions udev pour Kinect
echo "🔑 Configuration permissions Kinect..."
cat > /etc/udev/rules.d/51-kinect.rules << 'EOF'
# Xbox Kinect V1
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666", GROUP="plugdev"

# Webcams génériques
SUBSYSTEM=="usb", ATTRS{bInterfaceClass}=="0e", GROUP="video", MODE="0664"
EOF

udevadm control --reload-rules
udevadm trigger

# Groups utilisateur
echo "👥 Configuration groupes utilisateur..."
usermod -a -G video,plugdev,input pi

# Optimisations performances
echo "🚀 Optimisations performances..."

# Swappiness
echo 'vm.swappiness=10' > /etc/sysctl.d/99-kinect-patterns.conf

# Priorités CPU pour multimedia
cat > /etc/security/limits.d/99-kinect-patterns.conf << 'EOF'
@video soft rtprio 10
@video hard rtprio 15
@video soft nice -10
@video hard nice -10
EOF

echo "✅ Configuration système terminée"
echo "⚠️  Redémarrage recommandé pour appliquer tous les changements"
