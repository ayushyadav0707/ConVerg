import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

def convert_sqft_to_num(x):
    if not isinstance(x, str):
        return x
    tokens = x.split('-')
    if len(tokens) == 2:
        return (float(tokens[0]) + float(tokens[1])) / 2
    try:
        return float(x)
    except:
        return None

def clean_data(df):
    print("Cleaning dataset...")
    # Drop irrelevant columns to simplify
    cols_to_drop = ['area_type', 'society', 'balcony', 'availability']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
    
    df = df.dropna()
    
    # Extract integer from size (e.g. '2 BHK' -> 2)
    if 'size' in df.columns:
        df['bhk'] = df['size'].apply(lambda x: int(x.split(' ')[0]) if isinstance(x, str) else x)
        df = df.drop('size', axis=1)
        
    # Clean total_sqft which contains ranges like '2100 - 2850'
    if 'total_sqft' in df.columns:
        df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_num)
        df = df.dropna(subset=['total_sqft'])
        
    # Remove anomalies: properties with less than 300 sqft per bhk are unusual
    if 'total_sqft' in df.columns and 'bhk' in df.columns:
        df = df[~(df.total_sqft / df.bhk < 300)]
        
    # Clean location text and group rare locations into 'other'
    if 'location' in df.columns:
        df['location'] = df['location'].apply(lambda x: x.strip())
        location_stats = df['location'].value_counts(ascending=False)
        location_stats_less_than_10 = location_stats[location_stats <= 10]
        df['location'] = df['location'].apply(lambda x: 'other' if x in location_stats_less_than_10 else x)
        
    # Remove price per sqft outliers to improve model accuracy
    def remove_pps_outliers(df):
        df_out = pd.DataFrame()
        if 'price' not in df.columns or 'total_sqft' not in df.columns or 'location' not in df.columns:
            return df
        
        df['price_per_sqft'] = df['price'] * 100000 / df['total_sqft']
        for key, subdf in df.groupby('location'):
            m = np.mean(subdf.price_per_sqft)
            st = np.std(subdf.price_per_sqft)
            # Keep data within 1 standard deviation
            reduced_df = subdf[(subdf.price_per_sqft > (m - st)) & (subdf.price_per_sqft <= (m + st))]
            df_out = pd.concat([df_out, reduced_df], ignore_index=True)
        return df_out.drop('price_per_sqft', axis=1, errors='ignore')
        
    df = remove_pps_outliers(df)
    return df

def prepare_features(df):
    # One-Hot Encoding for categorical 'location' feature
    if 'location' in df.columns:
        dummies = pd.get_dummies(df['location'])
        # Drop one dummy to avoid multicollinearity trap (and 'other' class)
        if 'other' in dummies.columns:
            dummies = dummies.drop('other', axis=1)
        df = pd.concat([df.drop('location', axis=1), dummies], axis=1)
        
    y = df['price'].values
    X_df = df.drop('price', axis=1)
    
    return X_df, y

def newton_raphson_multivariate(X, y, lambda_reg=0.01):
    """
    Multivariate Newton-Raphson for Linear Regression
    Model: y = w1*x1 + w2*x2 + ... + wn*xn + b
    
    X: Feature matrix (N x D)
    y: Target vector (N,)
    lambda_reg: Small regularization to ensure Hessian is invertible
    """
    # Add bias column (ones) to X
    X_with_bias = np.c_[np.ones(X.shape[0]), X]
    N, D = X_with_bias.shape
    
    # Initialize parameters theta = [b, w1, w2, ..., wD]
    theta = np.zeros(D)
    
    # Hessian matrix = 2 * X^T * X
    XT_X = np.dot(X_with_bias.T, X_with_bias)
    
    # Add small regularization to diagonal to prevent singular matrix
    H = 2 * XT_X + lambda_reg * np.eye(D)
    
    try:
        H_inv = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        print("Hessian is singular, increasing regularization...")
        H = 2 * XT_X + (lambda_reg * 100) * np.eye(D)
        H_inv = np.linalg.inv(H)
        
    print(f"Optimizing {D} parameters (weights + bias) using Newton-Raphson...")
    
    # Converges in exactly 1 step for quadratic Error function
    y_pred = np.dot(X_with_bias, theta)
    error = np.sum((y - y_pred)**2)
    print(f"Initial Error (theta=0): {error:.2f}")
    
    # Gradient = -2 * X^T * (y - y_pred)
    G = -2 * np.dot(X_with_bias.T, (y - y_pred))
    
    # Newton-Raphson Update: theta_new = theta_old - H_inv * Gradient
    theta = theta - np.dot(H_inv, G)
        
    # Final Error
    y_pred_final = np.dot(X_with_bias, theta)
    final_error = np.sum((y - y_pred_final)**2)
    print(f"Final Error: {final_error:.2f} ---> Converged in 1 Step!\n")
    
    return theta

