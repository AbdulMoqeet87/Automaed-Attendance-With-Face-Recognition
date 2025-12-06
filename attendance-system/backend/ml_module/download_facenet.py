import os
import urllib.request
import sys

def download_facenet_model():
    # Model URL (from keras-facenet GitHub releases)
    model_url = "https://drive.google.com/uc?export=download&id=1pwQ3H4aJ8a6yyJHZkTwtjcL4wYWQb7bn"
    
    save_path = os.path.join(os.path.dirname(__file__), 'facenet_keras.h5')
    
    if os.path.exists(save_path):
        print(f"FaceNet model already exists at: {save_path}")
        response = input("Do you want to re-download? (y/n): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return
        print("Re-downloading...")
    
    print(f"\nDownloading FaceNet model from:")
    print(f"{model_url}")
    print(f"\nSaving to: {save_path}")
    
    try:
        def progress_hook(count, block_size, total_size):
            """Show download progress"""
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rProgress: [{'=' * (percent // 2)}{' ' * (50 - percent // 2)}] {percent}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(model_url, save_path, progress_hook)
        print("\nDownload completed successfully!")
        
    except Exception as e:
        print(f"\nError downloading model: {e}")

if __name__ == "__main__":
    download_facenet_model()
