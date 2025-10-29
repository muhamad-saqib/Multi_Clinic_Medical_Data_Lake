import gradio as gr
import pandas as pd
import sqlite3
import hashlib
import plotly.express as px
import plotly.io as pio
import os
from datetime import datetime

# Database functions
def init_database():
    conn = sqlite3.connect('medical_data.db')
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

def hash_id(raw_id):
    return hashlib.sha256(str(raw_id).encode()).hexdigest()[:16]

def remove_pii(df):
    df = df.copy()
    pii_columns = ['name', 'address', 'phone', 'email']
    for col in pii_columns:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    if 'patient_id' in df.columns:
        df['patient_hash'] = df['patient_id'].apply(hash_id)
        df.drop(columns=['patient_id'], inplace=True)
    return df

def save_to_database(df, clinic_name):
    conn = sqlite3.connect('medical_data.db')
    df['clinic'] = clinic_name
    df.to_sql('patients', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    return f"✅ Data saved successfully! {len(df)} records added."

def load_from_database():
    conn = sqlite3.connect('medical_data.db')
    try:
        df = pd.read_sql("SELECT * FROM patients", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# Initialize database
init_database()

# Gradio Functions
def process_file(file, clinic_name):
    if file is None:
        return "❌ Please upload a CSV file", None, None
    
    try:
        # Read CSV
        df = pd.read_csv(file.name)
        
        # Show original data
        original_html = f"<h3>📊 Original Data Preview ({len(df)} records)</h3>"
        original_html += df.head().to_html(classes='table table-striped', index=False)
        
        # Anonymize data
        clean_df = remove_pii(df)
        
        # Show cleaned data
        cleaned_html = f"<h3>🛡️ Anonymized Data</h3>"
        cleaned_html += clean_df.head().to_html(classes='table table-striped', index=False)
        
        # Save to database
        save_result = save_to_database(clean_df, clinic_name)
        
        return save_result, original_html, cleaned_html
    
    except Exception as e:
        return f"❌ Error: {str(e)}", None, None

def show_analytics():
    df = load_from_database()
    
    if df.empty:
        return "<h3>📝 No data available</h3><p>Upload data to see analytics.</p>", None, None, None
    
    # Basic stats
    stats_html = f"""
    <div style='background: #f8f9fa; padding: 20px; border-radius: 10px;'>
        <h3>📋 Database Overview</h3>
        <p><strong>Total Records:</strong> {len(df)}</p>
        <p><strong>Total Clinics:</strong> {df['clinic'].nunique()}</p>
        <p><strong>Average Age:</strong> {df['age'].mean():.1f} years</p>
        <p><strong>Unique Diagnoses:</strong> {df['diagnosis_code'].nunique()}</p>
    </div>
    """
    
    # Create charts
    charts_html = "<h3>📊 Analytics Dashboard</h3>"
    
    # Age distribution chart
    if 'age' in df.columns:
        fig_age = px.histogram(df, x='age', title="Age Distribution", 
                              color_discrete_sequence=['#267dff'])
        age_chart = pio.to_html(fig_age, include_plotlyjs='cdn', div_id="age_chart")
        charts_html += age_chart
    
    # Diagnosis chart
    if 'diagnosis_code' in df.columns:
        diagnosis_counts = df['diagnosis_code'].value_counts().reset_index()
        diagnosis_counts.columns = ['Diagnosis', 'Count']
        fig_diag = px.bar(diagnosis_counts, x='Diagnosis', y='Count', 
                         title="Diagnosis Distribution", color='Count')
        diag_chart = pio.to_html(fig_diag, include_plotlyjs=False, div_id="diag_chart")
        charts_html += diag_chart
    
    # Clinic distribution
    clinic_counts = df['clinic'].value_counts().reset_index()
    clinic_counts.columns = ['Clinic', 'Count']
    fig_clinic = px.pie(clinic_counts, values='Count', names='Clinic', 
                       title="Patients per Clinic")
    clinic_chart = pio.to_html(fig_clinic, include_plotlyjs=False, div_id="clinic_chart")
    charts_html += clinic_chart
    
    # Data preview
    data_html = f"<h3>💾 Current Database Data</h3>"
    data_html += df.head(10).to_html(classes='table table-striped', index=False)
    
    return stats_html, charts_html, data_html, df

def export_data():
    df = load_from_database()
    if df.empty:
        return None, "❌ No data available for export"
    
    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"medical_data_export_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    return filename, "✅ Data exported successfully!"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Medical Data Lake") as demo:
    gr.Markdown("# 🏥 Multi-Clinic Medical Data Lake")
    gr.Markdown("**Secure platform for medical data analysis with patient privacy protection**")
    
    with gr.Tab("📁 Data Upload"):
        with gr.Row():
            with gr.Column():
                file_input = gr.File(label="Upload CSV File", file_types=[".csv"])
                clinic_input = gr.Textbox(label="Clinic Name", value="Clinic_A")
                process_btn = gr.Button("💾 Process & Save Data", variant="primary")
            
            with gr.Column():
                result_output = gr.Textbox(label="Result", interactive=False)
                original_preview = gr.HTML(label="Original Data Preview")
                cleaned_preview = gr.HTML(label="Anonymized Data Preview")
        
        process_btn.click(
            fn=process_file,
            inputs=[file_input, clinic_input],
            outputs=[result_output, original_preview, cleaned_preview]
        )
    
    with gr.Tab("📊 Analytics"):
        refresh_btn = gr.Button("🔄 Refresh Analytics", variant="secondary")
        
        stats_output = gr.HTML(label="Statistics")
        charts_output = gr.HTML(label="Charts")
        data_output = gr.HTML(label="Database Preview")
        analytics_df = gr.Dataframe(label="Full Data", interactive=False)
        
        refresh_btn.click(
            fn=show_analytics,
            outputs=[stats_output, charts_output, data_output, analytics_df]
        )
    
    with gr.Tab("📥 Export"):
        export_btn = gr.Button("📄 Export Data to CSV", variant="primary")
        export_result = gr.Textbox(label="Export Result", interactive=False)
        export_file = gr.File(label="Download Exported Data", interactive=False)
        
        export_btn.click(
            fn=export_data,
            outputs=[export_file, export_result]
        )
    
    with gr.Tab("ℹ️ Instructions"):
        gr.Markdown("""
        ## 📋 How to Use
        
        ### 1. Data Upload
        - Upload a CSV file with patient data
        - Expected columns: `patient_id, name, age, sex, visit_date, diagnosis_code`
        - Enter your clinic name
        
        ### 2. Data Processing
        - System automatically removes personal information
        - Patient IDs are hashed for privacy
        - Data is saved to secure database
        
        ### 3. Analytics
        - View interactive charts and statistics
        - Monitor age distribution, diagnosis patterns
        - Track multiple clinics
        
        ### 4. Export
        - Download processed data as CSV
        - Generate reports for research
        
        ## 🔒 Privacy Features
        - Automatic PII removal
        - Secure patient ID hashing
        - Local data processing
        """)

# Launch app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
