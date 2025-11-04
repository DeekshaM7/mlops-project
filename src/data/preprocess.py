import argparse
import os
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.utils.io import ensure_dir, load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess water potability dataset")
    parser.add_argument("--params", type=str, required=True, help="Path to params.yaml")
    return parser.parse_args()


def split_train_val_test(
    data: pd.DataFrame,
    target_column: str,
    test_size: float,
    val_size: float,
    random_state: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from sklearn.model_selection import train_test_split

    train_val, test = train_test_split(
        data,
        test_size=test_size,
        random_state=random_state,
        stratify=data[target_column],
    )
    relative_val_size = val_size / (1.0 - test_size)
    train, val = train_test_split(
        train_val,
        test_size=relative_val_size,
        random_state=random_state,
        stratify=train_val[target_column],
    )
    return train, val, test


def main() -> None:
    args = parse_args()
    params = load_yaml(args.params)

    raw_path = params["data"]["raw_path"]
    processed_dir = params["data"]["processed_dir"]
    target_column = params["data"]["target_column"]
    imp_strategy = params["preprocess"]["imputation_strategy"]
    scale = params["preprocess"]["scale"]
    test_size = float(params["preprocess"]["test_size"])
    val_size = float(params["preprocess"]["val_size"])
    random_state = int(params["preprocess"]["random_state"])

    df = pd.read_csv(raw_path)
    # Ensure consistent column names (Kaggle dataset uses lowercase sometimes)
    if target_column not in df.columns:
        alt = target_column.lower()
        if alt in df.columns:
            df.rename(columns={alt: target_column}, inplace=True)

    feature_columns = [c for c in df.columns if c != target_column]
    train_df, val_df, test_df = split_train_val_test(
        df, target_column, test_size, val_size, random_state
    )

    # Build preprocessing pipeline
    numeric_features = feature_columns
    numeric_transformer_steps = [("imputer", SimpleImputer(strategy=imp_strategy))]
    if scale:
        numeric_transformer_steps.append(("scaler", StandardScaler()))

    preprocess_pipe = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=numeric_transformer_steps), numeric_features)
        ]
    )

    X_train = train_df[feature_columns]
    y_train = train_df[target_column]
    X_val = val_df[feature_columns]
    y_val = val_df[target_column]
    X_test = test_df[feature_columns]
    y_test = test_df[target_column]

    X_train_t = preprocess_pipe.fit_transform(X_train)
    X_val_t = preprocess_pipe.transform(X_val)
    X_test_t = preprocess_pipe.transform(X_test)

    # Save processed datasets
    ensure_dir(processed_dir)
    train_out = os.path.join(processed_dir, "train.csv")
    val_out = os.path.join(processed_dir, "val.csv")
    test_out = os.path.join(processed_dir, "test.csv")

    # Concatenate target back for storage
    train_proc = pd.DataFrame(
        X_train_t, columns=[f"f_{i}" for i in range(X_train_t.shape[1])]
    )
    train_proc[target_column] = y_train.values
    val_proc = pd.DataFrame(
        X_val_t, columns=[f"f_{i}" for i in range(X_val_t.shape[1])]
    )
    val_proc[target_column] = y_val.values
    test_proc = pd.DataFrame(
        X_test_t, columns=[f"f_{i}" for i in range(X_test_t.shape[1])]
    )
    test_proc[target_column] = y_test.values

    train_proc.to_csv(train_out, index=False)
    val_proc.to_csv(val_out, index=False)
    test_proc.to_csv(test_out, index=False)

    # Save transformer for inference
    transformer_out = os.path.join(processed_dir, "transformer.joblib")
    joblib.dump(preprocess_pipe, transformer_out)
    print(
        f"Saved processed datasets to {processed_dir} and transformer to {transformer_out}"
    )


if __name__ == "__main__":
    main()
