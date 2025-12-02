"""
Script to download FaceNet model for face recognition
"""
import os
import urllib.request
import sys

def download_facenet_model():
    """Download FaceNet Keras model"""
    
    print("=" * 70)
    print("FaceNet Model Downloader")
    print("=" * 70)
    
    # Model URL (from keras-facenet GitHub releases)
    # Alternative mirror: drive.google.com/uc?export=download&id=1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn
    model_url = "https://drive.google.com/uc?export=download&id=1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn"
    
    # Save path
    save_path = os.path.join(os.path.dirname(__file__), 'facenet_keras.h5')
    
    if os.path.exists(save_path):
        print(f"✓ FaceNet model already exists at: {save_path}")
        response = input("Do you want to re-download? (y/n): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return
        print("Re-downloading...")
    
    print(f"\nDownloading FaceNet model from:")
    print(f"{model_url}")
    print(f"\nSaving to: {save_path}")
    print("\nThis may take a few minutes (file size: ~90 MB)...")
    print("-" * 70)
    
    try:
        def progress_hook(count, block_size, total_size):
            """Show download progress"""
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rProgress: [{'=' * (percent // 2)}{' ' * (50 - percent // 2)}] {percent}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(model_url, save_path, progress_hook)
        print("\n" + "-" * 70)
        print("✓ Download completed successfully!")
        print(f"✓ Model saved to: {save_path}")
        print("\n" + "=" * 70)
        print("Next steps:")
        print("1. Restart your backend server (python app.py)")
        print("2. The system will automatically use FaceNet for recognition")
        print("3. Delete old students and re-register with new embeddings")
        print("=" * 70)
        
    except Exception as e:
        print("\n✗ Error downloading model: {e}")
        print("\nAlternative download method:")
        print("1. Manually download from:")
        print("   https://drive.google.com/file/d/1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn/view?usp=sharing")
        print("   OR")
        print("   https://github.com/serengil/deepface_models/releases/download/v1.0/facenet_keras_weights.h5")
        print(f"2. Place the file in: {os.path.dirname(__file__)}")
        print("3. Rename it to: facenet_keras.h5")

if __name__ == "__main__":
    download_facenet_model()
