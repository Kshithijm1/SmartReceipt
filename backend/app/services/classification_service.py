# backend/app/services/classification_service.py
from transformers import pipeline
from app.core.config import settings

_zero_shot = pipeline(
    "zero-shot-classification",
    model=settings.HF_MODEL_ZERO_SHOT,
    device=0 if __import__("torch").cuda.is_available() else -1,
)
_text_clf = pipeline(
    "text-classification",
    model=settings.HF_MODEL_CLASSIFIER,
    device=0 if __import__("torch").cuda.is_available() else -1,
)


def classify_merchant(text: str, labels: list[str]):
    return _zero_shot(text, labels)


def classify_category(text: str):
    out = _text_clf(text, truncation=True)[0]
    return {"label": out["label"], "score": float(out["score"])}
