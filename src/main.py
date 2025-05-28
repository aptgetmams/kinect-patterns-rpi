#!/usr/bin/env python3
"""
Kinect Patterns Generator - Application principale
Générateur de patterns visuels réactifs au mouvement
"""

import cv2
import time
import signal
import sys
from .motion_detector import MotionDetector
from .pattern_generator import PatternGenerator
from .config import *

class KinectPatternsApp:
    def __init__(self):
        self.motion_detector = MotionDetector()
        self.pattern_generator = PatternGenerator()
        self.running = False
        self.fps_counter = 0
        self.fps_time = time.time()
        
        # Gestion du signal d'arrêt
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print("\n🛑 Arrêt demandé...")
        self.running = False
    
    def display_info(self, image):
        """Affiche les informations à l'écran"""
        # FPS
        current_time = time.time()
        if current_time - self.fps_time >= 1.0:
            self.fps_time = current_time
            self.fps_counter = 0
        self.fps_counter += 1
        
        # Texte d'information
        pattern_name = self.pattern_generator.get_current_pattern_name()
        info_text = [
            f"Pattern: {pattern_name.upper()}",
            f"Particules: {len(self.pattern_generator.particles)}",
            f"Intensité: {self.motion_detector.motion_intensity:.2f}",
            f"Mode: {KINECT_MODE.upper()}",
            "",
            "Contrôles:",
            "P - Changer pattern",
            "ESPACE - Reset",
            "Q - Quitter"
        ]
        
        # Affichage du texte
        y_offset = 30
        for line in info_text:
            cv2.putText(image, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                       (255, 255, 255), 1)
            y_offset += 25
    
    def run(self):
        """Boucle principale de l'application"""
        print("🚀 Démarrage Kinect Patterns Generator")
        print(f"📊 Configuration: {WINDOW_WIDTH}x{WINDOW_HEIGHT} @ {TARGET_FPS} FPS")
        
        # Initialisation de la détection de mouvement
        if not self.motion_detector.start():
            print("❌ Impossible d'initialiser la détection de mouvement")
            return False
        
        self.running = True
        frame_time = 1.0 / TARGET_FPS
        last_frame_time = time.time()
        
        print("✅ Application démarrée avec succès")
        print("🎮 Bougez devant la caméra pour générer des patterns!")
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Mise à jour de la détection de mouvement
                self.motion_detector.update()
                
                # Ajout de particules en fonction du mouvement
                if self.motion_detector.motion_intensity > 0.05:
                    x, y = self.motion_detector.motion_center
                    self.pattern_generator.add_particles(
                        x, y, self.motion_detector.motion_intensity
                    )
                
                # Mise à jour des particules
                self.pattern_generator.update()
                
                # Rendu de l'image
                image = self.pattern_generator.render()
                
                # Affichage des informations
                self.display_info(image)
                
                # Indicateur de mouvement
                x, y = self.motion_detector.motion_center
                intensity = self.motion_detector.motion_intensity
                if intensity > 0.05:
                    color = (0, int(255 * intensity), 0)  # Vert
                    cv2.circle(image, (x, y), 20, color, 3)
                
                # Affichage
                cv2.imshow('Kinect Patterns Generator', image)
                
                # Gestion des événements clavier
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q ou Echap
                    break
                elif key == ord('p'):
                    self.pattern_generator.change_pattern()
                elif key == ord(' '):  # Espace
                    self.pattern_generator.reset_particles()
                
                # Contrôle du FPS
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Erreur durant l'exécution: {e}")
        finally:
            self.cleanup()
            
        return True
    
    def cleanup(self):
        """Nettoyage des ressources"""
        print("🧹 Nettoyage en cours...")
        self.running = False
        
        self.motion_detector.stop()
        cv2.destroyAllWindows()
        
        print("✅ Application fermée proprement")

def main():
    """Point d'entrée principal"""
    app = KinectPatternsApp()
    
    try:
        success = app.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
