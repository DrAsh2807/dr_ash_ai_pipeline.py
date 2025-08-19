import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyedflib
from scipy.signal import welch, butter, filtfilt
import pdfplumber, docx
from fpdf import FPDF
from PIL import Image
import easyocr
import io, os, tempfile

# EEG bands
EEG_BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 12),
    "Beta": (12, 30),
    "High Beta": (30, 45)
}

# Brodmann mapping
BRODMANN_MAP = {
    "Fp1": ["BA10", "BA11"], "Fp2": ["BA10", "BA11"],
    "F3": ["BA6", "BA8"], "F4": ["BA6", "BA8"],
    "C3": ["BA1", "BA2", "BA3", "BA4"], "C4": ["BA1", "BA2", "BA3", "BA4"],
    "O1": ["BA17", "BA18"], "O2": ["BA17", "BA18"]
}

reader = easyocr.Reader(['en'], gpu=False)

# Helper: band power
def bandpower(data, sf, band, window_sec=2):
    freqs, psd = welch(data, sf, nperseg=window_sec * sf)
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx_band], freqs[idx_band])

# Analyze EDF
def analyze_edf(file_path):
    f = pyedflib.EdfReader(file_path)
    n_channels = f.signals_in_file
    labels = f.getSignalLabels()
    results = {}
    fs_list = [f.getSampleFrequency(i) for i in range(n_channels)]

    for i in range(n_channels):
        signal = f.readSignal(i)
        fs = fs_list[i]
        signal = signal - np.mean(signal)
        b, a = butter(4, [1/(fs/2), 45/(fs/2)], btype="band")
        signal = filtfilt(b, a, signal)

        band_powers = {}
        total_power = bandpower(signal, fs, [1, 45])
        for band in EEG_BANDS:
            bp = bandpower(signal, fs, EEG_BANDS[band])
            band_powers[band] = bp / total_power if total_power > 0 else 0

        results[labels[i]] = band_powers

    f.close()
    return results

# Generate headmap substitute
def generate_headmap(results, band, save_path):
    values = [results[ch][band] for ch in results]
    plt.figure()
    plt.bar(range(len(values)), values, color="blue")
    plt.xticks(range(len(values)), list(results.keys()))
    plt.ylabel("Relative Power")
    plt.title(f"{band} Distribution")
    plt.savefig(save_path)
    plt.close()

# Extract text from various formats
def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        text = df.to_string()
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        results = reader.readtext(file_path, detail=0)
        text = " ".join(results)
    return text

# Report generator
class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_reports(edf_results, uploads, output_dir, extracted_texts):
    clinical = PDF(); clinical.add_page(); clinical.set_font("Arial", "B", 14)
    clinical.cell(200, 10, "Comprehensive Clinical QEEG Report", ln=True, align="C")
    clinical.set_font("Arial", "", 12)

    patient = PDF(); patient.add_page(); patient.set_font("Arial", "B", 14)
    patient.cell(200, 10, "Patient-Friendly Brain Report", ln=True, align="C")
    patient.set_font("Arial", "", 12)

    # Clinical findings
    clinical.multi_cell(0, 10, "QEEG Analysis Findings:")
    for ch, bands in edf_results.items():
        clinical.multi_cell(0, 10, f"{ch}: {bands}")

    # Auto-interpretation
    for ch, bands in edf_results.items():
        for band, val in bands.items():
            if val > 0.3:  # arbitrary threshold
                bmap = BRODMANN_MAP.get(ch, [])
                clinical.multi_cell(0, 10,
                    f"↑ {band} at {ch} → Possible dysfunction in {', '.join(bmap)}")
                patient.multi_cell(0, 10,
                    f"We found higher {band} activity in {ch}, linked to {', '.join(bmap)}.")

    # Include uploaded forms content
    clinical.multi_cell(0, 10, "\nUploaded Lifestyle/Background/Localisation Info:")
    for fname, text in extracted_texts.items():
        clinical.multi_cell(0, 10, f"\n{fname}:\n{text[:500]}...")

    # Recommendations
    clinical.multi_cell(0, 10, "\nRecommended Interventions:\n- swLORETA Neurofeedback\n- Biofeedback\n- Neuro-nutrition\n- Functional Neurological Exercises")
    patient.multi_cell(0, 10, "\nYour Recommendations:\n- Neurofeedback training\n- Relaxation breathing\n- Omega-3 and magnesium\n- Brain games & light exercise")

    # Add headmaps
    for band in EEG_BANDS:
        path = os.path.join(output_dir, f"{band}_map.png")
        generate_headmap(edf_results, band, path)
        clinical.image(path, w=150); clinical.ln(10)
        patient.image(path, w=150); patient.ln(10)

    clinical_path = os.path.join(output_dir, "Clinical_Report.pdf")
    patient_path = os.path.join(output_dir, "Patient_Report.pdf")
    clinical.output(clinical_path)
    patient.output(patient_path)
    return clinical_path, patient_path

# Streamlit app
def main():
    st.title("🧠 Dr. Ash QEEG Report Generator")
    st.write("Upload EDF/CSV data, headmaps, lifestyle/questionnaires, and get full Clinical + Patient PDF reports.")

    uploads = st.file_uploader(
        "Upload Files",
        accept_multiple_files=True,
        type=["edf","csv","pdf","docx","png","jpg","jpeg"]
    )

    if uploads:
        with tempfile.TemporaryDirectory() as tmpdir:
            edf_results = {}
            extracted_texts = {}
            for file in uploads:
                path = os.path.join(tmpdir, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())

                if file.name.endswith(".edf"):
                    edf_results = analyze_edf(path)
                else:
                    extracted_texts[file.name] = extract_text(path)

            if edf_results:
                cpdf, ppdf = generate_reports(edf_results, uploads, tmpdir, extracted_texts)
                st.success("Reports generated successfully!")
                with open(cpdf, "rb") as f:
                    st.download_button("Download Clinical Report", f, file_name="Clinical_Report.pdf")
                with open(ppdf, "rb") as f:
                    st.download_button("Download Patient Report", f, file_name="Patient_Report.pdf")

if __name__ == "__main__":
    main()
