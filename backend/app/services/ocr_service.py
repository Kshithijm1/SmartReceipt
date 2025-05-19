# backend/app/services/ocr_service.py
import io
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

from app.core.config import settings

# Load once
processor = TrOCRProcessor.from_pretrained(settings.HF_MODEL_OCR)
model = VisionEncoderDecoderModel.from_pretrained(settings.HF_MODEL_OCR)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
    generated_ids = model.generate(pixel_values, max_length=512)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
