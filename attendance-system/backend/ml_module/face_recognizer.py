import cv2
import numpy as np
import os

# Try to import keras-facenet
try:
    from keras_facenet import FaceNet
    FACENET_AVAILABLE = True
except ImportError:
    FACENET_AVAILABLE = False
    print("Warning: keras-facenet not available")

class FaceRecognizer:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.facenet_model = None
        self._load_facenet_model()
        self.THRESHOLD = 0.8
         
        
    def _load_facenet_model(self):
        if not FACENET_AVAILABLE:
            raise RuntimeError(
                "keras-facenet is required but not installed.\n"
            )
            
        try:
            print("Loading FaceNet model...")
            cache_folder = os.path.join(os.path.dirname(__file__), 'facenet_cache')
            os.makedirs(cache_folder, exist_ok=True)
            self.facenet_model = FaceNet(cache_folder=cache_folder)
            print("FaceNet model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load FaceNet model: {e}")
    
    def detect_faces(self, image):
        """
        Detect faces in an image using OpenCV
        Returns: List of face regions (x, y, w, h)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces
    
    def generate_embedding(self, face_img):
        if self.facenet_model is None:
            raise RuntimeError("FaceNet model is not loaded. Cannot generate embeddings.")
        
        try:
            face_resized = cv2.resize(face_img, (160, 160))
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            face_batch = np.expand_dims(face_rgb, axis=0)
            
            embeddings = self.facenet_model.embeddings(face_batch)
            embedding = embeddings[0]
            
            # Normalize embedding using L2 normalization
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate FaceNet embedding: {e}")
    
    def find_best_match(self, embedding, known_embeddings):
        if not known_embeddings:
            return None, 0.0
        
        best_match_id = None
        best_score = 0.0
        
        for student_id, stored_embeddings in known_embeddings.items():
            for idx, stored_embedding in enumerate(stored_embeddings):
 
                similarity = np.dot(embedding, stored_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match_id = student_id
        
        #print(f"Best match: {best_match_id} with score {best_score:.4f} (threshold: {self.THRESHOLD})")
        #print(f"Match accepted: {best_score > self.THRESHOLD}\n")
        
        return best_match_id, best_score
    
    def draw_label(self, image, face_coords, label, color=None):
        """
        Draw bounding box and label on face
        Green box with roll number for recognized
        Orange box with "NO MATCH" for unrecognized
        """
        x, y, w, h = face_coords
        
        if color is None:
            color = (0, 255, 0) if label != "NO MATCH" else (0, 165, 255)
        
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        label_y = y - 10
        if label_y - text_height - 10 < 0:  
            label_y = y + h + text_height + 10
        
        cv2.rectangle(
            image,
            (x, label_y - text_height - 5),
            (x + text_width + 10, label_y + baseline),
            color,
            -1  
        )
        
        cv2.putText(
            image,
            label,
            (x + 5, label_y - 5),
            font,
            font_scale,
            (255, 255, 255),
            font_thickness,
            cv2.LINE_AA  # Anti-aliased for smoother text
        )
        
        return image
    
    def detect_and_recognize(self, image_path, known_embeddings):
        """
        Main recognition function 
        Input: 
            - image path to classroom image
            - dict of {student_id: [embeddings]}
        Output:
            - recognized_students: list of recognized student IDs
            - unrecognized: list of unrecognized face images
            - annotated_img: annotated classroom image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")
        
        faces = self.detect_faces(image)
        
        #print(f"\nTotal faces detected: {len(faces)}")

        recognized = []
        unrecognized = []
        annotated_img = image.copy()
        
        for face_num, (x, y, w, h) in enumerate(faces, 1):
            face = image[y:y+h, x:x+w]
            
            embedding = self.generate_embedding(face)
            
            match_id, match_score = self.find_best_match(embedding, known_embeddings)
            
            if match_id and match_score > self.THRESHOLD:
                recognized.append({
                    'student_id': match_id,
                    'confidence': float(match_score)
                })
                annotated_img = self.draw_label(
                    annotated_img,
                    (x, y, w, h),
                    match_id  
                )
            else:
                unrecognized.append(face)
                annotated_img = self.draw_label(
                    annotated_img,
                    (x, y, w, h),
                    "NO MATCH"  
                )
        
        unique_recognized = []
        seen_ids = set()
        for item in recognized:
            if item['student_id'] not in seen_ids:
                unique_recognized.append(item['student_id'])
                seen_ids.add(item['student_id'])
        
        print(f"\nRecognized students: {unique_recognized}")
        
        return {
            'recognized_students': unique_recognized,
            'unrecognized': unrecognized,
            'annotated_img': annotated_img
        }
    
    def generate_embedding_from_bytes(self, img_bytes):
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        faces = self.detect_faces(img)
        
        if len(faces) == 0:
            raise ValueError("No face detected in image")
        
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        
        return self.generate_embedding(face)
