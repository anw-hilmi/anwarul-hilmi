FROM python:3.12-slim

# Instal dependensi sistem yang diperlukan untuk beberapa library Python (opsional tapi disarankan)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements terlebih dahulu untuk memanfaatkan cache layer Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh file dari context ke direktori kerja
COPY . .

# Pastikan port terekspos
EXPOSE 8501

# Tambahkan flag untuk mencegah Streamlit memunculkan browser dan mengaktifkan file watcher
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
