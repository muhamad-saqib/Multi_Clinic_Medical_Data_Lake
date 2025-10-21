# Multi-Clinic Medical Research Data Lake

A secure web app for medical data analysis with patient privacy protection.

## Features

- Patient data anonymization (removes names, addresses)
- Interactive charts and analytics
- Multiple clinics support
- Data export functionality
- Free cloud deployment

## Quick Setup

1. Create virtual environment:
python -m venv medical_env
medical_env\Scripts\activate  (Windows)
source medical_env/bin/activate  (Mac/Linux)

2. Install packages:
pip install -r requirements.txt

3. Run app:
streamlit run app.py

## Required CSV Format

patient_id, name, age, sex, visit_date, diagnosis_code
P001, Ali Khan, 25, M, 2024-01-15, FLU
P002, Sara Ahmed, 30, F, 2024-01-16, COLD

## How to Use

1. Upload CSV file using sidebar
2. Enter clinic name
3. Click "Ingest Data" to process
4. View analytics in dashboard
5. Download reports if needed

## Privacy Features

- Automatic removal of personal information
- Patient ID hashing for security
- Local data processing
- No external data sharing

## Technology

- Python + Streamlit
- SQLite database
- Pandas for data processing
- Free deployment on Streamlit Cloud

## Live Demo

[Your app live link here]

## Support

For issues, check the documentation or create GitHub issue.

# Author
Muhammad Saqib<br>
BSCS-SZABIST'26 | Python<br>
GitHub: @muhamad-saqib
