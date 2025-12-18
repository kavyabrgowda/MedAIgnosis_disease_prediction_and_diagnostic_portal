import pandas as pd 
from sqlalchemy import create_engine

# Load specialization data once when the module is imported
specialization_df = pd.read_csv('specialization.csv')

# Database connection (adjust as needed for your project structure)
engine = create_engine('postgresql://postgres:postgres@localhost/medical_db')

def get_specialization(predicted_disease):
    """
    Get the medical specialization for a given predicted disease.
    """
    specialization_row = specialization_df[specialization_df['Disease'] == predicted_disease]
    
    if not specialization_row.empty:
        return specialization_row.iloc[0]['Medical Specialization']  # Ensure this matches the CSV column name
    print(f"No specialization found for disease: {predicted_disease}")
    return None

def get_doctors_by_specialization(specialization):
    """
    Retrieve doctors from the database with the given specialization.
    """
    query = "SELECT first_name, last_name, speciality, education, hospital_affiliation FROM doctors WHERE speciality = %s"
    
    try:
        doctor_df = pd.read_sql_query(query, engine, params=(specialization,))
        if doctor_df.empty:
            print(f"No doctors found with specialization: {specialization}")
            return []
        return doctor_df.to_dict(orient='records')
    except Exception as e:
        print(f"An error occurred while fetching doctors: {e}")
        return []
