import cv2
import numpy as np
import os

# Try to import keras-facenet
try:
    from keras_facenet import FaceNet
    FACENET_AVAILABLE = True
except ImportError:
    FACENET_AVAILABLE = False
    print("Warning: keras-facenet not available. Install with: pip install keras-facenet")

class FaceRecognizer:
    """
    Machine Learning Module
    Handles face detection using OpenCV and recognition using FaceNet
    """
    
    def __init__(self):
        # Face detection using OpenCV Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Load FaceNet model
        self.facenet_model = None
        self._load_facenet_model()
        
        # Recognition threshold
        if self.facenet_model is not None:
            self.THRESHOLD = 0.8  # 80% similarity threshold for FaceNet
        else:
            self.THRESHOLD = 0.6  # Higher threshold for fallback features
        
    def _load_facenet_model(self):
        """Load the FaceNet model for embedding generation"""
        if not FACENET_AVAILABLE:
            raise RuntimeError(
                "keras-facenet is required but not installed.\n"
                "Install with: pip install keras-facenet"
            )
            
        try:
            print("Loading FaceNet model...")
            # Use local cache folder on E: drive to avoid C: drive space issues
            cache_folder = os.path.join(os.path.dirname(__file__), 'facenet_cache')
            os.makedirs(cache_folder, exist_ok=True)
            self.facenet_model = FaceNet(cache_folder=cache_folder)
            print("✓ FaceNet model loaded successfully!")
            print("Using deep learning embeddings for high-accuracy face recognition.")
        except Exception as e:
            raise RuntimeError(f"Failed to load FaceNet model: {e}")
    
    def detect_faces(self, image):
        """
        Detect faces in an image using OpenCV
        Returns: List of face regions (x, y, w, h)
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def generate_embedding(self, face_img):
        """
        Generate face embedding using FaceNet
        Input: face image (cropped face region)
        Output: 128-dimensional embedding vector
        """
        if self.facenet_model is None:
            raise RuntimeError("FaceNet model is not loaded. Cannot generate embeddings.")
        
        try:
            # Preprocess face for FaceNet (160x160)
            face_resized = cv2.resize(face_img, (160, 160))
            
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            # Add batch dimension and get embeddings
            face_batch = np.expand_dims(face_rgb, axis=0)
            
            # Generate embedding using keras-facenet
            embeddings = self.facenet_model.embeddings(face_batch)
            embedding = embeddings[0]
            
            # Normalize embedding (L2 normalization)
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate FaceNet embedding: {e}")
    
    def find_best_match(self, embedding, known_embeddings):
        """
        Find the best matching student for a given embedding
        Returns: (student_id, match_score)
        """
        if not known_embeddings:
            return None, 0.0
        
        best_match_id = None
        best_score = 0.0
        
        print(f"\n=== Matching face ===")
        for student_id, stored_embeddings in known_embeddings.items():
            for idx, stored_embedding in enumerate(stored_embeddings):
                # Calculate cosine similarity
                similarity = np.dot(embedding, stored_embedding)
                
                print(f"Student {student_id} (embedding {idx}): similarity = {similarity:.4f}")
                
                if similarity > best_score:
                    best_score = similarity
                    best_match_id = student_id
        
        print(f"Best match: {best_match_id} with score {best_score:.4f} (threshold: {self.THRESHOLD})")
        print(f"Match accepted: {best_score > self.THRESHOLD}\n")
        
        return best_match_id, best_score
    
    def draw_label(self, image, face_coords, label, color=None):
        """
        Draw bounding box and label on face
        Green box with roll number for recognized
        Orange box with "NO MATCH" for unrecognized
        """
        x, y, w, h = face_coords
        
        # Choose color: Green for recognized, Orange for unrecognized
        if color is None:
            color = (0, 255, 0) if label != "NO MATCH" else (0, 165, 255)
        
        # Draw rectangle around face - make it thicker
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)
        
        # Prepare label text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        
        # Get text size for background
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        # Calculate label position - place above the face
        label_y = y - 10
        if label_y - text_height - 10 < 0:  # If not enough space above, place below
            label_y = y + h + text_height + 10
        
        # Draw filled rectangle as background for text
        cv2.rectangle(
            image,
            (x, label_y - text_height - 5),
            (x + text_width + 10, label_y + baseline),
            color,
            -1  # Filled rectangle
        )
        
        # Draw the label text in white
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
        Main recognition function - implements the ML Module workflow
        Input: 
            - image_path: path to classroom image
            - known_embeddings: dict of {student_id: [embeddings]}
        Output:
            - recognized_students: list of recognized student IDs
            - unrecognized: list of unrecognized face images
            - annotated_img: annotated classroom image
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")
        
        # Detect faces
        faces = self.detect_faces(image)
        
        print(f"\n{'='*50}")
        print(f"Total faces detected: {len(faces)}")
        print(f"{'='*50}")
        
        recognized = []
        unrecognized = []
        annotated_img = image.copy()
        
        # Process each detected face
        for face_num, (x, y, w, h) in enumerate(faces, 1):
            print(f"\n--- Processing Face #{face_num} ---")
            
            # Extract face region
            face = image[y:y+h, x:x+w]
            
            # Generate embedding
            embedding = self.generate_embedding(face)
            
            # Find best match
            match_id, match_score = self.find_best_match(embedding, known_embeddings)
            
            # Check if match is above threshold
            if match_id and match_score > self.THRESHOLD:
                recognized.append({
                    'student_id': match_id,
                    'confidence': float(match_score)
                })
                annotated_img = self.draw_label(
                    annotated_img,
                    (x, y, w, h),
                    match_id  # Only show roll number
                )
            else:
                unrecognized.append(face)
                annotated_img = self.draw_label(
                    annotated_img,
                    (x, y, w, h),
                    "NO MATCH"  # Only show "NO MATCH"
                )
        
        # Remove duplicate recognitions (same student detected multiple times)
        unique_recognized = []
        seen_ids = set()
        for item in recognized:
            if item['student_id'] not in seen_ids:
                unique_recognized.append(item['student_id'])
                seen_ids.add(item['student_id'])
        
        print(f"\n{'='*50}")
        print(f"Summary: {len(unique_recognized)} unique students recognized, {len(unrecognized)} unrecognized faces")
        print(f"Recognized students: {unique_recognized}")
        print(f"{'='*50}\n")
        
        return {
            'recognized_students': unique_recognized,
            'unrecognized': unrecognized,
            'annotated_img': annotated_img
        }
    
    def generate_embedding_from_bytes(self, img_bytes):
        """
        Generate embedding from image bytes (for student registration)
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect face
        faces = self.detect_faces(img)
        
        if len(faces) == 0:
            raise ValueError("No face detected in image")
        
        # Use the first (largest) face
        x, y, w, h = faces[0]
        face = img[y:y+h, x:x+w]
        
        # Generate and return embedding
        return self.generate_embedding(face)
