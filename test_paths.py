import os, glob

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

print("Current:", current_dir)
print("Parent:", parent_dir)
print("Files in current:", glob.glob(os.path.join(current_dir, "books_upload_*.json")))
print("Files in parent:", glob.glob(os.path.join(parent_dir, "books_upload_*.json")))
