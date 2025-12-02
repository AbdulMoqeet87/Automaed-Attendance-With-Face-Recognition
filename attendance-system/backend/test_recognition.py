"""
Utility script to test face recognition functionality
"""

import cv2
from ml_module.face_recognizer import FaceRecognizer
import sys

def test_face_detection(image_path):
    """Test face detection on an image"""
    print(f"Testing face detection on: {image_path}")
    
    recognizer = FaceRecognizer()
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Unable to read image")
        return
    
    # Detect faces
    faces = recognizer.detect_faces(image)
    print(f"Detected {len(faces)} face(s)")
    
    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Save result
    output_path = 'test_detection_result.jpg'
    cv2.imwrite(output_path, image)
    print(f"Result saved to: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_recognition.py <image_path>")
        sys.exit(1)
    
    test_face_detection(sys.argv[1])
