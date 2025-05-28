"""Détecteur de mouvement unifié Kinect/Webcam"""
import cv2
import numpy as np
import os
from .config import *

def try_import_freenect():
    """Tentative d'import de freenect"""
    try:
        import freenect
        return freenect
    except ImportError:
        return None

class MotionDetector:
    def __init__(self):
        self.motion_center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.motion_intensity = 0.0
        self.background = None
        self.running = False
        
        # Détection du mode
        self.freenect = try_import_freenect()
        self.use_kinect = (KINECT_MODE == 'kinect' and self.freenect is not None)
        
        if self.use_kinect:
            print("🎯 Mode Kinect activé")
        else:
            print("📷 Mode webcam activé")
            self.cap = None
    
    def start(self):
        """Démarre la détection"""
        self.running = True
        
        if self.use_kinect:
            return self._start_kinect()
        else:
            return self._start_webcam()
    
    def _start_kinect(self):
        """Démarrage mode Kinect"""
        try:
            # Test de connexion Kinect
            ctx = self.freenect.init()
            num_devices = self.freenect.num_devices(ctx)
            
            if num_devices == 0:
                print("❌ Aucune Kinect détectée")
                return False
                
            print(f"✅ {num_devices} Kinect(s) détectée(s)")
            self.freenect.shutdown(ctx)
            return True
            
        except Exception as e:
            print(f"❌ Erreur Kinect: {e}")
            return False
    
    def _start_webcam(self):
        """Démarrage mode webcam"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("❌ Impossible d'ouvrir la webcam")
            return False
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialisation du background
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.background = cv2.GaussianBlur(gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
            
        print("✅ Webcam initialisée")
        return True
    
    def update(self):
        """Met à jour la détection de mouvement"""
        if not self.running:
            return
            
        if self.use_kinect:
            self._update_kinect()
        else:
            self._update_webcam()
    
    def _update_kinect(self):
        """Mise à jour avec Kinect"""
        try:
            # Capture des données depth
            depth, _ = self.freenect.sync_get_depth()
            
            # Seuillage pour détecter les objets proches
            mask = (depth < 1000) & (depth > 0)
            
            # Morphologie pour nettoyer
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask.astype(np.uint8) * 255, cv2.MORPH_OPEN, kernel)
            
            # Détection des contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Plus grand contour
                largest = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                
                if area > MIN_CONTOUR_AREA:
                    # Centre de masse
                    M = cv2.moments(largest)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Conversion vers coordonnées d'affichage
                        self.motion_center = (
                            int(cx * WINDOW_WIDTH / 640),
                            int(cy * WINDOW_HEIGHT / 480)
                        )
                        self.motion_intensity = min(area / 50000, 1.0)
                    else:
                        self.motion_intensity *= 0.9  # Décroissance graduelle
            else:
                self.motion_intensity *= 0.9
                
        except Exception as e:
            print(f"⚠️  Erreur Kinect: {e}")
            self.motion_intensity = 0
    
    def _update_webcam(self):
        """Mise à jour avec webcam"""
        if not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Préparation de l'image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
        
        if self.background is None:
            self.background = gray.copy().astype(float)
            return
        
        # Détection de mouvement
        diff = cv2.absdiff(gray, self.background.astype(np.uint8))
        thresh = cv2.threshold(diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=DILATE_ITERATIONS)
        
        # Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            
            if area > MIN_CONTOUR_AREA:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    self.motion_center = (
                        int(cx * WINDOW_WIDTH / 640),
                        int(cy * WINDOW_HEIGHT / 480)
                    )
                    self.motion_intensity = min(area / 20000, 1.0)
            else:
                self.motion_intensity *= 0.95
        else:
            self.motion_intensity *= 0.95
        
        # Mise à jour du background
        cv2.accumulateWeighted(gray, self.background, BACKGROUND_LEARNING_RATE)
    
    def stop(self):
        """Arrête la détection"""
        self.running = False
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
