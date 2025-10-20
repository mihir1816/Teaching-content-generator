# YouTube → Notes (Flask, Pinecone, OpenAI) — Minimal Setup

## 1 Install
```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```
<<<<<<< HEAD

## File Upload extraction endpoint

This project includes a File Upload flow to extract text from uploaded documents and images.

- Endpoint: POST /api/file_upload/upload
- Form field: `files` (multipart/form-data). Can upload multiple files.
- Supported types: .pdf, .docx, .doc, .txt, .png, .jpg, .tiff

Behavior:
- The extractor prefers `docling` when available. If `docling` is not installed,
	it falls back to common libraries (PyPDF2, python-docx, pytesseract).
- Output: JSON with `metadata`, `extraction_method`, and `pages` (per-page text).

Dependency notes:
- Docling is recommended for best results (combined machine text + OCR).
- Before adding Docling, verify compatibility with your environment. If you want me
	to add Docling to `requirements.txt` and install it, say "approve docling" and I'll update the manifest and instructions.

Quick test (PowerShell):

```powershell
# Example using curl in PowerShell to upload a file:
curl -X POST -F "files=@C:/path/to/file.pdf" http://127.0.0.1:5000/api/file_upload/upload
```


=======
>>>>>>> 20f6bdf6d73c22162298f54bfba132a01ce16c5e
