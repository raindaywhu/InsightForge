"""Clear ChromaDB cache to resolve embedding conflict"""
import sys
import os
import shutil

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Common ChromaDB storage locations
locations = [
    os.path.expanduser("~/.chroma"),
    os.path.expanduser("~/.crewai"),
    os.path.join(os.getcwd(), "chroma_db"),
    os.path.join(os.getcwd(), ".chroma"),
    os.path.join(os.getcwd(), "db"),
]

print("Searching for ChromaDB storage...")

for loc in locations:
    if os.path.exists(loc):
        print(f"Found: {loc}")
        try:
            shutil.rmtree(loc)
            print(f"  [DELETED] {loc}")
        except Exception as e:
            print(f"  [ERROR] Could not delete: {e}")
    else:
        print(f"Not found: {loc}")

# Also check for chroma.sqlite3
import glob
sqlite_files = glob.glob(os.path.expanduser("~/**/chroma.sqlite3"), recursive=True)
for f in sqlite_files:
    print(f"Found SQLite: {f}")
    try:
        os.remove(f)
        print(f"  [DELETED] {f}")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\nDone! ChromaDB cache cleared.")