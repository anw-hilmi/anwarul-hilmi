import argparse
import os
import numpy as np
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def train():
    # 1. Parsing Parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="Dataset-Final/train/")
    parser.add_argument("--f1", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--u", type=int, default=64)
    args = parser.parse_args()

    # 2. Setup MLflow
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("ZooVision_Experiment")
    
    with mlflow.start_run():
        # Log Parameters
        mlflow.log_param("dataset_path", args.dataset_path)
        mlflow.log_param("f1_filters", args.f1)
        mlflow.log_param("learning_rate", args.lr)
        mlflow.log_param("units", args.u)

        # 3. Data Preprocessing (Simple Generator)
        datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
        
        train_generator = datagen.flow_from_directory(
            args.dataset_path,
            target_size=(150, 150),
            batch_size=32,
            class_mode='categorical',
            subset='training'
        )

        # 4. Model Architecture (Menggunakan param f1 dan u)
        model = Sequential([
            Conv2D(args.f1, (3, 3), activation='relu', input_shape=(150, 150, 3)),
            MaxPooling2D(2, 2),
            Flatten(),
            Dense(args.u, activation='relu'),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        # 5. Training
        history = model.fit(train_generator, epochs=5)

        # 6. Log Metrics & Artifacts
        mlflow.log_metric("final_accuracy", history.history['accuracy'][-1])
        
        # Simpan Model sebagai Artifact
        mlflow.keras.log_model(model, "model")
        
        # Simpan Label Kelas sebagai Artifact (Text file)
        with open("labels.txt", "w") as f:
            for label in train_generator.class_indices.keys():
                f.write(f"{label}\n")
        mlflow.log_artifact("labels.txt")

        print(f"Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    train()