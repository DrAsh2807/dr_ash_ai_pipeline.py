🧠 Dr. Ash AI QEEG Report Generator
📌 Overview
This Streamlit app generates two professional QEEG reports:
Clinical Report – detailed EEG findings with Z-score analysis, Brodmann area mapping, neurophysiological explanations, swLORETA neurofeedback, biofeedback, neuro-nutrition, and functional neurological exercise recommendations.
Patient-Friendly Report – simplified explanations with lifestyle, nutrition, and neurofeedback guidance patients can easily follow.
Both reports are automatically generated as PDFs with page numbers, embedded visuals, and headmaps.
📸 Preview
Add a screenshot of your app here (replace app_screenshot.png with your image file):
📂 Supported File Inputs
Upload any combination of:
QEEG Data: .edf, .csv
Reports: .pdf, .docx, .jpeg, .jpg, .png
Headmaps: .jpeg, .jpg, .png
Lifestyle & Background Questionnaires: .pdf, .docx, .csv, .jpeg, .jpg, .png
Brain Region Localisation Forms: .pdf, .docx, .csv, .jpeg, .jpg, .png
⚙️ Features
EEG bandpower extraction (Delta, Theta, Alpha, Beta, High Beta).
Z-score interpretation with auto-mapping to Brodmann areas.
Clinical significance + neurophysiological explanations.
Amplitude, asymmetry, coherence, and phase lag analysis.
OCR for scanned PDFs and JPEG/PNG forms.
Dual report output: Clinical_Report.pdf + Patient_Report.pdf.
🚀 Installation
Clone the repo and install dependencies:
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt
Run locally:
streamlit run dr_ash_ai_pipeline.py
☁️ Deploy on Streamlit Cloud
Push your repo to GitHub.
Go to Streamlit Cloud.
Create a new app → Select your repo.
Set Main file path to:
dr_ash_ai_pipeline.py
Deploy 🚀
👨‍⚕️ Author
Dr. Ash
Head Clinician — The Healthy Brain Clinic
