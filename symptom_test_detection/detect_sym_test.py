import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv('symptom_test_detection/symptom_tests.csv', encoding='ISO-8859-1')

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['Symptoms'], df['Tests'], test_size=0.2, random_state=42)

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Fit vectorizer to training data and transform both sets
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Initialize and train random forest classifier
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train_tfidf, y_train)

# Function to predict tests based on symptoms
def predict_tests(symptoms):
    symptoms_tfidf = vectorizer.transform([symptoms])  # Transform the input symptoms
    prediction = rf.predict(symptoms_tfidf)              # Predict tests for symptoms
    return prediction
