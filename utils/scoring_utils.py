import pandas as pd
from xgboost import XGBClassifier
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import shap
#"C:\Users\kyan so\OneDrive\Documents\Z_Personal\Microfund AI\data\sme_esg_applications_1000.csv"
# === Train the model once (optional) ===
def train_model(csv_path="data/sme_esg_applications_1000.csv"):
    df = pd.read_csv(csv_path)
    df["combined_text"] = (
        df["Answer_Text"].fillna("") + " " +
        df["File_Summary"].fillna("") + " " +
        df["Tags"].fillna("")
    )
    df["ESG_Label"] = df["ESG_Aligned"].map({"No": 0, "Partial": 1, "Yes": 2})
    X, y = df["combined_text"], df["ESG_Label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    
    pipeline = make_pipeline(
        TfidfVectorizer(max_features=500),
        XGBClassifier(use_label_encoder=False, eval_metric="mlogloss")
    )
    pipeline.fit(X_train, y_train)
    acc = accuracy_score(y_test, pipeline.predict(X_test))
    return pipeline, acc

# === Predict and return label ===
def predict_esg_label(pipeline, essay_text):
    label_map = {0: "No", 1: "Partial", 2: "Yes"}
    pred = pipeline.predict([essay_text])[0]
    return label_map[pred]

# === Return top SHAP keywords for context ===
def get_top_shap_keywords(pipeline, num_words=10):
    vectorizer = pipeline.named_steps["tfidfvectorizer"]
    model = pipeline.named_steps["xgbclassifier"]
    df = pd.read_csv("data/sme_esg_applications_1000.csv")
    df["combined_text"] = (
        df["Answer_Text"].fillna("") + " " +
        df["File_Summary"].fillna("") + " " +
        df["Tags"].fillna("")
    )
    X_vect = vectorizer.transform(df["combined_text"])
    X_sample = X_vect[:100].toarray()

    explainer = shap.Explainer(model)
    shap_values = explainer(X_sample)
    mean_shap = shap_values.values.mean(axis=0)
    top_indices = mean_shap.argsort()[-num_words:][::-1]
    return [vectorizer.get_feature_names_out()[i] for i in top_indices]