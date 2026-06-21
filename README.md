# 🏡 House Price Predictor
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)

A full-stack web application that predicts real estate prices for properties in Bengaluru based on features like location, square footage, BHK, etc.  

## ✨ Key Features & Plus Points

* **Custom Math Algorithm**: Instead of relying on standard black-box libraries, the prediction engine is built from scratch using **Multivariate Linear Regression** optimized via the **Newton-Raphson Method** for high efficiency.

* **Transparent Pricing**: The app doesn't just give you a price—it provides a mathematical breakdown of how each feature (e.g., balconies, bathrooms, location) influenced the final estimate.

* **Automated Data Cleaning**: Automatically handles missing values, removes extreme outliers, and encodes categorical text data.

* **Modern Tech Stack**: 
  * **Frontend**: Fast, responsive UI built with **React** and **Vite**.
  * **Backend**: Lightweight API powered by **Python** and **Flask**.

## 🚀 Quick Start

### 1. Backend Server
```bash
cd backend
python -m venv venv     # Optional: Create virtual environment
pip install -r requirements.txt
python app.py           # Starts on http://localhost:5000 and trains the model
```

### 2. Frontend Website
```bash
cd frontend
npm install
npm run dev             # Starts on http://localhost:5173
```
