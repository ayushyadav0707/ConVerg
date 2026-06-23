# ConVerg: House Price Predictor - Full Project Context

This document provides a comprehensive overview of the `ConVerg` repository. It is designed to be provided as context to Claude or any other AI assistant to understand the complete architecture, tech stack, directory structure, and mathematical algorithms used in the project.

---

## 1. Project Overview
**ConVerg** is a web application that predicts real estate prices for properties in Bengaluru based on parameters such as location, square footage, BHK, bathrooms, and area type.

**Core Differentiator**: Instead of using high-level machine learning libraries like `scikit-learn` for the core inference, the mathematical engine (Multivariate Linear Regression) is implemented entirely from scratch using `NumPy`. The optimization relies on the second-order **Newton-Raphson Method**, ensuring exact convergence to the global minimum efficiently. It also provides **Transparent Pricing**, sending a mathematical breakdown to the frontend detailing exactly how much each feature contributed to the final price.

## 2. Technology Stack
- **Backend & Serving**: Python, Flask, Gunicorn
- **Mathematical Engine**: NumPy (built from scratch, no `scikit-learn` inference)
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, Flask Server-Side Templates (Jinja2)
- **Deployment**: Vercel (via `vercel.json`)

## 3. Directory Structure
The entire application operates as a monolithic Flask application residing in the `new_backend/` folder.

```text
House-Price-Predictor/
├── .gitignore
├── requirements.txt         # Project dependencies (flask, numpy, flask-cors, gunicorn)
├── README.md                # Project README
├── PROJECT_REPORT.md        # Detailed documentation on system architecture
├── overview.md              # Mathematical explanation of the algorithms
└── new_backend/
    ├── app.py               # Main Flask API and Template Serving
    ├── data_processor.py    # Data cleaning, outlier filtering, standard scaling
    ├── optimizer.py         # Custom Newton-Raphson optimization class
    ├── train.py             # Script that trains the model and saves weights
    ├── model_weights.json   # The generated JSON file storing the model's Theta parameters
    ├── data/
    │   └── bengaluru_house_prices_cleaned.csv  # The static dataset
    ├── static/              # CSS, JS, Images
    │   ├── css/style.css
    │   ├── js/main.js       # Handles frontend interactivity and API requests
    │   └── images/logo.png.png
    └── templates/           # HTML views
        ├── index.html       # Landing page
        ├── about.html       # About page
        ├── how_it_works.html# How it works documentation
        └── predictor.html   # Main application interface
```

## 4. Core Components Deep Dive

### 4.1 Data Processing (`new_backend/data_processor.py`)
- **Input Parsing**: Handles string manipulation for ranges (e.g., `"2100 - 2850"`) and removes weird units (e.g., "Sq. Meter", "Acres") to extract pure numbers.
- **Outlier Filtering**: Drops rows where the square foot per bedroom is extremely low (`< 300` sqft/bhk). Drops rows that are wildly outside the normal price-per-sqft distribution (keeping the 5th to 90th percentiles).
- **Feature Engineering**: Calculates `sqft_per_bhk` and `bath_per_bhk`.
- **Categorical Encoding**: Identifies locations appearing less than 10 times and categorizes them as `'Other'`. Uses `pd.get_dummies` to one-hot encode locations and area types.
- **Scaling**: Uses `StandardScaler` on purely numeric features (leaving one-hot encoded variables untouched to prevent sparse matrix explosion). Adds a Bias/Intercept column of `1.0`.

### 4.2 Mathematical Optimization (`new_backend/optimizer.py`)
- Implements `NewtonRaphsonRegressor`.
- Calculates the Gradient: `G = (-2 / N) * X^T * (Y - Y_pred) + 2 * lambda * theta`
- Calculates the Hessian (second derivative): `H = (2 / N) * X^T * X + 2 * lambda * I`
- Uses L2 (Ridge) Regularization (the `lambda` factor) by adding an identity matrix to the Hessian to prevent singularity errors caused by multicollinearity in the one-hot encoded locations.
- Performs the update: `theta_new = theta_old - inv(H) · G` (Using `np.linalg.solve`).

### 4.3 Training Pipeline (`new_backend/train.py`)
- Pulls data using `load_and_preprocess()`.
- Instantiates the `NewtonRaphsonRegressor(l2_penalty=1e-4)`.
- Evaluates metrics (RMSE, MAE, R²) on the test set.
- Dumps the scaler means/variances, the feature column names, and the trained Theta weights into a `model_weights.json` file.

### 4.4 API & Inference (`new_backend/app.py`)
- On startup, the script loads `model_weights.json` directly into memory.
- It parses the `columns` array to extract all available "locations" and "area_types" to inject into the `predictor.html` Jinja template.
- **The `/predict` Endpoint**:
  1. Accepts JSON with `sqft`, `bhk`, `bath`, `balcony`, `location`, `area_type`.
  2. Constructs an empty vector matching the trained feature columns.
  3. Fills in the numeric values and sets `1.0` for the corresponding categorical dummy columns.
  4. Manually applies standard scaling to the numeric segment of the vector using the `mean` and `scale` loaded from the JSON.
  5. Performs the dot product: `pred_price = np.dot(x_final, theta)`.
  6. Calculates the `breakdown` array, computing exactly how much `weight * scaled_value` each feature contributed to the final price.

### 4.5 Frontend (`new_backend/static/js/main.js`)
- Persists user inputs to `localStorage` (using keys like `conVerg_location`) so they aren't lost on refresh.
- Fetches the `/predict` API on form submit.
- Dynamically renders the total price.
- Maps over the returned `breakdown` array to render an "Explainable AI" table showing the positive or negative financial contribution of every feature.

## 5. Deployment Setup
- The application is configured to deploy directly to Vercel via a monolithic Python runtime setup.
- The `vercel.json` maps `new_backend/app.py` to `@vercel/python`.
- **Note**: The repository MUST cleanly install dependencies via `pip install -r requirements.txt`. The repository does NOT track the `__pycache__` folder.

---

### End of Context
*You now have complete situational awareness of the ConVerg project architecture. You may use this context to write code, debug issues, or propose new features.*
