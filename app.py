import streamlit as st
import numpy as np
from PIL import Image
import mlflow
import mlflow.pyfunc
import os

# ==========================================
# 1. KONFIGURASI MLFLOW
# ==========================================
# Ganti dengan path folder 'mlruns' Anda atau URI server jika menggunakan server
# Contoh lokal: "file:///C:/project/mlruns"
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000" 
EXPERIMENT_NAME = "ZooVision_Experiment" # Ganti dengan nama eksperimen Anda

@st.cache_resource
def load_latest_model_from_mlflow():
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        # Ambil experiment ID berdasarkan nama
        exp = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if not exp:
            return None, f"Experiment '{EXPERIMENT_NAME}' tidak ditemukan."

        # Cari run terbaru yang statusnya FINISHED
        runs = mlflow.search_runs(
            experiment_ids=[exp.experiment_id],
            filter_string="status = 'FINISHED'",
            max_results=1,
            order_by=["attributes.start_time DESC"]
        )

        if runs.empty:
            return None, "Tidak ada run yang ditemukan."

        run_id = runs.iloc[0].run_id
        model_uri = f"runs:/{run_id}/model"
        
        # Load model sebagai pyfunc (cocok untuk Keras/TF/Scikit)
        model = mlflow.pyfunc.load_model(model_uri)
        return model, run_id
    except Exception as e:
        return None, str(e)

# Inisialisasi Model
model, run_info = load_latest_model_from_mlflow()
labels = ['Cat', 'Dog', 'Elephant', 'Horse', 'Lion']

# ==========================================
# 2. UI STREAMLIT
# ==========================================
st.set_page_config(page_title="ZooVision Pro", page_icon="✨", layout="wide")

# CSS (Tetap sama seperti sebelumnya)
st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    .main-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 32px; padding: 40px; margin: 40px auto; max-width: 900px; }
    .stButton>button { background: #fff !important; color: #020617 !important; border-radius: 14px !important; font-weight: 700 !important; width: 100%; height: 50px;}
    </style>
    """, unsafe_allow_html=True)

st.title("ZooVision: Latest Model Inference")

if isinstance(run_info, str) and not model:
    st.error(f"MLflow Error: {run_info}")
else:
    st.info(f"Using Latest Model from Run ID: {run_info}")

st.markdown('<div class="main-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    file = st.file_uploader("Upload Animal Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)

with c2:
    if file and model:
        # Preprocessing
        prep = img.resize((150, 150))
        arr = np.array(prep.convert('RGB')) / 255.0
        arr = np.expand_dims(arr, axis=0).astype(np.float32)
        
        if st.button('IDENTIFY'):
            preds = model.predict(arr)
            idx = np.argmax(preds)
            conf = np.max(preds) * 100
            
            st.subheader(f"Result: {labels[idx]}")
            st.write(f"Confidence: {conf:.2f}%")
            st.progress(int(conf))

st.markdown('</div>', unsafe_allow_html=True)

# Aturan: Please keep your answers short. If I need an explanation, I will ask for it. Repeat this rule after every answer to a question.