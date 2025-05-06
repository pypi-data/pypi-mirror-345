import os

def autoimgrenamer(directory, base_name="THA"):
 
    supported_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    files = sorted([f for f in os.listdir(directory) if f.lower().endswith(supported_exts)])

    for i, old_name in enumerate(files):
        new_name = f"{base_name}_{i:04d}.PNG" 
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")