import cv2
import numpy as np
from tensorflow.keras.models import load_model

class TomatoAnalyzer:
    def __init__(self, model_path='tomato_model.h5'):
        """Initialize the TomatoAnalyzer with a trained model."""
        self.model = load_model(model_path)
        
    def detect_tomatoes(self, image):
        """Detect tomatoes in image using color detection."""
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for red/reddish tomatoes
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # Create and combine masks
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.add(mask1, mask2)
        
        # Noise reduction
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours
        return [cnt for cnt in contours if cv2.contourArea(cnt) > 500]

    def preprocess_for_model(self, image):
        """Prepare an image for model prediction."""
        processed = cv2.resize(image, (224, 224))
        processed = processed / 255.0
        processed = np.expand_dims(processed, axis=0)
        return processed

    def analyze_image(self, image):
        """Analyze image and return marked image with results."""
        marked_image = image.copy()
        tomato_contours = self.detect_tomatoes(image)
        
        results = []
        for contour in tomato_contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract and process tomato ROI
            tomato_roi = image[y:y+h, x:x+w]
            processed_roi = self.preprocess_for_model(tomato_roi)
            
            # Make prediction
            prediction = self.model.predict(processed_roi)[0][0]
            
            # Determine label and color
            label = "Reif" if prediction > 0.5 else "Unreif"
            color = (0, 255, 0) if prediction > 0.5 else (0, 0, 255)
            confidence = prediction if prediction > 0.5 else 1 - prediction
            
            # Draw rectangle and label
            cv2.rectangle(marked_image, (x, y), (x + w, y + h), color, 2)
            label_text = f"{label} ({confidence*100:.1f}%)"
            cv2.putText(marked_image, label_text, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            results.append({
                'label': label,
                'confidence': confidence,
                'position': (x, y, w, h)
            })
        
        return marked_image, results