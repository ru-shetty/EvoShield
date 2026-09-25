"""
Training script for M02 - Malicious URL Analysis.

Uses the real malicious_phish.csv dataset and trains
a character-level TF-IDF URL classifier.
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "malicious_phish.csv"

MODEL_PATH = (
    BASE_DIR
    / "algorithms"
    / "artifacts"
    / "url_model.joblib"
)


# -------------------------------------------------------------------
# URL cleaning
# -------------------------------------------------------------------

def clean_url(url: str) -> str:
    """
    Convert URL into a clean string representation.

    The URL is kept mostly unchanged because the character-level
    model learns useful patterns directly from the URL structure.
    """

    if pd.isna(url):
        return ""

    return str(url).strip().lower()


# -------------------------------------------------------------------
# Main training function
# -------------------------------------------------------------------

def main():

    print("=" * 70)
    print("M02 - MALICIOUS URL MODEL TRAINING")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------------

    print("\n[1/6] Loading dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset loaded successfully.")
    print(f"Total rows: {len(df):,}")

    # ---------------------------------------------------------------
    # Validate columns
    # ---------------------------------------------------------------

    required_columns = {"url", "type"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ---------------------------------------------------------------
    # Clean data
    # ---------------------------------------------------------------

    print("\n[2/6] Cleaning dataset...")

    df = df.dropna(
        subset=["url", "type"]
    ).copy()

    df["url"] = df["url"].apply(clean_url)

    df["type"] = (
        df["type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df[df["url"] != ""]

    # Remove duplicate URLs.
    # This prevents identical URLs from appearing in both
    # training and testing data.
    df = df.drop_duplicates(
        subset=["url"],
        keep="first",
    )

    print(f"Rows after cleaning: {len(df):,}")

    # ---------------------------------------------------------------
    # Display original classes
    # ---------------------------------------------------------------

    print("\nOriginal dataset classes:")

    print(
        df["type"].value_counts()
    )

    # ---------------------------------------------------------------
    # Convert to binary classification
    # ---------------------------------------------------------------

    print("\n[3/6] Creating binary labels...")

    # SAFE:
    #     benign -> 0
    #
    # MALICIOUS:
    #     phishing -> 1
    #     malware -> 1
    #     defacement -> 1

    df["label"] = (
        df["type"] != "benign"
    ).astype(int)

    print("\nBinary class distribution:")

    print(
        df["label"]
        .value_counts()
        .rename(
            index={
                0: "SAFE / benign",
                1: "MALICIOUS",
            }
        )
    )

    # ---------------------------------------------------------------
    # Train/test split
    # ---------------------------------------------------------------

    print("\n[4/6] Splitting dataset...")

    X = df["url"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Training URLs: {len(X_train):,}")
    print(f"Testing URLs:  {len(X_test):,}")

    # ---------------------------------------------------------------
    # Character-level TF-IDF
    # ---------------------------------------------------------------

    print("\n[5/6] Building character-level TF-IDF features...")

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=2,
        max_features=200000,
        sublinear_tf=True,
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )

    X_test_tfidf = vectorizer.transform(
        X_test
    )

    print(
        f"Training feature matrix: "
        f"{X_train_tfidf.shape}"
    )

    print(
        f"Testing feature matrix: "
        f"{X_test_tfidf.shape}"
    )

    # ---------------------------------------------------------------
    # Train classifier
    # ---------------------------------------------------------------

    print("\nTraining Logistic Regression model...")

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
        solver="liblinear",
    )

    model.fit(
        X_train_tfidf,
        y_train,
    )

    # ---------------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------------

    print("\n[6/6] Evaluating model...")

    predictions = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "SAFE / benign",
                "MALICIOUS",
            ],
            digits=4,
        )
    )

    # ---------------------------------------------------------------
    # Save model
    # ---------------------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
            "model_type": "character_tfidf_logistic_regression",
            "classes": {
                0: "SAFE",
                1: "MALICIOUS",
            },
            "dataset_classes": [
                "benign",
                "phishing",
                "malware",
                "defacement",
            ],
        },
        MODEL_PATH,
    )

    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)

    print(
        f"\nModel saved successfully at:\n{MODEL_PATH}"
    )


if __name__ == "__main__":
    main()