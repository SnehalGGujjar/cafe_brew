# menu/ml_rf.py
"""
Random Forest training + inference for dish prediction.

Expected training DataFrame columns (you can have more; unknowns are ignored):
- target column (string/categorical): 'dish_name'  (or change via target_col)
- numeric: 'temperature', 'precipitation', 'hour', 'weekday'
- categorical: 'condition' (any/hot/cold/rain/clear), 'location_label'
- optional binary: 'is_weekend', 'is_holiday' (0/1)
- (add more feature columns freely; categorical & numeric are auto-detected)

Outputs:
- Trained model saved as a .pkl
- Holdout metrics printed (accuracy, macro F1, classification report)
- Feature importances accessor
"""

from __future__ import annotations
import os
import joblib
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Tuple

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score

@dataclass
class TrainResult:
    model_path: str
    classes_: List[str]
    accuracy: float
    f1_macro: float
    report: str
    feature_names: List[str]
    rf_feature_importances_: Optional[np.ndarray] = None


def _infer_column_types(df: pd.DataFrame, target_col: str) -> Tuple[List[str], List[str]]:
    """Pick numeric vs categorical feature columns automatically."""
    feature_cols = [c for c in df.columns if c != target_col]
    numeric_cols, cat_cols = [], []
    for c in feature_cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_cols.append(c)
        else:
            cat_cols.append(c)
    return numeric_cols, cat_cols


def build_pipeline(
    numeric_cols: List[str],
    cat_cols: List[str],
    n_estimators: int = 400,
    max_depth: Optional[int] = None,
    random_state: int = 42,
) -> Pipeline:
    """
    Preprocessing:
      - numeric: passthrough
      - categorical: OneHotEncoder(handle_unknown='ignore')

    Model:
      - RandomForestClassifier(class_weight='balanced_subsample')
    """
    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ],
        remainder="drop",
    )

    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        n_jobs=-1,
        random_state=random_state,
        class_weight="balanced_subsample",
    )

    pipe = Pipeline(steps=[("pre", pre), ("clf", rf)])
    return pipe


def train_random_forest(
    df: pd.DataFrame,
    target_col: str = "dish_name",
    model_path: str = "menu_models/dish_rf.pkl",
    test_size: float = 0.2,
    random_state: int = 42,
    n_estimators: int = 400,
    max_depth: Optional[int] = None,
) -> TrainResult:
    """
    Train and persist a RandomForest classifier. Returns metrics and metadata.
    """
    # Clean rows with missing target
    df = df.copy()
    df = df[~df[target_col].isna()]
    df[target_col] = df[target_col].astype(str)

    # Basic imputations for simplicity
    for c in df.columns:
        if c == target_col:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].astype(float)
            df[c] = df[c].fillna(df[c].median())
        else:
            df[c] = df[c].astype(str).fillna("")

    y = df[target_col].values
    X = df.drop(columns=[target_col])

    numeric_cols, cat_cols = _infer_column_types(df, target_col)
    pipe = build_pipeline(numeric_cols, cat_cols, n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    pipe.fit(X_train, y_train)

    # Evaluation
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1m = f1_score(y_test, y_pred, average="macro")
    report = classification_report(y_test, y_pred)

    # Optional: quick CV
    try:
        cv_acc = cross_val_score(pipe, X, y, cv=5, scoring="accuracy", n_jobs=-1).mean()
        print(f"[CV] Mean Accuracy (5-fold): {cv_acc:.4f}")
    except Exception:
        pass

    # Persist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"pipeline": pipe, "target_col": target_col, "classes_": sorted(np.unique(y))}, model_path)

    # Derive expanded feature names for importances (optional)
    feature_names = []
    rf_importances = None
    try:
        # Pull preprocessor and RF
        pre: ColumnTransformer = pipe.named_steps["pre"]
        rf: RandomForestClassifier = pipe.named_steps["clf"]

        # Build feature name list (numeric + expanded categorical)
        num_names = numeric_cols
        cat_encoder: OneHotEncoder = pre.named_transformers_["cat"]
        cat_names = []
        if cat_cols:
            # scikit-learn ≥1.1 uses get_feature_names_out
            cat_names = cat_encoder.get_feature_names_out(cat_cols).tolist()
        feature_names = num_names + cat_names

        if hasattr(rf, "feature_importances_"):
            rf_importances = rf.feature_importances_
    except Exception:
        pass

    return TrainResult(
        model_path=model_path,
        classes_=sorted(np.unique(y)),
        accuracy=acc,
        f1_macro=f1m,
        report=report,
        feature_names=feature_names,
        rf_feature_importances_=rf_importances,
    )


def load_model(model_path: str = "menu_models/dish_rf.pkl"):
    obj = joblib.load(model_path)
    return obj["pipeline"], obj["target_col"], obj["classes_"]


def predict_topk(
    X: pd.DataFrame,
    model_path: str = "menu_models/dish_rf.pkl",
    top_k: int = 5,
) -> List[List[Tuple[str, float]]]:
    """
    Returns a per-row ranked list of (dish, probability) of length top_k.
    """
    pipe, _, classes_ = load_model(model_path)
    proba = pipe.predict_proba(X)  # shape [n_samples, n_classes]
    classes = list(classes_)

    results: List[List[Tuple[str, float]]] = []
    for row in proba:
        idx = np.argsort(row)[::-1][:top_k]
        results.append([(classes[i], float(row[i])) for i in idx])
    return results
