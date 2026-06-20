import numpy as np

class NewtonRaphsonRegressor:
    """
    Exact Multivariate Newton-Raphson Optimization for Mean Squared Error
    with L2 (Ridge) Regularization for numerical stability.
    """
    def __init__(self, l2_penalty=0.1, epochs=3):
        self.l2_penalty = l2_penalty
        self.epochs = epochs
        self.theta = None
        self.history = []

    def fit(self, X, y):
        n_samples, n_features = X.shape
        # Initialize theta
        self.theta = np.zeros(n_features)
        
        # Identity matrix for regularization (excluding bias term at index 0)
        I = np.eye(n_features)
        I[0, 0] = 0.0 
        
        for epoch in range(self.epochs):
            # 1. Predictions
            y_pred = X @ self.theta
            
            # 2. Cost (MSE + L2 Regularization term)
            mse = np.mean((y - y_pred)**2)
            l2_cost = self.l2_penalty * np.sum(self.theta[1:]**2)
            cost = mse + l2_cost
            self.history.append({'epoch': epoch+1, 'cost': float(cost)})
            
            # 3. First Derivative (Gradient)
            # G = -2/N * X^T (Y - Y_pred) + 2 * lambda * theta
            gradient = (-2.0 / n_samples) * (X.T @ (y - y_pred)) + 2.0 * self.l2_penalty * (I @ self.theta)
            
            # 4. Second Derivative (Hessian)
            # H = 2/N * X^T X + 2 * lambda * I
            hessian = (2.0 / n_samples) * (X.T @ X) + 2.0 * self.l2_penalty * I
            
            # 5. Newton-Raphson Update Step
            # theta_new = theta_old - inv(H) @ G
            # Note: We use np.linalg.solve for better numerical stability instead of explicit inversion
            step = np.linalg.solve(hessian, gradient)
            self.theta = self.theta - step
            
            print(f"Epoch {epoch+1}/{self.epochs} - Cost: {cost:.6f} - Gradient Norm: {np.linalg.norm(gradient):.6f}")
            
    def predict(self, X):
        return X @ self.theta
