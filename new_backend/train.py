import os
import json
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from data_processor import load_and_preprocess
from optimizer import NewtonRaphsonRegressor

def evaluate_metrics(y_true, y_pred):
    # Ensure no negative prices
    y_pred = np.clip(y_pred, a_min=0.0, a_max=None)
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'bengaluru_house_prices_cleaned.csv')
    
    X_train, X_test, y_train, y_test, columns, scaler = load_and_preprocess(data_path)
    print(f"Data shape: Train {X_train.shape}, Test {X_test.shape}")
    
    # Train Newton-Raphson
    # Using L2 penalty ensures the Hessian is perfectly positive-definite and invertible.
    # Because OLS is a quadratic surface, Newton-Raphson converges to the global minimum in EXACTLY 1 step.
    # We run 3 epochs just to demonstrate the gradient vanishing to zero.
    print("\n--- Training Exact Newton-Raphson Optimizer ---")
    model = NewtonRaphsonRegressor(l2_penalty=0.01, epochs=3)
    model.fit(X_train, y_train)
    
    # Predict and evaluate on unseen Test set
    y_pred_test = model.predict(X_test)
    rmse, mae, r2 = evaluate_metrics(y_test, y_pred_test)
    
    print("\n--- Final Test Metrics ---")
    print(f"RMSE: {rmse:.4f} Lakhs")
    print(f"MAE:  {mae:.4f} Lakhs")
    print(f"R²:   {r2:.4f}")
    
    # Save weights and config
    weights_path = os.path.join(base_dir, 'model_weights.json')
    output = {
        'columns': columns,
        'theta_nr': model.theta.tolist(),
        'history': model.history,
        'metrics': {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2)
        }
    }
    with open(weights_path, 'w') as f:
        json.dump(output, f)
    print(f"\nModel strictly successfully built! Weights saved to {weights_path}")

if __name__ == "__main__":
    main()
