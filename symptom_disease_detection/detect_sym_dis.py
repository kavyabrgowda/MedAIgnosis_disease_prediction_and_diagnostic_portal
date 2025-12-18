import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

# Load dataset
df = pd.read_csv('symptom_disease_detection/symptom_sentence_dis.csv', encoding='ISO-8859-1')

# Handle cases where one symptom maps to multiple diseases by splitting diseases into lists
df['disease'] = df['disease'].apply(lambda x: x.split(','))

# Initialize MultiLabelBinarizer to handle multi-label classification
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['disease'])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['symptoms'], y, test_size=0.2, random_state=42)

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Fit vectorizer to training data and transform both sets
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Initialize and train random forest classifier for multi-label classification
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train_tfidf, y_train)

# Function to retrieve diseases for specific symptoms
def get_diseases_for_symptoms(symptoms):
    symptoms_lower = symptoms.lower()  # Convert symptoms to lowercase
    matched_diseases = df[df['symptoms'].str.lower().str.contains(symptoms_lower)]['disease'].apply(lambda x: ', '.join(x))
    return matched_diseases.unique()
