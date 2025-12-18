import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import numpy as np
import pytesseract
from PIL import Image
import cv2
import os
from collections import Counter

# Specify the path to Tesseract-OCR executable (only for Windows users)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\KAVYA B R\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Step 1: Load the dataset
df = pd.read_csv('test_result_detection/testresult_disease.csv', encoding='ISO-8859-1')

def extract_features(test_result):
    if "(No Results)" in test_result:
        return [0] * 12  # Adjusted to include additional keyword features

    features = []
    tests = test_result.split(", ")

    # Define keywords for positive and negative results
    keywords = {
        'positive': ['positive', 'reactive', 'abnormal'],
        'negative': ['negative', 'non-reactive', 'normal']
    }
    
    positive_indicator = 0
    negative_indicator = 0
    
    for test in tests:
        for keyword in keywords['positive']:
            if keyword in test.lower():
                positive_indicator = 1
        
        for keyword in keywords['negative']:
            if keyword in test.lower():
                negative_indicator = 1
        
        try:
            measurement = test.split(": ")[1]
            if '-' in measurement:  # It's a range
                lower, upper = map(float, measurement.split('-'))
                features.append((lower + upper) / 2)  # Use the average of the range
            else:  # It's a single value
                value = float(measurement.split()[0])  # Get the first number (ignoring units if any)
                features.append(value)
        except (IndexError, ValueError) as e:
            features.append(0)  # Append a default value

    features.append(positive_indicator)
    features.append(negative_indicator)

    while len(features) < 12:  # Ensure the feature list is of consistent length
        features.append(0)  # Padding with zeros
    return features[:12]  # Truncate to the fixed length

# Step 3: Create Feature and Target Arrays
X = np.array([extract_features(test) for test in df['Test Results']])
y = df['Disease'].values

# Handle missing values if necessary
X = np.nan_to_num(X, nan=-1)  # Replace NaNs with -1

# Step 4: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Initialize and train the Random Forest classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)  # Fixed random state for reproducibility
rf.fit(X_train, y_train)

# Step 8: Define a function to predict disease based on test results
def predict_disease(test_result):
    features = extract_features(test_result)
    prediction = rf.predict([features])
    return prediction[0]

# Step 9: Function to extract text from the image
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Apply Gaussian blur to reduce noise
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)  # Apply thresholding
    text = pytesseract.image_to_string(thresh)
    return text

# Step 10: Function to process extracted text into test results
def process_extracted_text(text):
    test_results = {}
    lines = text.split('\n')
    
    for line in lines:
        if ": " in line:
            parts = line.split(": ")
            if len(parts) >= 2:
                test_name = parts[0]
                result = ": ".join(parts[1:]).strip()
                test_results[test_name] = result
    return test_results

# Step 11: Function to predict disease from image with caching
prediction_cache = {}

def predict_disease_from_image(image_path):
    if image_path in prediction_cache:
        print(f"Using cached result for {image_path}.")
        return prediction_cache[image_path]

    text = extract_text_from_image(image_path)
    test_results = process_extracted_text(text)
    test_result_str = ", ".join([f"{key}: {value}" for key, value in test_results.items()])
    predicted_disease = predict_disease(test_result_str)
    
    prediction_cache[image_path] = predicted_disease  # Cache the result
    return predicted_disease

# Step 12: Main function to handle multiple image paths and aggregate predictions
def main():
    image_paths = []
    
    while True:
        image_path = input("\nPlease upload your medical report image path (jpeg, jpg, png, webp) or press Enter to finish: ")
        
        if image_path == "":
            break

        if not os.path.isfile(image_path) or not image_path.lower().endswith(('.jpeg', '.jpg', '.png', '.webp')):
            print("Invalid file path or unsupported file format. Please provide a valid image.")
            continue

        image_paths.append(image_path)

    if not image_paths:
        print("No images provided. Exiting.")
        return

    predictions = [predict_disease_from_image(path) for path in image_paths]
    final_prediction = Counter(predictions).most_common(1)[0][0]  # Get the most common prediction

    print("Aggregated Predicted Disease:", final_prediction)

if __name__ == "__main__":
    main()
