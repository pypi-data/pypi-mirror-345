import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from xgboost import XGBClassifier

def calculate_sensitivity(scores, cutoff):
    if not scores:
        return 0.0
    return sum(score >= cutoff for score in scores) / len(scores)


def calculate_specificity(all_scores, sp_scores, cutoff):
    passed_all = [score for score in all_scores if score >= cutoff]
    passed_sp = [score for score in sp_scores if score >= cutoff]
    return len(passed_sp) / len(passed_all) if passed_all else 0.0


def find_cutoff(proteins_scores_df, sp_proteins, output_dir=None, plot_roc=None):
    scores = proteins_scores_df['Score'].tolist()
    sp_scores = proteins_scores_df[proteins_scores_df['Protein'].isin(sp_proteins)]['Score'].tolist()

    cutoffs = [x / 100 for x in range(100, -1, -1)]
    tpr = [calculate_sensitivity(sp_scores, c) for c in cutoffs]
    tnr = [calculate_specificity(scores, sp_scores, c) for c in cutoffs]
    fpr = [1 - x for x in tnr]

    for i in range(2, len(tpr)):
        slope = (tpr[i] - tpr[i-1]) / (fpr[i] - fpr[i-1]) if (fpr[i] - fpr[i-1]) != 0 else float('inf')
        if slope < 1:
            cutoff = max(cutoffs[i], 0.69)
            if plot_roc and output_dir:
                plot_roc(fpr, tpr, cutoff, fpr[i], tpr[i], output_dir)
            return cutoff

    return 1


def find_apply_score_filter(proteins_scores_df, sp_proteins, output_dir=None, plot_roc=None):
    cutoff = find_cutoff(proteins_scores_df, sp_proteins, output_dir, plot_roc)
    high_scoring = set(proteins_scores_df[proteins_scores_df['Score'] >= cutoff]['Protein'])
    low_supported = set(proteins_scores_df[(proteins_scores_df['Score'] < cutoff) & proteins_scores_df['Protein'].isin(sp_proteins)]['Protein'])
    return high_scoring | low_supported


def get_high_confident_proteins(df):
    high_confident = []
    for _, group in df.groupby("Protein"):
        for _, row in group.iterrows():
            if row["protein_specific_peptides"] >= 2:
                high_confident.append(row)
                break
            if row["gene_specific_peptides"] >= 2 and row["protein_specific_peptides"] >= 1:
                high_confident.append(row)
                break
            if row["protein_coverage"] >= 0.5 and row["protein_specific_peptides"] >= 1:
                high_confident.append(row)
                break
            if row["protein_coverage"] >= 0.7:
                high_confident.append(row)
                break
    return pd.DataFrame(high_confident)


def train_iterative_model(df, feature_cols, pos_thr=0.90, neg_thr=0.10, n_iter=5, shap_output_dir=None, plot_shap=None):
    df["label"] = np.nan

    pos_mask = (
        (df["protein_specific_peptides"] >= 2) |
        (df["protein_coverage"] >= 0.7) |
        ((df["protein_specific_peptides"] >= 1) & (df["protein_coverage"] >= 0.5))
    )
    neg_mask = (
        (df["mapped_peptides"] <= 1) &
        (df["psauron_score"] < 0.5) &
        (df["prediction_score"] < 0.5)
    )

    df.loc[pos_mask, "label"] = 1
    df.loc[neg_mask, "label"] = 0
    
    df_labeled = df.dropna(subset=["label"])
    X_labeled = df_labeled[feature_cols]
    y_labeled = df_labeled["label"]
    
    # Check if there are any negative labels
    if (y_labeled == 0).sum() == 0:
        raise ValueError(
            "No negative labels found in the labeled data.\n"
            "Either the number of proteins in the fasta file is very low,\n"
            "or all proteins are fully supported by peptides.\n"
            "Stopping the pipeline."
        )
    else:
        # Use StratifiedKFold to preserve class imbalance in each fold
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Initialize base model
        base_model = XGBClassifier(eval_metric='logloss', random_state=42)

        param_dist = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'scale_pos_weight': [1, 2, 5]
        }
        
        # Set up RandomizedSearchCV
        random_search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=param_dist,
            n_iter=20,  # Adjust this to explore more parameters if needed
            scoring='roc_auc',  # Use a scoring metric that handles imbalance well
            cv=skf,
            verbose=1,
            random_state=42,
            n_jobs=-1
        )

        # Fit RandomizedSearchCV on your labeled data
        random_search.fit(X_labeled, y_labeled)

        # Use the best estimator from the search
        model = random_search.best_estimator_

    if plot_shap and shap_output_dir:
        plot_shap(model, X_labeled, shap_output_dir)

    for _ in range(n_iter):
        df_unlabeled = df[df["label"].isna()]
        if df_unlabeled.empty:
            break

        X_unlabeled = df_unlabeled[feature_cols]
        prob_pred = model.predict_proba(X_unlabeled)[:, 1]

        new_pos = df_unlabeled.index[prob_pred >= pos_thr]
        new_neg = df_unlabeled.index[prob_pred <= neg_thr]

        df.loc[new_pos, "label"] = 1
        df.loc[new_neg, "label"] = 0

        df_labeled = df.dropna(subset=["label"])
        y_labeled = df_labeled["label"]
        X_labeled = df_labeled[feature_cols]

        if y_labeled.nunique() == 2:
            model = XGBClassifier(eval_metric='logloss', random_state=42)
            model.fit(X_labeled, y_labeled)

        if len(new_pos) == 0 and len(new_neg) == 0:
            break

    df["prob_pos"] = model.predict_proba(df[feature_cols])[:, 1]
    df["final_label"] = (df["prob_pos"] >= 0.5).astype(int)
    return df
