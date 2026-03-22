import pickle
import os

# Get correct path
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")

# Load model
with open(model_path, "rb") as f:
    model, vectorizer = pickle.load(f)

def predict_review(review):
    review_vector = vectorizer.transform([review])
    prediction = model.predict(review_vector)[0]

    if prediction == 1:
        sentiment = "Positive"
        rating = 4.5
        stars = "★★★★★"
    else:
        sentiment = "Negative"
        rating = 1.5
        stars = "★☆☆☆☆"

    return sentiment, rating, stars