class HousePredictorModel:
    def __init__(self, dataset_path='bengaluru_house_prices.csv'):
        self.dataset_path = dataset_path
        self.theta = None
        self.columns = None
        
    def train(self):
        if not os.path.exists(self.dataset_path):
            print(f"Error: {self.dataset_path} not found.")
            return False
            
        print("Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        
        df_cleaned = clean_data(df)
        print(f"Data cleaned. Remaining samples after dropping outliers: {len(df_cleaned)}")
        
        X_df, y = prepare_features(df_cleaned)
        self.columns = X_df.columns
        X_mat = X_df.values.astype(float)
        
        self.theta = newton_raphson_multivariate(X_mat, y)
        print("Model trained successfully.")
        return True
        
    def predict_price(self, location, sqft, bath, bhk):
        """
        Function to predict price given custom parameters.
        Returns price in Lakhs.
        """
        if self.theta is None or self.columns is None:
            print("Model is not trained yet.")
            return None
            
        # Create a zero array for input matching our feature columns
        x = np.zeros(len(self.columns))
        
        # Set continuous variables
        if 'total_sqft' in self.columns:
            x[np.where(self.columns == 'total_sqft')[0][0]] = sqft
        if 'bath' in self.columns:
            x[np.where(self.columns == 'bath')[0][0]] = bath
        if 'bhk' in self.columns:
            x[np.where(self.columns == 'bhk')[0][0]] = bhk
            
        # Set categorical location variable to 1
        if location in self.columns:
            loc_index = np.where(self.columns == location)[0][0]
            x[loc_index] = 1
        elif 'other' in self.columns: # fallback
            loc_index = np.where(self.columns == 'other')[0][0]
            x[loc_index] = 1
            
        # Add 1 for the bias at index 0
        x_with_bias = np.insert(x, 0, 1)
        
        # Calculate dot product: theta * X
        price = np.dot(x_with_bias, self.theta)
        return price

if __name__ == "__main__":
    print("=== Bengaluru House Price Predictor (Newton-Raphson) ===\n")
    
    model = HousePredictorModel('bengaluru_house_prices.csv')
    success = model.train()
    
    if success:
        print("--- Interactive Prediction ---")
        # ========================================================
        # CHANGE THESE PARAMETERS TO TEST DIFFERENT HOUSE PREDICTIONS
        # ========================================================
        test_location = 'Whitefield'
        test_sqft = 1000
        test_bath = 2
        test_bhk = 2
        
        predicted_price = model.predict_price(test_location, test_sqft, test_bath, test_bhk)
        
        print(f"Inputs:")
        print(f"- Location: {test_location}")
        print(f"- Size: {test_sqft} sqft")
        print(f"- BHK: {test_bhk}")
        print(f"- Bathrooms: {test_bath}")
        print("-" * 20)
        print(f"PREDICTED PRICE: {predicted_price:.2f} Lakhs")
        print("========================================================\n")
        print("Tip: Modify the parameters in the code (line 144) to predict other houses!")
