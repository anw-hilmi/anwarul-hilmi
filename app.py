import streamlit as st
import tensorflow as tf
import gdown
import os
import numpy as np
from PIL import Image

# Konfigurasi GDrive (Gunakan Folder ID tempat model disimpan)
FOLDER_ID = "1TY5tzm4Ts9Yx3iY9uuV5Vh0rE5aUxaRE"
MODEL_PATH = "model.keras"

@st.cache_resource
def load_model_from_drive():
    # URL unduh folder/file (tergantung cara simpan di workflow)
    url = f'https://drive.google.com/uc?id={FOLDER_ID}' 
    if not os.path.exists(MODEL_PATH):
        gdown.download(url, MODEL_PATH, quiet=False)
    return tf.keras.models.load_model(MODEL_PATH)

st.title("Animal Classifier Deployment")
model = load_model_from_drive()

uploaded_file = st.file_uploader("Upload gambar hewan...", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).resize((150, 150))
    st.image(image, caption="Gambar Terupload")
    
    img_array = np.expand_dims(np.array(image) / 255.0, axis=0)
    predictions = model.predict(img_array)
    classes = ['cat', 'dog', 'elephant', 'horse', 'lion']
    
    st.write(f"Prediksi: **{classes[np.argmax(predictions)]}**")