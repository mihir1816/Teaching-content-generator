"""
File extractor service.
"""
from datetime import datetime
from pathlib import Path
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

# Try importing Docling
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling not available, will use fallback extraction methods")


def process_file_storage(file_storage):
    """
    Extract text from an uploaded file (FileStorage object from Flask).
    
    Returns a dict:
    {
        "metadata": {...},
        "extraction_method": "...",
        "pages": [{"page_number": 1, "text": "...", "success": True}, ...]
    }
    """
    # CRITICAL FIX: Reset file pointer to beginning
    file_storage.seek(0)
    
    filename = file_storage.filename
    logger.info(f"Processing uploaded file: {filename}")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        file_storage.save(tmp.name)
        tmp_path = Path(tmp.name)
    
    try:
        file_size = tmp_path.stat().st_size
        
        # Try Docling first if available
        pages = None
        method = None
        last_err = None
        
        if DOCLING_AVAILABLE:
            try:
                logger.info("Attempting Docling extraction...")
                pages = _extract_with_docling(tmp_path)
                method = "docling"
                logger.info("Docling extraction successful")
            except Exception as e:
                logger.warning(f"Docling extraction failed: {e}")
                last_err = e
        
        # Fallback if Docling failed or unavailable
        if pages is None:
            logger.info("Using fallback extraction methods")
            pages = _fallback_extract(tmp_path)
            method = "fallback"
        
        # Build result
        result = {
            "metadata": {
                "filename": filename,
                "file_size": file_size,
                "page_count": len(pages),
                "processed_at": datetime.now().isoformat()
            },
            "extraction_method": method,
            "pages": pages
        }
        
        logger.info(f"Extraction complete: {len(pages)} pages using {method}")
        return result
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {tmp_path}: {e}")


def _extract_with_docling(file_path: Path):
    """
    Extract using Docling.
    Returns list of page dicts.
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(str(file_path))
        
        pages = []
        if hasattr(result, 'document') and hasattr(result.document, 'pages'):
            for i, page in enumerate(result.document.pages, 1):
                text = page.export_to_markdown() if hasattr(page, 'export_to_markdown') else str(page)
                pages.append({
                    "page_number": i,
                    "text": text,
                    "success": True
                })
        
        if not pages:
            raise RuntimeError("Docling returned no pages")
        
        return pages
        
    except Exception as e:
        logger.error(f"Docling extraction error: {e}")
        raise


def _fallback_extract(file_path: Path):
    """
    Fallback extraction using PyPDF2, python-docx, Pillow, etc.
    Returns list of page dicts.
    """
    pages = []
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == ".pdf":
            pages = _extract_pdf_fallback(file_path)
        elif suffix in [".docx", ".doc"]:
            pages = _extract_docx_fallback(file_path)
        elif suffix == ".txt":
            pages = _extract_txt(file_path)
        elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            pages = _extract_image_ocr(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
            
    except Exception as e:
        logger.error(f"Fallback extraction failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Return empty page with error
        pages = [{
            "page_number": 1,
            "text": "",
            "success": False,
            "error": str(e)
        }]
    
    return pages


def _extract_pdf_fallback(file_path: Path):
    """Extract PDF using PyPDF2."""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    pages = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text() or ""
                pages.append({
                    "page_number": i,
                    "text": text,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Failed to extract page {i}: {e}")
                pages.append({
                    "page_number": i,
                    "text": "",
                    "success": False,
                    "error": str(e)
                })
    
    return pages


def _extract_docx_fallback(file_path: Path):
    """Extract DOCX using python-docx."""
    try:
        import docx
    except ImportError:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")
    
    doc = docx.Document(file_path)
    text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    return [{
        "page_number": 1,
        "text": text,
        "success": True
    }]


def _extract_txt(file_path: Path):
    """Extract plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    
    return [{
        "page_number": 1,
        "text": text,
        "success": True
    }]


def _extract_image_ocr(file_path: Path):
    """Extract text from image using Tesseract OCR."""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise ImportError("PIL/pytesseract not installed. Install with: pip install Pillow pytesseract")
    
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        
        return [{
            "page_number": 1,
            "text": text,
            "success": True
        }]
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return [{
            "page_number": 1,
            "text": "",
            "success": False,
            "error": str(e)
        }]