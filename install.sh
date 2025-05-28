#!/bin/bash

set -e

echo "=================================================="
echo "    Installation Kinect Patterns Generator"
echo "=================================================="

# Variables
USER_HOME="/home/pi"
PROJECT_DIR="$USER_HOME/kinect_patterns"
SERVICE_NAME="kinect-patterns"

# Fonction d'erreur
error_exit() {
    echo "❌ Erreur: $1" >&2
    exit 1
}

# Vérification des droits root
if [[ $EUID -ne 0 ]]; then
   error_exit "Ce script doit être exécuté en tant que root (sudo)"
fi

echo "🔄 Mise à jour du système..."
apt update && apt upgrade -y || error_exit "Échec de la mise à jour"

echo "📦 Installation des dépendances système..."
apt install -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    python3-pip \
    python3-numpy \
    python3-opencv \
    libusb-1.0-0-dev \
    libopenblas-dev \
    pkg-config \
    udev \
    || error_exit "Échec de l'installation des dépendances"

echo "🔧 Configuration des permissions USB..."
cat > /etc/udev/rules.d/66-kinect.rules << 'EOF'
# Kinect V1 rules
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666", GROUP="plugdev"
EOF

udevadm control --reload-rules
usermod -a -G plugdev,video pi

echo "📁 Création de la structure du projet..."
mkdir -p "$PROJECT_DIR"/{src,logs}
chown -R pi:pi "$PROJECT_DIR"

echo "📄 Copie des fichiers sources..."
cp -r src/* "$PROJECT_DIR/src/"
cp start.sh "$PROJECT_DIR/"
chmod +x "$PROJECT_DIR/start.sh"
chown -R pi:pi "$PROJECT_DIR"

echo "🚀 Installation du service systemd..."
cp systemd/kinect-patterns.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $SERVICE_NAME

echo "🏗️ Installation de libfreenect..."
cd /opt
if [ -d "libfreenect" ]; then
    rm -rf libfreenect
fi

git clone https://github.com/OpenKinect/libfreenect.git || error_exit "Échec du clone libfreenect"
cd libfreenect
mkdir build && cd build

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_PYTHON3=ON \
    -DPYTHON_EXECUTABLE=/usr/bin/python3 \
    || error_exit "Échec de la configuration cmake"

make -j$(nproc) || error_exit "Échec de la compilation"
make install
ldconfig

# Installation Python bindings
cd ../wrappers/python
python3 setup.py build
python3 setup.py install || echo "⚠️  Bindings Python optionnels échoués - mode webcam sera utilisé"

echo "✅ Installation terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Redémarrez le système: sudo reboot"
echo "2. Connectez la Kinect"
echo "3. Lancez: cd $PROJECT_DIR && ./start.sh"
echo ""
echo "🔧 Services disponibles:"
echo "- Démarrage auto: sudo systemctl start $SERVICE_NAME"
echo "- Logs: journalctl -f -u $SERVICE_NAME"
echo "- Test matériel: ./scripts/test_hardware.sh"
