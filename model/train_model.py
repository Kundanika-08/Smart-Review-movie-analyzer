import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load dataset
data = pd.read_csv("IMDB Dataset.csv")

# Convert sentiment to numbers
data['sentiment'] = data['sentiment'].map({'positive': 1, 'negative': 0})

# Features and labels
X = data['review']
y = data['sentiment']

# Convert text to numbers
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_vectorized = vectorizer.fit_transform(X)

# Train model
model = LogisticRegression()
model.fit(X_vectorized, y)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump((model, vectorizer), f)

print("Model trained successfully!")