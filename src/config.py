"""Configuration du projet"""
import os

# Mode de fonctionnement
KINECT_MODE = os.environ.get('KINECT_MODE', 'webcam')  # 'kinect' ou 'webcam'

# Paramètres d'affichage
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TARGET_FPS = 30

# Paramètres de détection
MOTION_THRESHOLD = 25
MIN_CONTOUR_AREA = 500
BACKGROUND_LEARNING_RATE = 0.05

# Paramètres des particules
MAX_PARTICLES = 150
PARTICLE_LIFE_DECAY = 0.02
PARTICLE_SIZE_DECAY = 0.995

# Patterns disponibles
PATTERNS = ['fire', 'water', 'rainbow', 'stars']

# Performance
BLUR_KERNEL_SIZE = 21
DILATE_ITERATIONS = 2
