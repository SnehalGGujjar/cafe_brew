import pandas as pd
from menu.ml_rf import train_random_forest, predict_topk

# 1) Prepare a CSV (see schema below)
df = pd.read_csv("orders_for_training.csv")

# 2) Train
result = train_random_forest(df, target_col="dish_name", model_path="menu_models/dish_rf.pkl")
print(result.accuracy, result.f1_macro)
print(result.report)

# 3) Predict for today’s context (one or many rows)
X = pd.DataFrame([{
    "temperature": 31.2,
    "precipitation": 0.0,
    "hour": 13,
    "weekday": 2,               
    "condition": "hot",
    "location_label": "Cafeteria A",
    "is_weekend": 0
}])

ranked = predict_topk(X, model_path="menu_models/dish_rf.pkl", top_k=5)
print(ranked[0])  
