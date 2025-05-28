"""Générateur de patterns visuels"""
import numpy as np
import cv2
import random
import math
import colorsys
from .config import *

class Particle:
    def __init__(self, x, y, intensity, pattern_type):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3) * intensity
        self.vy = random.uniform(-3, 3) * intensity
        self.life = 1.0
        self.max_life = 1.0
        self.size = random.uniform(2, 8) * intensity
        self.pattern_type = pattern_type
        self.color = self._generate_color(intensity)
        
    def _generate_color(self, intensity):
        """Génère une couleur selon le type de pattern"""
        if self.pattern_type == 'fire':
            # Feu: rouge-orange-jaune
            r = int(255 * intensity)
            g = int(150 * intensity * random.uniform(0.3, 0.8))
            b = int(50 * intensity * random.uniform(0, 0.3))
            return (b, g, r)  # BGR pour OpenCV
            
        elif self.pattern_type == 'water':
            # Eau: bleu avec variations
            r = int(50 * intensity)
            g = int(150 * intensity * random.uniform(0.5, 1.0))
            b = int(255 * intensity)
            return (b, g, r)
            
        elif self.pattern_type == 'rainbow':
            # Arc-en-ciel: couleur cyclique
            hue = random.uniform(0, 1)
            rgb = colorsys.hsv_to_rgb(hue, 0.8, intensity)
            return (int(rgb[2]*255), int(rgb[1]*255), int(rgb[0]*255))
            
        else:  # stars
            # Étoiles: blanc brillant
            val = int(255 * intensity)
            return (val, val, val)
    
    def update(self):
        """Met à jour la particule"""
        # Mouvement
        self.x += self.vx
        self.y += self.vy
        
        # Comportement selon le pattern
        if self.pattern_type == 'fire':
            self.vy -= 0.2  # Monte vers le haut
            self.vx *= 0.98  # Friction horizontale
            
        elif self.pattern_type == 'water':
            self.vy += 0.15  # Gravité
            if self.y > WINDOW_HEIGHT - 50:  # "Sol"
                self.vy *= -0.3  # Rebond amorti
                
        elif self.pattern_type == 'stars':
            # Scintillement
            self.vx *= 0.95
            self.vy *= 0.95
            
        # Vieillissement
        self.life -= PARTICLE_LIFE_DECAY
        self.size *= PARTICLE_SIZE_DECAY
        
        return self.life > 0 and self.size > 0.5
    
    def draw(self, image):
        """Dessine la particule"""
        x, y = int(self.x), int(self.y)
        size = max(1, int(self.size))
        
        if 0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT:
            # Couleur avec transparence basée sur la vie
            alpha = self.life / self.max_life
            color = tuple(int(c * alpha) for c in self.color)
            
            # Particule principale
            cv2.circle(image, (x, y), size, color, -1)
            
            # Effet de glow pour certains patterns
            if self.pattern_type in ['fire', 'stars'] and size > 2:
                glow_color = tuple(int(c * 0.3) for c in color)
                cv2.circle(image, (x, y), size + 2, glow_color, 2)

class PatternGenerator:
    def __init__(self):
        self.particles = []
        self.current_pattern = 0
        self.pattern_names = PATTERNS
        self.frame_count = 0
        
    def add_particles(self, x, y, intensity):
        """Ajoute des particules à la position donnée"""
        if intensity < 0.1:
            return
            
        pattern_name = self.pattern_names[self.current_pattern]
        num_particles = int(intensity * 10) + 1
        
        for _ in range(min(num_particles, 15)):  # Limite par frame
            # Dispersion autour du point central
            offset_x = random.uniform(-20, 20) * intensity
            offset_y = random.uniform(-20, 20) * intensity
            
            particle = Particle(
                x + offset_x, 
                y + offset_y, 
                intensity, 
                pattern_name
            )
            self.particles.append(particle)
        
        # Limite globale
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:]
    
    def update(self):
        """Met à jour toutes les particules"""
        self.particles = [p for p in self.particles if p.update()]
        self.frame_count += 1
    
    def render(self):
        """Génère l'image finale"""
        # Image de base selon le pattern
        if self.pattern_names[self.current_pattern] == 'fire':
            # Fond sombre avec gradient rouge
            image = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
            image[:, :, 2] = 10  # Légère teinte rouge
        else:
            # Fond noir
            image = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
        
        # Dessiner toutes les particules
        for particle in self.particles:
            particle.draw(image)
        
        # Effet de post-traitement léger
        if len(self.particles) > 50:
            image = cv2.GaussianBlur(image, (3, 3), 0)
        
        return image
    
    def change_pattern(self):
        """Change le pattern actuel"""
        self.current_pattern = (self.current_pattern + 1) % len(self.pattern_names)
        pattern_name = self.pattern_names[self.current_pattern]
        print(f"🎨 Pattern changé: {pattern_name.upper()}")
        
        # Clear particles pour transition nette
        self.particles.clear()
    
    def get_current_pattern_name(self):
        """Retourne le nom du pattern actuel"""
        return self.pattern_names[self.current_pattern]
    
    def reset_particles(self):
        """Supprime toutes les particules"""
        self.particles.clear()
        print("🔄 Particules réinitialisées")
