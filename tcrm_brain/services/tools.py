import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import uuid
import os

# Ensure static directory exists for saving plots
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def trend_plot_tool(df: pd.DataFrame, x_col: str, y_col: str, plot_type: str = "line") -> str:
    """
    Generates a chart from a DataFrame and returns the file path.
    """
    plt.figure(figsize=(10, 6))
    
    # Simple error handling if columns don't exist
    if x_col not in df.columns or y_col not in df.columns:
        return f"Error: Columns {x_col} or {y_col} not found in data."

    if plot_type == "line":
        sns.lineplot(data=df, x=x_col, y=y_col)
    elif plot_type == "bar":
        sns.barplot(data=df, x=x_col, y=y_col)
    
    plt.title(f"{plot_type.capitalize()} Plot of {y_col} vs {x_col}")
    
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return filepath

def prediction_tool(df: pd.DataFrame, feature_col: str, target_col: str) -> str:
    """
    Trains a simple Linear Regression model and returns a prediction explanation.
    """
    try:
        if feature_col not in df.columns or target_col not in df.columns:
            return f"Error: Columns {feature_col} or {target_col} not found."
            
        # Clean data
        df_clean = df[[feature_col, target_col]].dropna()
        if df_clean.empty:
            return "Not enough data for prediction."

        X = df_clean[[feature_col]].values
        y = df_clean[target_col].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next value (simple extrapolation: last_value + mean_step or just +1 if it implies time/seq)
        # For simplicity, we just look at the last X value and add 1 unit (assuming time/index like).
        last_val = X[-1][0]
        next_val = np.array([[last_val + 1]]) 
        prediction = model.predict(next_val)[0]
        
        return f"Based on linear regression of {feature_col}, the predicted next value for {target_col} (at {last_val+1}) is approximately {prediction:.2f}. " \
               f"(Model Coeff: {model.coef_[0]:.2f})"
    except Exception as e:
        return f"Prediction failed: {str(e)}"

def report_tool(df: pd.DataFrame, format: str = "csv") -> str:
    """
    Saves the DataFrame to a file and returns the path.
    """
    filename = f"{uuid.uuid4()}.{format}"
    filepath = os.path.join(STATIC_DIR, filename)
    
    if format == "csv":
        df.to_csv(filepath, index=False)
    elif format == "excel" or format == "xlsx":
        df.to_excel(filepath, index=False)
        
    return filepath
