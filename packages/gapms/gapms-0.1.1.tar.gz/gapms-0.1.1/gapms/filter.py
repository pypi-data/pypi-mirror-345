from pathlib import Path
import pandas as pd
import numpy as np

from .extract import extract_features
from .gtf_utils import gtf_to_df_with_genes
from .model_utils import (
    get_high_confident_proteins,
    find_apply_score_filter,
    train_iterative_model
)
from .plotting import (
    plot_roc_curve,
    plot_shap_summary,
    plot_stacked_percentage_bar
)


def filter_predictions(gtf_file, protein_fasta, mapping_file, psauron_csv, output_dir):
    gtf_file = Path(gtf_file)
    protein_fasta = Path(protein_fasta)
    mapping_file = Path(mapping_file)
    psauron_csv = Path(psauron_csv)

    # Step 1: Extract features
    extract_features(gtf_file, protein_fasta, mapping_file, psauron_csv, output_dir)

    # Step 2: Load feature outputs
    all_scores_path = output_dir / "all_proteins_scores.tsv"
    all_proteins_df = pd.read_csv(all_scores_path, sep='\t')

    # Step 3: Get GTF with Protein/Gene annotations
    gtf_df = gtf_to_df_with_genes(gtf_file)

    # Step 4: Find highly supported proteins
    high_confident_df = get_high_confident_proteins(all_proteins_df)
    high_confident_proteins = set(high_confident_df['Protein'].unique())

    high_confident_proteins_gtf = gtf_df[gtf_df['Protein'].isin(high_confident_proteins)]
    high_confident_proteins_gtf.drop(['Protein', 'Gene'], axis=1).to_csv(output_dir / "high_confident_proteins.gtf", sep="\t", index=False, header=False)

    # Step 5: Apply ROC-based score filtering
    all_proteins_df["Score"] = np.where(
        all_proteins_df["psauron_score"] <= 0.1,
        all_proteins_df["psauron_score"],
        all_proteins_df["prediction_score"]
    )

    if gtf_df['Source'].iloc[0] == 'Helixer':
        all_proteins_df["Score"] = all_proteins_df["psauron_score"]
        prediction_supported = high_confident_proteins
    else:
        prediction_supported = find_apply_score_filter(
            all_proteins_df, high_confident_proteins,
            output_dir=output_dir,
            plot_roc=plot_roc_curve
        )

    # Save prediction-supported GTF
    prediction_supported_gtf = gtf_df[gtf_df['Protein'].isin(prediction_supported)]
    # prediction_supported_gtf.drop(['Protein', 'Gene'], axis=1).to_csv(output_dir / "prediction_supported_proteins.gtf", sep="\t", index=False, header=False)

    
    FEATURE_COLUMNS = [
    "protein_coverage",
    "protein_specific_peptides",
    "gene_specific_peptides",
    "splice_peptides",
    "internal_peptides",
    "start_peptides",
    "stop_peptides",
    "splice_sites",
    "protein_isoforms"
    ]
    # Step 6: Train iterative self-labeling model
    labeled_df = train_iterative_model(
        all_proteins_df,
        feature_cols=FEATURE_COLUMNS,
        pos_thr=0.90,
        neg_thr=0.10,
        n_iter=5,
        shap_output_dir=output_dir,
        plot_shap=plot_shap_summary
    )

    # Save iterative results
    iterative_proteins = set(labeled_df[labeled_df["final_label"] == 1]["Protein"])
    
    
    all_proteins = set(all_proteins_df["Protein"])
    supported_proteins = prediction_supported | iterative_proteins
    unsupported_proteins = all_proteins - supported_proteins
    supported_proteins_gtf = gtf_df[gtf_df['Protein'].isin(supported_proteins)]
    supported_proteins_gtf.drop(['Protein', 'Gene'], axis=1).to_csv(output_dir / "supported_proteins.gtf", sep="\t", index=False, header=False)

    # Step 7: Save protein sets
    def save_protein_list(protein_set, filename):
        with open(output_dir / filename, "w") as f:
            for p in sorted(protein_set):
                f.write(f"{p}\n")

    save_protein_list(all_proteins, "all_proteins.txt")
    save_protein_list(high_confident_proteins, "high_confident_proteins.txt")
    # save_protein_list(prediction_supported - high_confident_proteins, "prediction_only_proteins.txt")
    # save_protein_list(iterative_proteins - prediction_supported, "iterative_only_proteins.txt")
    save_protein_list(supported_proteins, "supported_proteins.txt")
    save_protein_list(unsupported_proteins, "unsupported_proteins.txt")

    # Step 8: Filter FASTA
    output_fasta = output_dir / "supported_proteins.faa"
    with open(protein_fasta) as fasta, open(output_fasta, "w") as out:
        header, seq = "", ""
        for line in fasta:
            if line.startswith(">"):
                if header and header[1:] in supported_proteins:
                    out.write(header + "\n" + seq + "\n")
                header, seq = line.strip(), ""
            else:
                seq += line.strip()
        if header and header[1:] in supported_proteins:
            out.write(header + "\n" + seq + "\n")

    plot_stacked_percentage_bar(len(supported_proteins), len(unsupported_proteins), output_dir)
    print(f"\nPipeline completed\nOutputs written to: {output_dir}")
    print(f"\nNumber of all proteins = {len(set(all_proteins_df['Protein']))}")
    print(f"Number of high confident proteins = {len(high_confident_proteins)}")
    # print(f"\n Number of low confident proteins = {len(low_confident_proteins)}")
    print(f"Number of supported proteins = {len(supported_proteins)}")
    print(f"Number of un-supported proteins = {len(unsupported_proteins)}")
