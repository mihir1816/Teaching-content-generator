"""
File extractor service.

Implements the File Upload extraction flow. Prefers Docling when available.
If Docling is not importable at runtime, the code will raise an informative error
so the caller can ask for dependency approval/installation. A minimal fallback
path is provided that attempts to use common libraries if present.

Outputs a structured JSON-like dict with per-page text, metadata and method used.
"""
import os
import tempfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

try:
    import docling
    DOCLING_AVAILABLE = True
except Exception:
    DOCLING_AVAILABLE = False

try:
    from langdetect import detect as _detect_lang
except Exception:
    _detect_lang = None


def _detect_language(text: str):
    if not text or not _detect_lang:
        return None
    try:
        return _detect_lang(text)
    except Exception:
        return None


def _save_file_to_temp(file_storage):
    """Save a Flask FileStorage to a temporary file and return the path.

    Caller should remove the file when done.
    """
    suffix = Path(file_storage.filename).suffix or ""
    tmp_dir = tempfile.mkdtemp(prefix="file_upload_")
    tmp_path = os.path.join(tmp_dir, f"upload{suffix}")
    file_storage.save(tmp_path)
    return tmp_path, tmp_dir


def _build_output(filename, file_path, pages_texts, method):
    file_stat = Path(file_path).stat()
    full_text = "\n\n".join([p.get("text", "") for p in pages_texts if p.get("text")])
    metadata = {
        "file_name": filename,
        "file_size": file_stat.st_size,
        "file_type": Path(filename).suffix.lower().lstrip('.'),
        "page_count": len(pages_texts),
        "language": _detect_language(full_text),
        "extraction_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    return {
        "metadata": metadata,
        "extraction_method": method,
        "pages": pages_texts,
    }


def _extract_with_docling(file_path):
    """Attempt extraction using Docling. The Docling API surface may vary
    between versions so we try a few common entry points and fall back with
    an informative exception if none are present.
    """
    if not DOCLING_AVAILABLE:
        raise RuntimeError("Docling is not installed in the environment.")

    # Try a few likely docling APIs.
    last_err = None
    try:
        # Common single-call API (hypothetical): docling.extract_text(path) -> str or list
        if hasattr(docling, "extract_text"):
            out = docling.extract_text(file_path)
            if isinstance(out, list):
                pages = out
            else:
                pages = str(out).split('\f') if isinstance(out, str) else [str(out)]

            pages_texts = []
            for idx, t in enumerate(pages, start=1):
                pages_texts.append({"page_number": idx, "text": t.strip(), "success": True})

            return pages_texts
    except Exception as e:
        last_err = e

    try:
        # Another plausible API: docling.load_document / Document
        if hasattr(docling, "load_document"):
            doc = docling.load_document(file_path)
            # try to read pages attribute or method
            pages = None
            if hasattr(doc, "pages"):
                pages = [getattr(p, "text", str(p)) for p in doc.pages]
            elif hasattr(doc, "get_pages"):
                pages_obj = doc.get_pages()
                pages = [getattr(p, "text", str(p)) for p in pages_obj]

            if pages is not None:
                pages_texts = []
                for idx, t in enumerate(pages, start=1):
                    pages_texts.append({"page_number": idx, "text": str(t).strip(), "success": True})
                return pages_texts
    except Exception as e:
        last_err = e

    try:
        if hasattr(docling, "Document"):
            Doc = getattr(docling, "Document")
            doc = Doc(file_path)
            if hasattr(doc, "pages"):
                pages = [getattr(p, "text", str(p)) for p in doc.pages]
                pages_texts = [{"page_number": i+1, "text": str(t).strip(), "success": True} for i, t in enumerate(pages)]
                return pages_texts
    except Exception as e:
        last_err = e

    # If we reach here, we could not use docling via expected entrypoints.
    logger.exception("Docling import succeeded but extraction API calls failed.")
    raise RuntimeError("Docling is available but extraction failed: %s" % str(last_err))


def process_file_storage(file_storage):
    """Main entrypoint for handling an uploaded Flask FileStorage object.

    Returns a dict matching the structured output defined in the project spec.
    """
    filename = file_storage.filename
    tmp_path = None
    tmp_dir = None
    try:
        tmp_path, tmp_dir = _save_file_to_temp(file_storage)
        ext = Path(filename).suffix.lower()

        # Prefer Docling when available
        if DOCLING_AVAILABLE:
            try:
                pages = _extract_with_docling(tmp_path)
                return _build_output(filename, tmp_path, pages, method="docling")
            except Exception as e:
                # If Docling failed unexpectedly, log and fall back to slower approach
                logger.exception("Docling extraction failed, falling back: %s", str(e))

        # Fallback: try basic extraction using common libraries if installed.
        pages = []
        last_err = None

        # PDF fallback via PyPDF2 (if present)
        if ext in [".pdf"]:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(tmp_path)
                for i, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text() or ""
                        pages.append({"page_number": i+1, "text": text.strip(), "success": True})
                    except Exception as pe:
                        pages.append({"page_number": i+1, "text": "", "success": False, "error": str(pe)})
                return _build_output(filename, tmp_path, pages, method="pdf-pypdf2")
            except Exception as e:
                last_err = e

        # DOCX fallback via python-docx
        if ext in [".docx"]:
            try:
                import docx
                doc = docx.Document(tmp_path)
                full = []
                for p in doc.paragraphs:
                    full.append(p.text)
                text = "\n\n".join(full)
                pages = [{"page_number": 1, "text": text.strip(), "success": True}]
                return _build_output(filename, tmp_path, pages, method="docx-python-docx")
            except Exception as e:
                last_err = e

        # Image fallback via pytesseract
        if ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif"]:
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(tmp_path)
                text = pytesseract.image_to_string(img)
                pages = [{"page_number": 1, "text": text.strip(), "success": True}]
                return _build_output(filename, tmp_path, pages, method="ocr-pytesseract")
            except Exception as e:
                last_err = e

        # Plain text files
        if ext in [".txt"]:
            try:
                with open(tmp_path, 'r', encoding='utf-8', errors='replace') as fh:
                    text = fh.read()
                pages = [{"page_number": 1, "text": text.strip(), "success": True}]
                return _build_output(filename, tmp_path, pages, method="text-plain")
            except Exception as e:
                last_err = e

        # DOC (legacy Word) fallback via textract (if present)
        if ext in [".doc"]:
            try:
                import textract
                text = textract.process(tmp_path)
                # textract.process returns bytes
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='replace')
                pages = [{"page_number": 1, "text": text.strip(), "success": True}]
                return _build_output(filename, tmp_path, pages, method="doc-textract")
            except Exception as e:
                last_err = e

        # If we reach here and no method worked, raise an informative error.
        raise RuntimeError(
            "No extraction method succeeded. Last error: %s.\nTo enable Docling-based extraction add 'docling' to your environment." % str(last_err)
        )

    finally:
        # cleanup temporary dir if created
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
            except Exception:
                pass
