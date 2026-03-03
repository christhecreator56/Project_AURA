import kagglehub
import shutil
import os

def download_and_store():
    # Identify the base project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, 'data')
    
    # Download latest version from Kaggle
    print("Downloading dataset from Kaggle...")
    path = kagglehub.dataset_download("prasoonkottarathil/polycystic-ovary-syndrome-pcos")
    
    print(f"Dataset downloaded to: {path}")
    
    # Create the local data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created local data directory: {data_dir}")
        
    # Copy all files from the downloaded directory to our project's data directory
    for item in os.listdir(path):
        src = os.path.join(path, item)
        dst = os.path.join(data_dir, item)
        
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
            
    print(f"All files have been stored in: {data_dir}")
    return data_dir

if __name__ == "__main__":
    download_and_store()
