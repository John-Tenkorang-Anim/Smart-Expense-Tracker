import pickle
import numpy as np
import sqlite3
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report

MODEL_PATH = "models/expense_model.pkl"

def load_training_data():
    """
    Loads transaction data from SQLite for training.
    Uses both amount and text description as features.
    """
    conn = sqlite3.connect("expense_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT amount, description, category FROM transactions")
    data = cursor.fetchall()
    
    conn.close()
    
    if not data:
        return None, None, None
    
    amounts = np.array([[row[0]] for row in data])  
    descriptions = [row[1] for row in data]
    categories = np.array([row[2] for row in data])  
    
    return amounts, descriptions, categories


def train_model():
    """
    Trains a Naïve Bayes classifier using both amount and description.
    Saves the trained model to disk.
    """
    amounts, descriptions, categories = load_training_data()
    
    if amounts is None or len(amounts) < 5:
        print("Not enough data to train the model.")
        return
    
    vectorizer = TfidfVectorizer()
    description_features = vectorizer.fit_transform(descriptions)

    # Combine numerical and text features
    X_combined = np.hstack((amounts, description_features.toarray()))
    
    model = MultinomialNB()
    model.fit(X_combined, categories)

    # Save model and vectorizer
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((vectorizer, model), f)
    
    print("Model retrained successfully!")


def predict_category(amount, description):
    """
    Predicts the expense category based on amount and description.
    """
    try:
        with open(MODEL_PATH, "rb") as f:
            vectorizer, model = pickle.load(f)
    except FileNotFoundError:
        print("Model not found. Please train the model first.")
        return None

    description_feature = vectorizer.transform([description]).toarray()
    features = np.hstack(([amount], description_feature))  

    category = model.predict([features])
    return category[0]


def evaluate_model():
    """
    Evaluates the trained model using accuracy and classification report.
    """
    amounts, descriptions, categories = load_training_data()
    
    if amounts is None:
        print("No data for evaluation.")
        return
    
    try:
        with open(MODEL_PATH, "rb") as f:
            vectorizer, model = pickle.load(f)
    except FileNotFoundError:
        print("Model not found.")
        return

    description_features = vectorizer.transform(descriptions).toarray()
    X_combined = np.hstack((amounts, description_features))

    y_pred = model.predict(X_combined)
    accuracy = accuracy_score(categories, y_pred)
    
    print(f"Model Accuracy: {accuracy:.2f}")
    print(classification_report(categories, y_pred))
