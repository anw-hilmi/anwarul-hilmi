import argparse
import os
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def train():
    # 1. Parsing Parameter
    parser = argparse.ArgumentParser()
    # Path disesuaikan dengan struktur folder Dataset-Final
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    parser.add_argument("--train_path", type=str, 
                        default=os.path.join(base_dir, "Dataset-Final", "train"))
    parser.add_argument("--test_path", type=str, 
                        default=os.path.join(base_dir, "Dataset-Final", "test"))
    parser.add_argument("--f1", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.0001)
    parser.add_argument("--u", type=int, default=64)
    args = parser.parse_args()

    # 2. Setup MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    
    with mlflow.start_run():
        # Log Parameters
        mlflow.log_params({
            "f1_filters": args.f1,
            "learning_rate": args.lr,
            "units": args.u
        })

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

        # Log Dataset Metadata
        mlflow.log_param("train_samples", train_generator.samples)
        mlflow.log_param("test_samples", test_generator.samples)

        # 4. Model Architecture
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

        # 5. Training & Validation
        history = model.fit(
            train_generator, 
            epochs=5,
            validation_data=test_generator
        )

        # 6. Log Metrics, Artifacts, & Model
        # Log metrics terakhir
        mlflow.log_metric("train_accuracy", history.history['accuracy'][-1])
        mlflow.log_metric("test_accuracy", history.history['val_accuracy'][-1])
        
        # Log Model
        mlflow.keras.log_model(model, "cnn-model")
        
        # Simpan dan Log Labels sebagai Artifact
        with open("labels.txt", "w") as f:
            for label in train_generator.class_indices.keys():
                f.write(f"{label}\n")
        mlflow.log_artifact("labels.txt")
        
        # Log local dataset path sebagai info tambahan
        mlflow.log_dict({"train": args.train_path, "test": args.test_path}, "dataset_info.json")

        print(f"Selesai! Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    train()