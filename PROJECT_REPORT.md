# ConVerg: House Price Predictor - Detailed Project Report

## 1. Project Overview
**ConVerg** is a full-stack web application that predicts real estate prices for properties in Bengaluru based on features like location, square footage, and BHK (Bedrooms, Hall, Kitchen). 

What sets this project apart is its **custom mathematical foundation**. Instead of relying on standard machine learning libraries (like `scikit-learn`) for the core inference, the prediction engine is built entirely from scratch using **Multivariate Linear Regression** optimized via the **Newton-Raphson Method** for high efficiency and transparent pricing.

---

## 2. System Architecture & Components

### 2.1 Database Schema Design
**Status: N/A (Static File-Based)**
This project currently does not use a traditional relational database (like PostgreSQL or MySQL) or a NoSQL database. 
- **Data Source**: It relies on a pre-processed static dataset (`data/bengaluru_house_prices_cleaned.csv`).
- **Storage Strategy**: During the training phase (`train.py`), the dataset is loaded directly into memory using Pandas for data manipulation.
- **Model Storage**: Once the mathematical model is trained, the resulting weights (Theta parameters), scaling factors, and column names are saved to a static JSON file (`model_weights.json`). The backend API directly loads this JSON file into memory on startup for lightning-fast inference without needing a database connection.

### 2.2 Authentication and Onboarding Flow
**Status: N/A (Public Tool)**
Currently, the application is designed as a public-facing utility. There is no user authentication (OAuth, JWT, or sessions) or onboarding flow. Users can access the web application and immediately start entering property parameters to get price predictions.

### 2.3 Real-Time Features
**Status: N/A (Stateless REST API)**
There are no real-time WebSocket connections or push notifications. The architecture is a traditional stateless request-response model:
1. The user clicks "Predict" on the frontend.
2. The frontend sends a single synchronous `POST` HTTP request to the Flask backend.
3. The backend calculates the price and returns a JSON response immediately.

### 2.4 Presentation Layer
**Technology Stack:** HTML, CSS, Vanilla JavaScript, Flask Templates (Jinja2)
- **Frontend Architecture**: The active codebase uses server-side rendered HTML templates via Flask (the React codebase mentioned in the README is not present).
- **Pages**:
  - `index.html`: The landing page with a hero section emphasizing the mathematical transparency of the tool.
  - `predictor.html`: The core application interface where users select property attributes (Location, Area Type, BHK, Bathrooms, SqFt).
- **Styling**: Custom CSS stored in the `static/css` directory.
- **Interactivity**: Vanilla JavaScript handles form submission, payload construction, and dynamically displaying the predicted price and the mathematical breakdown sent from the backend.

### 2.5 Security Layer
**Technology Stack:** Flask CORS, Input Sanitization, Mathematical Regularization
While there is no authentication, the system implements basic security and stability measures:
- **CORS Protection**: The backend utilizes `flask-cors` (`CORS(app)`) to explicitly manage cross-origin requests, ensuring the API is securely accessed by the frontend.
- **Input Validation & Clipping**: The `/predict` endpoint uses `try...except` blocks to handle malformed JSON requests gracefully. It ensures mathematical validity by defaulting missing values and using `max(0.0, float(pred_price))` to prevent impossible negative property prices.
- **Algorithm Stability (L2 Regularization)**: To prevent mathematical "explosions" (singular matrix errors) caused by multicollinear one-hot encoded variables (like location data), the optimizer uses Ridge (L2) Regularization. This acts as a mathematical security layer ensuring stable model weights.

---

## 3. Core Machine Learning Architecture
The backend is highly sophisticated, focusing on algorithm transparency.
- **Data Preprocessing** (`data_processor.py`): Performs custom outlier filtering (e.g., ensuring standard square-footage per bedroom), Z-score standardization for numeric features, and one-hot encoding for categorical variables.
- **Optimization Algorithm** (`optimizer.py`): Implements an exact multivariate **Newton-Raphson Optimization** algorithm from scratch using `NumPy`. Because the loss surface of Mean Squared Error is perfectly quadratic, this algorithm converges to the global minimum almost instantly.
- **Inference & Transparency** (`app.py`): The prediction endpoint (`/predict`) doesn't just output a single price number. It calculates the mathematical dot product of the input vector and the model weights, and returns a **transparent mathematical breakdown**. This allows the user to see exactly how much each feature (e.g., having an extra bathroom) added or subtracted from the final home price.

## 4. API Endpoints
- `GET /` : Serves the main landing page.
- `GET /predictor` : Serves the prediction dashboard and dynamically populates location dropdowns.
- `POST /predict` : Expects a JSON payload with property features (`sqft`, `bhk`, `bath`, `balcony`, `location`, `area_type`) and returns the predicted `price_lakhs` along with the mathematical `breakdown`.
