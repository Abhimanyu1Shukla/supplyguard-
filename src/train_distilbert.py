import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Check if GPU available (M2 Mac has MPS)
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("✅ Using Apple M2 GPU (MPS)")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("✅ Using CUDA GPU")
else:
    device = torch.device("cpu")
    print("⚠️ Using CPU (slower but works)")

# Label mapping
label_map = {
    "natural_disaster": 0,
    "geopolitical": 1,
    "labour_strike": 2,
    "material_shortage": 3,
    "logistics": 4,
    "political": 5,
    "no_risk": 6
}
reverse_label_map = {v: k for k, v in label_map.items()}

# Load data
df = pd.read_csv("data/training_data.csv")
df["text"] = df["title"] + " " + df["description"].fillna("")
df["label_id"] = df["risk_label"].map(label_map)
df = df.dropna(subset=["label_id"])

print(f"Total samples: {len(df)}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df["text"].tolist(),
    df["label_id"].tolist(),
    test_size=0.2,
    random_state=42,
    stratify=df["label_id"]
)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# Tokenizer
print("\n🔄 Loading DistilBERT tokenizer...")
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

# Dataset class
class NewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label": torch.tensor(self.labels[idx], dtype=torch.long)
        }

# Create datasets
train_dataset = NewsDataset(X_train, y_train, tokenizer)
test_dataset = NewsDataset(X_test, y_test, tokenizer)

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8)

# Load DistilBERT model
print("🔄 Loading DistilBERT model...")
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=7
)
model = model.to(device)

# Training
optimizer = AdamW(model.parameters(), lr=2e-5)
EPOCHS = 5

print(f"\n🚀 Training for {EPOCHS} epochs...")
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()

    avg_loss = total_loss / len(train_loader)
    print(f"  Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.4f}")

# Evaluation
print("\n📊 Evaluating model...")
model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

accuracy = accuracy_score(all_labels, all_preds)
print(f"\n✅ DistilBERT Accuracy: {accuracy:.2%}")
print("\nDetailed Report:")
print(classification_report(
    all_labels, all_preds,
    target_names=list(label_map.keys())
))

# Test with real headlines
print("\n🧪 Testing with real headlines:")
test_headlines = [
    "Major earthquake hits Taiwan disrupting TSMC chip production",
    "Workers at Mumbai port go on strike demanding pay hike",
    "US announces new sanctions on Russian oil exports",
    "Infosys reports strong quarterly earnings beating estimates",
    "Severe flooding closes factories in Chennai industrial zone",
    "Steel prices surge as global shortage hits manufacturers"
]

model.eval()
for headline in test_headlines:
    encoding = tokenizer(
        headline,
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

    label = reverse_label_map[pred_id]
    print(f"  '{headline[:55]}...'")
    print(f"   → {label} (confidence: {confidence:.0%})\n")

# Save model
os.makedirs("models", exist_ok=True)
model.save_pretrained("models/distilbert_supplyguard")
tokenizer.save_pretrained("models/distilbert_supplyguard")
with open("models/label_map.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("✅ DistilBERT model saved to models/distilbert_supplyguard/")