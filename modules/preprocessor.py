# modules/preprocessor.py
# ============================================================
# DATA PREPROCESSING MODULE
# Cleans and tokenizes text from uploaded study materials.
# ============================================================

import re
import string
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (runs once)
def download_nltk_data():
    """Download all required NLTK datasets."""
    packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger',
                'punkt_tab', 'averaged_perceptron_tagger_eng']
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

download_nltk_data()


def clean_text(text: str) -> str:
    """
    Remove noise from raw text:
    - Extra whitespace and newlines
    - Special characters (keep punctuation for sentence splitting)
    - Numeric-only tokens
    """
    # Replace multiple newlines / tabs with a single space
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()


def tokenize_sentences(text: str) -> list[str]:
    """Split cleaned text into a list of sentences."""
    return sent_tokenize(text)


def tokenize_words(text: str, remove_stopwords: bool = True) -> list[str]:
    """
    Tokenize text into words.
    Optionally removes English stopwords and punctuation.
    """
    words = word_tokenize(text.lower())
    # Remove punctuation tokens
    words = [w for w in words if w not in string.punctuation]

    if remove_stopwords:
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words]

    return words


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract plain text from a PDF file given as bytes.
    Uses PyMuPDF (fitz) if available, falls back to pdfminer.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        return clean_text(' '.join(pages))
    except ImportError:
        pass

    try:
        import io
        from pdfminer.high_level import extract_text as pdfminer_extract
        return clean_text(pdfminer_extract(io.BytesIO(pdf_bytes)))
    except Exception as e:
        return f"[PDF extraction failed: {e}]"


def preprocess(raw_text: str) -> dict:
    """
    Full preprocessing pipeline.
    Returns a dict with cleaned text, sentences, and word tokens.
    """
    cleaned   = clean_text(raw_text)
    sentences = tokenize_sentences(cleaned)
    words     = tokenize_words(cleaned)
    return {
        'cleaned_text': cleaned,
        'sentences':    sentences,
        'words':        words,
    }
