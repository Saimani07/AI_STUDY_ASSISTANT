# modules/question_generator.py
# ============================================================
# QUESTION GENERATION MODULE
# Uses POS tagging and rule-based heuristics to produce
# meaningful practice questions from study text.
# ============================================================

import re
import random
import nltk
from nltk import pos_tag
from modules.preprocessor import tokenize_sentences, tokenize_words

# ── POS-tag helpers ──────────────────────────────────────────

def _get_pos_tags(sentence: str):
    """Return (word, POS-tag) pairs for a sentence."""
    words = nltk.word_tokenize(sentence)
    return pos_tag(words)


def _extract_noun_phrase(tagged: list) -> str | None:
    """
    Extract the first consecutive noun-phrase (NN/NNS/NNP/NNPS)
    from a POS-tagged sentence.
    """
    noun_tags = {'NN', 'NNS', 'NNP', 'NNPS'}
    phrase_words = []
    for word, tag in tagged:
        if tag in noun_tags:
            phrase_words.append(word)
        elif phrase_words:
            break  # end of first noun phrase
    return ' '.join(phrase_words) if phrase_words else None


# ── Question templates ────────────────────────────────────────

def _what_is_question(sentence: str) -> str | None:
    """Generate a 'What is …?' question from a definitional sentence."""
    tagged = _get_pos_tags(sentence)
    noun   = _extract_noun_phrase(tagged)
    if noun:
        return f"What is {noun}?"
    return None


def _how_does_question(sentence: str) -> str | None:
    """Generate a 'How does …?' question when a verb phrase is present."""
    tagged   = _get_pos_tags(sentence)
    vb_tags  = {'VB', 'VBZ', 'VBP', 'VBD'}
    nouns    = []
    has_verb = False
    for word, tag in tagged:
        if tag in {'NN', 'NNS', 'NNP', 'NNPS'}:
            nouns.append(word)
        if tag in vb_tags:
            has_verb = True
    if has_verb and nouns:
        subject = nouns[0]
        return f"How does {subject} work?"
    return None


def _why_question(sentence: str) -> str | None:
    """Generate a 'Why is …?' question for sentences with adjectives."""
    tagged   = _get_pos_tags(sentence)
    adj_tags = {'JJ', 'JJR', 'JJS'}
    nouns, adjs = [], []
    for word, tag in tagged:
        if tag in {'NN', 'NNS', 'NNP', 'NNPS'}:
            nouns.append(word)
        if tag in adj_tags:
            adjs.append(word)
    if nouns and adjs:
        return f"Why is {nouns[0]} considered {adjs[0]}?"
    return None


def _define_question(sentence: str) -> str | None:
    """Generate 'Define …' for sentences containing 'is' or 'are'."""
    if re.search(r'\bis\b|\bare\b', sentence, re.I):
        tagged = _get_pos_tags(sentence)
        noun   = _extract_noun_phrase(tagged)
        if noun:
            return f"Define the term: {noun}."
    return None


def _fill_blank_question(sentence: str) -> str | None:
    """
    Create a fill-in-the-blank question by blanking the
    first significant noun in the sentence.
    """
    tagged    = _get_pos_tags(sentence)
    noun_tags = {'NN', 'NNS', 'NNP', 'NNPS'}
    for word, tag in tagged:
        if tag in noun_tags and len(word) > 3:
            blank_sent = re.sub(r'\b' + re.escape(word) + r'\b',
                                '______', sentence, count=1)
            return f"Fill in the blank: {blank_sent}"
    return None


# Generator registry (order matters – more specific first)
_GENERATORS = [
    _define_question,
    _what_is_question,
    _how_does_question,
    _why_question,
    _fill_blank_question,
]


# ── Public API ────────────────────────────────────────────────

def generate_questions(text: str,
                       num_questions: int = 10,
                       seed: int = 42) -> list[str]:
    """
    Generate up to *num_questions* practice questions from *text*.

    Strategy
    --------
    1. Split text into sentences.
    2. For each sentence, try every question generator in order.
    3. Collect the first valid question per sentence.
    4. Shuffle and return up to num_questions.
    """
    random.seed(seed)
    sentences = tokenize_sentences(text)
    questions: list[str] = []

    for sent in sentences:
        # Skip very short or trivial sentences
        words = tokenize_words(sent, remove_stopwords=False)
        if len(words) < 6:
            continue

        for gen in _GENERATORS:
            q = gen(sent)
            if q and q not in questions:
                questions.append(q)
                break  # one question per sentence

    random.shuffle(questions)
    return questions[:num_questions] if questions else [
        "What are the main concepts discussed in this material?",
        "Summarise the key points covered in this text.",
        "How do the topics in this material relate to each other?",
    ]
