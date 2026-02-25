"""
AI-Based Domain Classifier using TF-IDF + Logistic Regression.

This module:
1. Trains a classifier on labeled domain data (keywords per domain)
2. Saves the trained model using joblib
3. Provides classify_domain() function used by the scraper

How it works (for viva explanation):
- TF-IDF (Term Frequency-Inverse Document Frequency) converts text to numerical vectors
- Logistic Regression then predicts which domain the text belongs to
- We use a pre-defined seed dataset for initial training
"""

import os
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / 'domain_classifier.pkl'
VECTORIZER_PATH = Path(__file__).resolve().parent / 'tfidf_vectorizer.pkl'

# ─── Training Dataset ───────────────────────────────────────────────
# Each entry: (text, domain_label)
# In a real system, you'd collect labeled data from scraping + manual tagging.
TRAINING_DATA = [
    # AI
    ("machine learning deep learning neural network artificial intelligence", "AI"),
    ("natural language processing computer vision transformer bert gpt", "AI"),
    ("reinforcement learning robotics autonomous systems AI research", "AI"),
    ("data science python tensorflow pytorch kaggle model training", "AI"),
    ("generative AI large language models diffusion models", "AI"),
    ("computer vision image recognition object detection YOLO", "AI"),
    ("NLP text classification sentiment analysis named entity recognition", "AI"),

    # LAW
    ("law legal policy regulation compliance constitutional rights", "LAW"),
    ("international law human rights cyber law intellectual property patent", "LAW"),
    ("jurisprudence litigation arbitration contract corporate law", "LAW"),
    ("criminal law public policy legal reform advocacy", "LAW"),
    ("moot court law school legal clinic internship bar", "LAW"),

    # BIO
    ("biomedical biology genetics genomics protein CRISPR drug discovery", "BIO"),
    ("clinical research medical trial pharmacology neuroscience", "BIO"),
    ("biochemistry molecular biology cell biology immunology", "BIO"),
    ("bioinformatics computational biology health data medicine", "BIO"),
    ("public health epidemiology global health disease prevention", "BIO"),

    # ECE
    ("electronics circuits VLSI semiconductor embedded systems", "ECE"),
    ("signal processing communication systems wireless 5G antenna", "ECE"),
    ("FPGA microcontroller Arduino IoT Internet of Things", "ECE"),
    ("power systems electrical engineering renewable energy solar", "ECE"),
    ("photonics optics laser electromagnetic fields", "ECE"),

    # CS
    ("software engineering web development algorithms data structures", "CS"),
    ("cybersecurity network security blockchain cryptography", "CS"),
    ("cloud computing distributed systems operating systems", "CS"),
    ("database systems SQL NoSQL system design scalability", "CS"),
    ("open source programming hackathon coding competition", "CS"),

    # BUSINESS
    ("entrepreneurship startup venture capital business strategy", "BUSINESS"),
    ("finance economics investment banking marketing management", "BUSINESS"),
    ("MBA leadership operations management consulting", "BUSINESS"),
    ("social entrepreneurship impact investing non-profit", "BUSINESS"),

    # ENV
    ("environment sustainability climate change renewable energy", "ENV"),
    ("ecology environmental policy carbon emissions green technology", "ENV"),
    ("water conservation biodiversity environmental science", "ENV"),

    # OTHER (catch-all)
    ("arts humanities philosophy history social science", "OTHER"),
    ("music theater film media communication journalism", "OTHER"),
    ("education psychology sociology anthropology linguistics", "OTHER"),
]


def train_model():
    """
    Train the TF-IDF + Logistic Regression classifier.
    Saves model and vectorizer to disk using joblib.
    Call this once to create the model files.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        texts = [item[0] for item in TRAINING_DATA]
        labels = [item[1] for item in TRAINING_DATA]

        # Build pipeline: TF-IDF vectorizer → Logistic Regression
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),       # unigrams and bigrams
            stop_words='english',
            max_features=5000,
            sublinear_tf=True         # apply log normalization
        )

        classifier = LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver='lbfgs',
            multi_class='multinomial'
        )

        # Fit vectorizer and train classifier
        X = vectorizer.fit_transform(texts)
        classifier.fit(X, labels)

        # Save both to disk
        joblib.dump(vectorizer, VECTORIZER_PATH)
        joblib.dump(classifier, MODEL_PATH)

        logger.info("Domain classifier trained and saved successfully.")
        return True

    except Exception as e:
        logger.error(f"Failed to train classifier: {e}")
        return False


# Module-level cache — load model once, reuse
_vectorizer = None
_classifier = None


def _load_model():
    """Load model from disk into module-level cache."""
    global _vectorizer, _classifier

    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        logger.info("Model not found, training now...")
        train_model()

    try:
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _classifier = joblib.load(MODEL_PATH)
    except Exception as e:
        logger.error(f"Could not load model: {e}")


def classify_domain(text: str) -> str:
    """
    Given a piece of text (opportunity title + description),
    return the predicted domain label.

    Usage:
        from apps.opportunities.classifier import classify_domain
        domain = classify_domain("We are looking for AI/ML researchers...")
        # Returns: "AI"
    """
    global _vectorizer, _classifier

    if _vectorizer is None or _classifier is None:
        _load_model()

    if _vectorizer is None or _classifier is None:
        # Fallback if model still not available
        return keyword_fallback(text)

    try:
        X = _vectorizer.transform([text.lower()])
        domain = _classifier.predict(X)[0]
        return domain
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return keyword_fallback(text)


def keyword_fallback(text: str) -> str:
    """
    Lightweight keyword-based fallback if ML model fails.
    Simple but always works.
    """
    t = text.lower()
    if any(kw in t for kw in ['machine learning', 'deep learning', 'ai ', 'neural', 'nlp', 'computer vision']):
        return 'AI'
    if any(kw in t for kw in ['law', 'legal', 'policy', 'rights', 'regulation']):
        return 'LAW'
    if any(kw in t for kw in ['biology', 'medical', 'health', 'biomedical', 'genetics', 'clinical']):
        return 'BIO'
    if any(kw in t for kw in ['electronics', 'circuit', 'vlsi', 'embedded', 'ece', 'signal']):
        return 'ECE'
    if any(kw in t for kw in ['software', 'coding', 'programming', 'database', 'cybersecurity']):
        return 'CS'
    if any(kw in t for kw in ['business', 'startup', 'finance', 'entrepreneurship', 'mba']):
        return 'BUSINESS'
    if any(kw in t for kw in ['environment', 'climate', 'sustainability', 'ecology']):
        return 'ENV'
    return 'OTHER'


def get_confidence_scores(text: str) -> dict:
    """
    Return probability scores for all domains — useful for the UI
    to show confidence percentages.
    """
    global _vectorizer, _classifier

    if _vectorizer is None or _classifier is None:
        _load_model()

    if _vectorizer is None or _classifier is None:
        return {}

    try:
        X = _vectorizer.transform([text.lower()])
        probas = _classifier.predict_proba(X)[0]
        classes = _classifier.classes_
        return {cls: round(float(prob) * 100, 1) for cls, prob in zip(classes, probas)}
    except Exception:
        return {}
