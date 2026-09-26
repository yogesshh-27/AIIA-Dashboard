"""
Utility script to extract JM_CTRIdb.sqlite from JM_CTRIdb.sqlite.gz during build or startup.
Ensures zero-overhead cold starts and preserves git repository file size limits (< 100 MB).
"""
import os
import sys
import gzip
import shutil
import time

def unpack_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(base_dir, "JM_CTRIdb.sqlite")
    gz_path = os.path.join(base_dir, "JM_CTRIdb.sqlite.gz")
    
    if os.path.exists(sqlite_path) and os.path.getsize(sqlite_path) > 10_000_000:
        size_mb = os.path.getsize(sqlite_path) / (1024 * 1024)
        print(f"[OK] JM_CTRIdb.sqlite already exists ({size_mb:.1f} MB). Skipping decompression.")
        return

    if not os.path.exists(gz_path):
        print(f"[INFO] No compressed database found at {gz_path}. Proceeding with normalized aiia_app.db.")
        return

    gz_size_mb = os.path.getsize(gz_path) / (1024 * 1024)
    print(f"[INFO] Decompressing {gz_path} ({gz_size_mb:.1f} MB) -> {sqlite_path}...")
    t0 = time.time()
    
    tmp_path = sqlite_path + ".tmp"
    try:
        with gzip.open(gz_path, "rb") as f_in, open(tmp_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=1024 * 1024)
            
        os.replace(tmp_path, sqlite_path)
        elapsed = time.time() - t0
        extracted_mb = os.path.getsize(sqlite_path) / (1024 * 1024)
        print(f"[SUCCESS] Extracted JM_CTRIdb.sqlite ({extracted_mb:.1f} MB) in {elapsed:.1f}s.")
    except Exception as exc:
        print(f"[ERROR] Failed to decompress database: {exc}", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    unpack_database()
