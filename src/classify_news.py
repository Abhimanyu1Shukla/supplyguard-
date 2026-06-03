import pandas as pd
import torch
import pickle
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from sqlalchemy import create_engine, text as sql_text

# Setup
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

# Load model
print("🔄 Loading DistilBERT model...")
tokenizer = DistilBertTokenizer.from_pretrained("models/distilbert_supplyguard")
model = DistilBertForSequenceClassification.from_pretrained("models/distilbert_supplyguard")
model = model.to(device)
model.eval()

with open("models/label_map.pkl", "rb") as f:
    label_map = pickle.load(f)
reverse_label_map = {v: k for k, v in label_map.items()}
print("✅ Model loaded!")

def classify_text(content):
    encoding = tokenizer(
        content,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.softmax(outputs.logits, dim=1)
        pred_id = torch.argmax(probs).item()
        confidence = probs[0][pred_id].item()

    return reverse_label_map[pred_id], round(confidence, 3)

# Add columns if not exist
with engine.connect() as conn:
    conn.execute(sql_text("""
        ALTER TABLE raw_news
        ADD COLUMN IF NOT EXISTS risk_category VARCHAR(50),
        ADD COLUMN IF NOT EXISTS confidence FLOAT
    """))
    conn.commit()
print("✅ Database columns ready")

# Fetch unclassified articles
with engine.connect() as conn:
    result = conn.execute(sql_text("""
        SELECT id, title, description
        FROM raw_news
        WHERE risk_category IS NULL
    """))
    articles = result.fetchall()

print(f"🔄 Found {len(articles)} unclassified articles. Starting classification...")

# Classify each article
for i, article in enumerate(articles):
    article_id = article[0]
    title = article[1] or ""
    description = article[2] or ""
    content = f"{title} {description}".strip()

    risk_category, confidence = classify_text(content)

    with engine.connect() as conn:
        conn.execute(sql_text("""
            UPDATE raw_news
            SET risk_category = :category,
                confidence = :confidence
            WHERE id = :id
        """), {
            "category": risk_category,
            "confidence": confidence,
            "id": article_id
        })
        conn.commit()

    print(f"  [{i+1}/{len(articles)}] {title[:50]} → {risk_category} ({confidence:.0%})")

# Show final distribution
print("\n📊 Risk Distribution in database:")
with engine.connect() as conn:
    result = conn.execute(sql_text("""
        SELECT risk_category, COUNT(*) as total,
               ROUND(AVG(confidence)::numeric, 2) as avg_confidence
        FROM raw_news
        WHERE risk_category IS NOT NULL
        GROUP BY risk_category
        ORDER BY total DESC
    """))
    rows = result.fetchall()

print(f"{'Category':<25} {'Count':<10} {'Avg Confidence'}")
print("-" * 50)
for row in rows:
    print(f"{row[0]:<25} {row[1]:<10} {row[2]}")

print("\n✅ All articles classified!")