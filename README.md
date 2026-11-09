# CBZ & CBR Comic Compressor

A multi-threaded Python CLI utility to batch compress and optimize `.cbz` and `.cbr` manga/comic archives without downscaling image resolutions.

Re-encodes pages to clean JPEGs using DCT quantization table optimization, significantly reducing archive sizes (often 40%–60% reduction) while preserving full dimensions and line sharpness.

---

## ✨ Features

- **Zero Resolution Loss**: Keeps the original pixel dimensions (e.g. 1280×720 remains 1280×720); only compresses image byte size.
- **Batch Processing**: Point to a single `.cbz`/`.cbr` or an entire directory containing multiple archives.
- **Fast & Multi-threaded**: Compresses pages concurrently across multiple CPU threads.
- **Broad Format Support**: Handles input pages in JPG, PNG, WEBP, BMP, and AVIF.
- **Customizable Quality**: Choose custom JPEG compression quality (1–100) or press Enter for the default (50%).

---

## ⚙️ Requirements

- **Python 3.8+**
- **7-Zip** or **WinRAR** installed on your system (only required if extracting `.cbr` archives).

### Python Dependencies
Install required packages via pip:

```bash
pip install -r requirements.txt
```

*(Or install directly)*:
```bash
pip install Pillow pillow-avif-plugin tqdm patool
```

---

## 🚀 How to Use

### 1. Run with Python
```bash
python compress_cbz.py
```

Follow the interactive prompts:
1. **Enter path**: Paste the path to a specific file or folder containing `.cbz` / `.cbr` files.
2. **Quality**: Enter a number between 1 and 100 (Default: `50`).

### 2. Run via Windows CMD shortcut (Optional)
If you placed `compress_cbz.cmd` in your path or a tools directory:
```cmd
compress_cbz.cmd
```

---

## 📁 Output

All compressed files are saved alongside your source files inside a separate folder:
```text
Source_Folder/
├── Volume_01.cbz
├── Volume_02.cbz
└── Compressed_CBZ/
    ├── Volume_01_opt.cbz
    └── Volume_02_opt.cbz
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
