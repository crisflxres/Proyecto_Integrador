import pandas as pd # manejar los datos en forma de DataFrame
import numpy as np #manejar los datos
import joblib # Para guardar y cargar el modelo
from sklearn.model_selection import train_test_split #Entrenamiento, prueba y validacion
from sklearn.tree import DecisionTreeClassifier #Clasificador de arboles de desicion
from sklearn.pipeline import Pipeline #Crear un pipeline de procesamiento

# configuracion
archivo_csv = 'Lecturas_de_los_sensores.csv'
modelo_archivo = 'modelo_carrito.pkl' 

if __name__ == "__main__":
    print("- ENTRENAMIENTO DEL CARRITO -")
    try:
        df = pd.read_csv(archivo_csv)
        print(f"Datos cargados desde '{archivo_csv}'. Primeras 5 filas:")
        print(df.head())
        print(f"Total de registros: {len(df)}")

        if len(df) < 20:
            print("Advertencia: Pocos datos para un entrenamiento efectivo.")
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_csv}' no fue encontrado.")
        print("Ejecuta primero 'Conexion_Arduino_Mejorada.py' para capturar y guardar los datos.")
        exit()
    except Exception:
        print("Error al cargar o procesar el archivo de datos.")
        exit()

    X = df[['izquierda', 'centro', 'derecha']]
    y = df['accion']

    # División de los datos en Entrenamiento, Validación y Prueba
    # Primer split: 60% Entrenamiento, 40% Resto
    # 'stratify=y' para mantener la proporción de las clases en los subsets.
    X_train, X_rest, y_train, y_rest = train_test_split(X, y, test_size=0.4, random_state=123, stratify=y)

    # Segundo split: El 'Resto' se divide en 50% Validación, 50% Prueba
    X_val, X_test, y_val, y_test = train_test_split(X_rest, y_rest, test_size=0.5, random_state=123, stratify=y_rest)

    print("\n-Tamaños de los Datasets -")
    print(f"Dataset Original: {X.shape[0]} muestras")
    print(f"Dataset de Entrenamiento: {X_train.shape[0]} muestras")
    print(f"Dataset de Validación: {X_val.shape[0]} muestras")
    print(f"Dataset de Prueba: {X_test.shape[0]} muestras")

    pipeline = Pipeline([
        ('clasificador', DecisionTreeClassifier(random_state=123))
    ])

    print("\nEntrenando el modelo...")
    pipeline.fit(X_train, y_train)
    print("Modelo entrenado exitosamente.")

    print("\n Evaluación del Modelo")
    train_accuracy = pipeline.score(X_train, y_train)
    print(f"Precisión en el conjunto de Entrenamiento: {train_accuracy:.4f}")

    val_accuracy = pipeline.score(X_val, y_val)
    print(f"Precisión en el conjunto de Validación: {val_accuracy:.4f}")

    test_accuracy = pipeline.score(X_test, y_test)
    print(f"Precisión en el conjunto de Prueba: {test_accuracy:.4f}")

    # Guardar el modelo entrenado
    joblib.dump(pipeline, modelo_archivo)
    print(f"\nModelo entrenado y guardado como '{modelo_archivo}'")