import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Load training data
df = pd.read_csv("data/training_data.csv")
print(f"Training data: {len(df)} rows")
print(f"Labels: {df['risk_label'].unique()}")

# Combine title + description for better features
df["text"] = df["title"] + " " + df["description"].fillna("")

# Encode labels to numbers
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
df["label_id"] = df["risk_label"].map(label_map)

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label_id"],
    test_size=0.2,
    random_state=42,
    stratify=df["label_id"]
)
print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# Step 1 — TF-IDF Vectorizer
# Converts text into numbers the model can understand
print("\n🔄 Training TF-IDF + Logistic Regression model...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),  # unigrams + bigrams
    stop_words="english"
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Step 2 — Train Logistic Regression
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_tfidf, y_train)

# Step 3 — Evaluate
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Model Accuracy: {accuracy:.2%}")
print("\nDetailed Report:")
print(classification_report(
    y_test, y_pred,
    target_names=list(label_map.keys())
))

# Step 4 — Test with real examples
print("\n🧪 Testing with real headlines:")
test_headlines = [
    "Major earthquake hits Taiwan disrupting TSMC chip production",
    "Workers at Mumbai port go on strike demanding pay hike",
    "US announces new sanctions on Russian oil exports",
    "Infosys reports strong quarterly earnings beating estimates",
    "Severe flooding closes factories in Chennai industrial zone",
    "Steel prices surge as global shortage hits manufacturers"
]

for headline in test_headlines:
    vec = vectorizer.transform([headline])
    pred_id = model.predict(vec)[0]
    confidence = model.predict_proba(vec)[0].max()
    label = reverse_label_map[pred_id]
    print(f"  '{headline[:50]}...'")
    print(f"   → {label} (confidence: {confidence:.0%})\n")

# Save model and vectorizer
os.makedirs("models", exist_ok=True)
with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open("models/classifier.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/label_map.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("✅ Model saved to models/")