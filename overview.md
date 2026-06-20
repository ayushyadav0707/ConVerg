# ConVerg Backend: Algorithm Overview

The backend of the ConVerg House Price Predictor is built entirely from scratch in Python (using NumPy) without relying on standard machine learning libraries like `scikit-learn`. The core feature is the implementation and comparison of two distinct mathematical optimization algorithms to solve the Multivariate Linear Regression problem.

---

## 1. Newton-Raphson Optimization

The Newton-Raphson method is a powerful second-order optimization algorithm. Because the cost function for Linear Regression (Mean Squared Error) is perfectly quadratic, Newton-Raphson is capable of finding the absolute optimal weights in just a single step.

### Implementation Details:
- **Matrix Operations:** We append a column of ones to the feature matrix `X` to account for the bias parameter (intercept).
- **Hessian Matrix ($H$):** We compute the second derivative of the cost function, which determines the curvature of the loss surface. The formula is `H = 2 * X^T * X`.
- **L2 Regularization (Ridge):** Because the dataset is heavily One-Hot Encoded (e.g., locations, area types), the features suffer from multicollinearity. This causes the Hessian to become non-invertible (singular). We solve this by adding a small identity matrix `lambda_reg * np.eye(D)` to the diagonal of the Hessian.
- **Update Rule:** The algorithm jumps directly to the minimum by computing the Gradient ($G$) and multiplying it by the inverse of the Hessian: 
  `theta_new = theta_old - H_inv · G`
- **Iteration:** Although theoretically it solves linear regression in 1 step, we implemented a loop with a strict tolerance (`tol=1e-4`) to track exactly how many epochs it takes to fully satisfy convergence.

---

## 2. Gradient Descent Optimization

Gradient descent is a first-order optimization algorithm that iteratively takes small steps against the slope of the error curve to slowly find the minimum.

### Implementation Details:
- **Feature Scaling (Crucial Step):** Real estate data contains features of vastly different magnitudes (e.g., `total_sqft` is in the thousands, while `bath` is 1-5). Standard Gradient Descent will easily explode or take millions of epochs to converge on unscaled data. Inside `gradient_descent_multivariate`, we apply Z-score standardization: `X_scaled = (X - Mean) / StdDev`.
- **Iterative Updates:** In a loop, we calculate the Gradient of the Mean Squared Error: `G = (-2 / N) * X^T * (Y - Y_pred)`. We then update the weights by subtracting a fraction (Learning Rate `alpha`) of the Gradient.
- **Early Stopping:** Just like Newton-Raphson, we track the change in Mean Squared Error at every epoch. If the improvement is smaller than our tolerance (`tol=1e-4`), we halt the training.
- **Unscaling the Weights:** To make the Gradient Descent model directly comparable to the Newton-Raphson model, we mathematically "unscale" the finalized weights at the very end. This allows the API to use the exact same raw user input for both models during the final price prediction, avoiding the need to scale data during the inference phase!
