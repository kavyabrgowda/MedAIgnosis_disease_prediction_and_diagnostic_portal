-- Create Database if not exists
CREATE DATABASE medical_db;

-- Connect to the Database
-- \c medical_db;

-- Create Patients Table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10),
    date_of_birth DATE,
    contact_number VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    address TEXT,
    medical_history TEXT,
    allergies TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

-- Create Doctors Table
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    date_of_birth DATE,
    contact_number VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    address TEXT,
    medical_license_number VARCHAR(100) UNIQUE,
    speciality VARCHAR(100) NOT NULL,
    education TEXT,
    years_of_experience INTEGER NOT NULL,
    hospital_affiliation VARCHAR(100),
    languages_spoken VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
