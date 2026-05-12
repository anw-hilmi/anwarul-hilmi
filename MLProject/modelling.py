import argparse
import os
import mlflow
import mlflow.tensorflow
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def train():
    # 1. Parsing Parameter
    parser = argparse.ArgumentParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    parser.add_argument("--train_path", type=str, default=os.path.join(base_dir, "Dataset-Final", "train"))
    parser.add_argument("--test_path", type=str, default=os.path.join(base_dir, "Dataset-Final", "test"))
    parser.add_argument("--f1", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--u", type=int, default=64)
    args = parser.parse_args()

    # 2. Setup MLflow & Autolog
    # Menggunakan server HTTP agar log_artifact tidak error
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Animal_Classification_Autolog")
    mlflow.tensorflow.autolog() 

    with mlflow.start_run():
        # 3. Data Preprocessing
        train_datagen = ImageDataGenerator(rescale=1./255)
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        train_generator = train_datagen.flow_from_directory(
            args.train_path,
            target_size=(150, 150),
            batch_size=32,
            class_mode='categorical'
        )

        test_generator = test_datagen.flow_from_directory(
            args.test_path,
            target_size=(150, 150),
            batch_size=32,
            class_mode='categorical',
            shuffle=False
        )

        # 4. Model Architecture
        model = Sequential([
        Conv2D(64, (3, 3), activation='relu', input_shape=(150, 150, 3)),
        tf.keras.layers.BatchNormalization(),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(32, activation='relu'),
        Dense(5, activation='softmax')
        ])

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        # 5. Training & Validation
        model.fit(
            train_generator, 
            epochs=5,
            validation_data=test_generator
        )

        # 6. Artifact Tambahan
        labels_path = "labels.txt"
        with open(labels_path, "w") as f:
            for label in train_generator.class_indices.keys():
                f.write(f"{label}\n")
        mlflow.log_artifact(labels_path)
        
        print(f"Selesai! Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    train()