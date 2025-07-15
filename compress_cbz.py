import os
import shutil
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import patoolib

# Import avif support plugin (auto-registers with Pillow)
try:
    import pillow_avif
except ImportError:
    pass

# ================= DEFAULT SETTINGS =================
MAX_WORKERS = 8
OUTPUT_SUFFIX = "_opt"
# ====================================================

# Added .avif here:
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".avif"}

def compress_single_image(img_path: Path, quality: int):
    """Re-encodes an image to JPEG at the specified quality."""
    try:
        with Image.open(img_path) as img:
            # Convert RGBA/Palette/Grayscale with alpha to RGB for clean JPEG encoding
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            
            temp_out = img_path.with_suffix(".tmp.jpg")
            img.save(temp_out, "JPEG", quality=quality, optimize=True)
            
        # Replace original file with the compressed JPEG
        os.remove(img_path)
        final_path = img_path.with_suffix(".jpg")
        shutil.move(temp_out, final_path)
    except Exception as e:
        print(f"Error compressing {img_path.name}: {e}")

def process_comic_file(comic_path: Path, output_dir: Path, quality: int):
    comic_path = Path(comic_path)
    out_name = f"{comic_path.stem}{OUTPUT_SUFFIX}.cbz"
    final_cbz_path = output_dir / out_name

    print(f"\n[+] Processing: {comic_path.name}")
    orig_size_mb = comic_path.stat().st_size / (1024 * 1024)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Extract archive
        try:
            if comic_path.suffix.lower() == ".cbz":
                with zipfile.ZipFile(comic_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
            else:  # .cbr or other comic formats
                patoolib.extract_archive(str(comic_path), outdir=str(temp_path), verbosity=-1)
        except Exception as e:
            print(f"[-] Failed to extract {comic_path.name}: {e}")
            return

        # 2. Collect all images inside the archive
        image_files = [
            p for p in temp_path.rglob("*")
            if p.suffix.lower() in IMAGE_EXTENSIONS and p.is_file()
        ]

        if not image_files:
            print(f"[-] No valid images found in {comic_path.name}")
            return

        # 3. Multi-threaded batch recompression
        print(f"    Compressing {len(image_files)} pages @ Quality {quality}%...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            list(tqdm(
                executor.map(lambda p: compress_single_image(p, quality), image_files),
                total=len(image_files),
                desc="    Pages"
            ))

        # 4. Repack into clean .cbz
        print(f"    Repacking into {final_cbz_path.name}...")
        with zipfile.ZipFile(final_cbz_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file in sorted(temp_path.rglob("*")):
                if file.is_file():
                    arcname = file.relative_to(temp_path)
                    zip_out.write(file, arcname)

    new_size_mb = final_cbz_path.stat().st_size / (1024 * 1024)
    savings = (1 - (new_size_mb / orig_size_mb)) * 100
    print(f"[✓] Done: {orig_size_mb:.1f}MB → {new_size_mb:.1f}MB ({savings:.1f}% reduction)")

def get_user_quality():
    """Prompts the user for a quality percentage between 1 and 100."""
    while True:
        quality_str = input("Enter JPEG Quality (1-100) [Default: 50]: ").strip()
        if not quality_str:
            return 50  # Default to 50 if user just presses Enter
        
        if quality_str.isdigit():
            val = int(quality_str)
            if 1 <= val <= 100:
                return val
        print("Please enter a valid number between 1 and 100.")

def main():
    # 1. Ask for target path
    user_input = input("Enter path to file or folder containing .cbz/.cbr: ").strip('\"\'')
    if not user_input:
        print("No path provided. Exiting.")
        return

    target = Path(user_input)
    if not target.exists():
        print(f"Path does not exist: {target}")
        return

    # 2. Ask for quality value
    quality = get_user_quality()

    # Collect files
    files_to_process = []
    if target.is_dir():
        files_to_process.extend(target.glob("*.cbz"))
        files_to_process.extend(target.glob("*.cbr"))
    elif target.is_file() and target.suffix.lower() in (".cbz", ".cbr"):
        files_to_process.append(target)

    if not files_to_process:
        print("No .cbz or .cbr files found!")
        return

    # Output directory created beside the input file(s)
    out_dir = files_to_process[0].parent / "Compressed_CBZ"
    out_dir.mkdir(exist_ok=True)

    print(f"\nFound {len(files_to_process)} archive(s). Using Quality: {quality}%")
    for comic in files_to_process:
        process_comic_file(comic, out_dir, quality)

if __name__ == "__main__":
    main()