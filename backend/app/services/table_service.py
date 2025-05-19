# backend/app/services/table_service.py
from transformers import TapasTokenizer, TapasForQuestionAnswering
import torch

from app.core.config import settings

tokenizer = TapasTokenizer.from_pretrained(settings.HF_MODEL_TABLE)
model = TapasForQuestionAnswering.from_pretrained(settings.HF_MODEL_TABLE)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def parse_line_items(table: dict) -> list[dict]:
    """
    `table` should be dict with keys:
      - 'cells': List[str] flattened table text
      - 'coordinates': List[List[int]] positions (row, col)
      - 'num_rows', 'num_columns'
    """
    df = tokenizer.convert_cells_to_table(table["cells"], table["coordinates"])
    questions = ["What are the items?", "What are the quantities?",
                 "What are the unit prices?", "What are the totals?"]
    answers = {}
    for q in questions:
        inputs = tokenizer(table=table, queries=[q], return_tensors="pt").to(device)
        outputs = model(**inputs)
        parsed = tokenizer.convert_logits_to_predictions(
            inputs,
            outputs.logits.detach(),
            outputs.logits_aggregation.detach(),
        )
        answers[q] = parsed
    # Align results into list of dicts
    items = []
    rows = table["num_rows"]
    for idx in range(rows):
        items.append({
            "description": answers[questions[0]][0][idx],
            "quantity": float(answers[questions[1]][0][idx] or 1),
            "unit_price": float(answers[questions[2]][0][idx] or 0),
            "total_price": float(answers[questions[3]][0][idx] or 0),
        })
    return items
