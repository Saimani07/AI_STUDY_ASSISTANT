# modules/summarizer.py
# ============================================================
# SUMMARIZATION MODULE  –  TextRank algorithm
# Ranks sentences by importance and returns the top-N as a
# concise summary of the uploaded study material.
# ============================================================

import math
from collections import defaultdict

from modules.preprocessor import tokenize_sentences, tokenize_words


# ── Helpers ──────────────────────────────────────────────────

def _build_word_freq(sentences: list[str]) -> dict[str, int]:
    """Count how often each word appears across all sentences."""
    freq: dict[str, int] = defaultdict(int)
    for sent in sentences:
        for word in tokenize_words(sent):
            freq[word] += 1
    return freq


def _sentence_score(sentence: str, word_freq: dict[str, int]) -> float:
    """
    Score a sentence as the sum of its word frequencies,
    normalised by sentence length to avoid favouring long sentences.
    """
    words = tokenize_words(sentence)
    if not words:
        return 0.0
    return sum(word_freq.get(w, 0) for w in words) / len(words)


def _idf_score(sentences: list[str]) -> dict[str, float]:
    """
    Compute inverse-document-frequency for each word across sentences.
    Adds a mild semantic weight on top of raw frequency.
    """
    N = len(sentences)
    doc_count: dict[str, int] = defaultdict(int)
    for sent in sentences:
        seen = set(tokenize_words(sent))
        for w in seen:
            doc_count[w] += 1

    idf = {}
    for word, count in doc_count.items():
        idf[word] = math.log((N + 1) / (count + 1)) + 1
    return idf


# ── Public API ────────────────────────────────────────────────

def summarize(text: str, num_sentences: int = 5) -> str:
    """
    Summarise *text* using a TextRank-inspired frequency approach.

    Parameters
    ----------
    text          : cleaned input text
    num_sentences : number of sentences to include in the summary

    Returns
    -------
    A multi-sentence summary string.
    """
    sentences = tokenize_sentences(text)

    # Need at least a few sentences to summarise
    if len(sentences) <= num_sentences:
        return text  # already short enough

    word_freq = _build_word_freq(sentences)
    idf       = _idf_score(sentences)

    # Combined score = frequency × IDF weight
    def combined_score(sent: str) -> float:
        words = tokenize_words(sent)
        if not words:
            return 0.0
        score = sum(word_freq.get(w, 0) * idf.get(w, 1.0) for w in words)
        return score / len(words)

    # Score every sentence while keeping its original index (for ordering)
    scored = [(combined_score(s), i, s) for i, s in enumerate(sentences)]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Pick top-N sentences and restore original document order
    top_indices = sorted([i for _, i, _ in scored[:num_sentences]])
    summary_sentences = [sentences[i] for i in top_indices]

    return ' '.join(summary_sentences)


def summarize_by_ratio(text: str, ratio: float = 0.3) -> str:
    """
    Summarise to a fraction of the original sentence count.
    ratio=0.3 keeps roughly 30 % of the content.
    """
    sentences = tokenize_sentences(text)
    n = max(3, int(len(sentences) * ratio))
    return summarize(text, num_sentences=n)
