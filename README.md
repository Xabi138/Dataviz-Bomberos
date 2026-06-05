# Análisis de Intervenciones de Bomberos en Bizkaia

Visualización interactiva de datos sobre 69,423 intervenciones del Servicio de Prevención, Extinción de Incendios y Salvamento (SPEIS) de Bizkaia realizadas entre 2021 y 2025.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar o descargar el repositorio

2. Instalar las dependencias:

pip install -r requirements.txt

o de forma manual:

pip install pandas numpy plotly dash

3. Ejecutar desde la terminal, en el directorio del proyecto:

python app.py

4. Aparecerá un mensaje indicando donde está la visualización, similar a este:

Dash is running on http://127.0.0.1:2071/

5. En ese caso se debe acceder en un navegador a http://127.0.0.1:2071

## Estructura

├── app.py              # Aplicación principal
├── bomberos.csv        # Dataset de intervenciones
├── requirements.txt    # Dependencias del proyecto
└── README.md          # Este archivo, con instrucciones de instalación

## Fuente de datos

Los datos provienen del catálogo abierto de la Diputación Foral de Bizkaia:
[Intervenciones del SPEIS](https://www.opendatabizkaia.eus/es/catalogo/intervenciones-speis)

El catalogo de datos ha sido integrado, limpiado y procesado para obtener el dataset utilizado.

Xabier Rodríguez - Visualización de Datos - Máster de Ciencia de Datos - UOC
Código con fines educacionales.
