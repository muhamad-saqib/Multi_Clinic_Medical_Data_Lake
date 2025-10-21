import streamlit as st
import pandas as pd
import sqlite3
from anonymize import remove_pii

# Page configuration
st.set_page_config(page_title="Medical Data Lake", page_icon="🏥")

DB_PATH = "data.db"

def init_database():
    """Database tables create karein agar nahi hain to"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clinic TEXT NOT NULL,
        patient_hash TEXT,
        age INTEGER,
        sex TEXT,
        visit_date TEXT,
        diagnosis_code TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_to_database(df, clinic_name):
    """Data ko database mein save karein"""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Clinic name add karein
        df['clinic'] = clinic_name
        
        # Database mein save karein
        df.to_sql('patients', conn, if_exists='append', index=False)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False
    finally:
        conn.close()

def load_from_database():
    """Database se data load karein"""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM patients", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# Initialize database
init_database()

# Title
st.title("🏥 Multi-Clinic Medical Research Data Lake")
st.write("Secure platform for medical data analysis")

# Sidebar for upload
st.sidebar.header("📁 Data Upload")

# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file", 
    type=['csv'],
    help="Upload patient data CSV file"
)

# Clinic name input
clinic_name = st.sidebar.text_input(
    "Clinic Name", 
    value="Clinic_A",
    help="Enter your clinic name"
)

# Main area
if uploaded_file is not None:
    # Read CSV file
    df = pd.read_csv(uploaded_file)
    
    st.subheader(f"📊 Data Preview for {clinic_name}")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(df.head())
    
    # Show original columns
    st.write("**Original Columns:**", list(df.columns))
    
    # Anonymization preview
    st.subheader("🛡️ Anonymization Preview")
    cleaned_df = remove_pii(df)
    st.write("**After removing personal information:**")
    st.dataframe(cleaned_df.head())
    st.write("**Final Columns for Database:**", list(cleaned_df.columns))
    
    # Data Ingestion Button
    if st.sidebar.button("💾 Ingest Data into Database"):
        with st.spinner('Data processing and saving...'):
            # Anonymize data
            final_df = remove_pii(df)
            
            # Debug information
            st.write("🔍 Debug Info:")
            st.write(f"Final DataFrame shape: {final_df.shape}")
            st.write(f"Final Columns: {list(final_df.columns)}")
            
            # Save to database
            success = save_to_database(final_df, clinic_name)
            
            if success:
                st.sidebar.success("✅ Data successfully ingested!")
                st.balloons()
                
                # Show saved data
                saved_data = load_from_database()
                st.subheader("💾 Saved Data in Database")
                st.dataframe(saved_data)
            else:
                st.sidebar.error("❌ Failed to save data!")

else:
    st.info("👆 Please upload a CSV file to get started")
    st.write("**Expected columns:** patient_id, name, age, sex, visit_date, diagnosis_code")

# Load existing data for dashboard
existing_data = load_from_database()

if not existing_data.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Dashboard")
    
    st.subheader("📊 Database Overview")
    st.write(f"Total Records: {len(existing_data)}")
    st.write(f"Total Clinics: {existing_data['clinic'].nunique()}")
    
    # Show all data
    st.write("**All Data in Database:**")
    st.dataframe(existing_data)
else:
    st.info("📝 No data in database yet. Upload a CSV file to get started!")
    
if not existing_data.empty:
    st.markdown("---")
    st.subheader("📈 Analytics Dashboard")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Age Distribution**")
        if 'age' in existing_data.columns:
            # Simple age chart
            age_chart_data = existing_data['age'].value_counts().sort_index()
            st.bar_chart(age_chart_data)
        else:
            st.info("Age data not available")
    
    with col2:
        st.write("**Diagnosis Distribution**")
        if 'diagnosis_code' in existing_data.columns:
            # Simple diagnosis chart
            diagnosis_chart_data = existing_data['diagnosis_code'].value_counts()
            st.bar_chart(diagnosis_chart_data)
        else:
            st.info("Diagnosis data not available")
    
    # Clinic-wise data
    st.write("**Clinic-wise Records**")
    clinic_data = existing_data['clinic'].value_counts()
    st.bar_chart(clinic_data)
    
    # Data summary
    st.write("**Data Summary**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patients", len(existing_data))
    
    with col2:
        st.metric("Total Clinics", existing_data['clinic'].nunique())
    
    with col3:
        if 'age' in existing_data.columns:
            avg_age = existing_data['age'].mean()
            st.metric("Average Age", f"{avg_age:.1f} years")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🔒 Patient privacy protected with secure hashing")