# 🏡 ConVerg: House Price Predictor

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)

**ConVerg** is a full-stack web application that predicts real estate prices for properties in Bengaluru based on features like location, square footage, BHK, and more.

What sets this project apart is its **custom mathematical foundation**. Instead of relying on standard machine learning libraries (like `scikit-learn`) for the core inference, the prediction engine is built entirely from scratch using **Multivariate Linear Regression** optimized via the **Newton-Raphson Method** for high efficiency and transparent pricing.

## ✨ Key Features & Plus Points

* **Custom Math Algorithm**: Built from scratch using NumPy. The algorithm uses a second-order optimization method (Newton-Raphson) that converges to the absolute minimum in a single step due to the perfectly quadratic nature of the cost function.
* **Transparent Pricing**: The app doesn't just give you a price—it provides a mathematical breakdown of how each feature (e.g., balconies, bathrooms, location) positively or negatively influenced the final estimate.
* **Modern Architecture**: A monolithic Flask application rendering server-side HTML templates (`new_backend/`), providing a fast and responsive UI without the overhead of heavy JavaScript frameworks.

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/ayushyadav0707/House-Price-Predictor.git
cd House-Price-Predictor
pip install -r requirements.txt
```

### 2. Running the Application

The entire application (frontend + backend API) is served via a single Flask server. Start the server from the `new_backend` directory:

```bash
cd new_backend
python app.py
```

The application will start on `http://127.0.0.1:5000`. Open this URL in your browser to access the ConVerg House Price Predictor.

## 📚 Documentation

For a deep dive into the architecture and mathematical optimization algorithms used in this project, check out:
- [Algorithm Overview](overview.md): Detailed explanation of the Newton-Raphson vs Gradient Descent algorithms.
- [Detailed Project Report](PROJECT_REPORT.md): Information regarding the system architecture, presentation layer, and security measures.
