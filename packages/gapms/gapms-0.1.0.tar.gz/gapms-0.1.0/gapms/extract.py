from pathlib import Path
import pandas as pd
import numpy as np
from Bio import SeqIO

from .gtf_utils import gtf_to_df_with_genes
from .mapping_utils import mapping_file_to_df
from .peptide_utils import (
    get_gene_protein_specific_peps,
    check_peptide_loc,
    count_expected_peptides_with_missed_cleavages,
    calculate_protein_coverage
)
from .plotting import (
    plot_protein_coverage_hist,
    plot_prediction_scores,
    plot_psauron_scores,
    plot_protein_metrics
)

def extract_features(gtf_file, prediction_fasta, mapping_file, psauron_csv, output_dir): 
    gtf_df = gtf_to_df_with_genes(gtf_file)
    transcripts_df = gtf_df[gtf_df['Type'].isin(['transcript', 'mRNA'])][['Suppl', 'Score']].rename(columns={'Suppl': 'Protein'})
    transcripts_df['Prediction_score'] = pd.to_numeric(transcripts_df['Score'], errors='coerce').fillna(0)
    transcripts_df = transcripts_df[['Protein', 'Prediction_score']]

    gtf_df = gtf_df[gtf_df['Type'] == 'CDS']
    gtf_df = gtf_df[gtf_df['Source'].isin(['AUGUSTUS', 'Helixer'])]
    gtf_df['Isoforms'] = gtf_df.groupby('Gene')['Protein'].transform(lambda x: x.nunique())
    gtf_df['Score'] = pd.to_numeric(gtf_df['Score'], errors='coerce')
    gtf_df['Protein_Start'] = gtf_df.groupby('Protein')['Start'].transform('min')
    gtf_df['Protein_End'] = gtf_df.groupby('Protein')['End'].transform('max')
    gtf_df = gtf_df.merge(transcripts_df, on='Protein', how='left')

    df_CDSs = gtf_df.copy().sort_values(by=['Protein', 'Start']).drop_duplicates(subset=['Seqid', 'Start', 'End', 'Protein'])
    df_CDSs['cds_start'] = 0
    df_CDSs['cds_end'] = 0

    splice_sites_dict = {}
    cds_start_map = {}
    cds_end_map = {}

    for protein, sub_df in df_CDSs.groupby('Protein'):
        protein_cds_start = 0
        total_protein_len = round((sub_df['End'] - sub_df['Start']).sum() / 3)
        splice_sites_dict[protein] = len(sub_df) - 1

        for idx, row in sub_df.iterrows():
            cds_length = round((row['End'] - row['Start']) / 3)
            if row['Strand'] == '+':
                cds_start = protein_cds_start + 1
                cds_end = protein_cds_start + cds_length
                protein_cds_start = cds_end
            else:
                cds_end = total_protein_len
                cds_start = total_protein_len - cds_length + 1
                total_protein_len = cds_start - 1

            cds_start_map[idx] = cds_start
            cds_end_map[idx] = cds_end

    df_CDSs.loc[cds_start_map.keys(), 'cds_start'] = list(cds_start_map.values())
    df_CDSs.loc[cds_end_map.keys(), 'cds_end'] = list(cds_end_map.values())

    gtf_df = gtf_df.merge(df_CDSs[['Protein', 'Start', 'cds_start', 'cds_end']], on=['Protein', 'Start'], how='left')
    gtf_df['cds_start'] = gtf_df['cds_start'].astype('Int64')
    gtf_df['cds_end'] = gtf_df['cds_end'].astype('Int64')
    gtf_df['splice_sites'] = gtf_df['Protein'].map(splice_sites_dict)

    mapping_df = mapping_file_to_df(mapping_file)
    pep_df = get_gene_protein_specific_peps(gtf_df, mapping_df)
    seq_dict = {record.id: str(record.seq).replace('I', 'L').replace('*', '') for record in SeqIO.parse(prediction_fasta, "fasta")}
    pep_df['Prot_seq'] = pep_df['Protein'].map(seq_dict)
    pep_df.dropna(subset=['Prot_seq'], inplace=True)

    pep_df['pep_start'] = pep_df.apply(lambda row: row['Prot_seq'].find(row['Peptide']) + 1, axis=1)
    pep_df['pep_end'] = pep_df.apply(lambda row: row['pep_start'] + len(row['Peptide']) - 1, axis=1)
    pep_df['prot_len'] = pep_df['Prot_seq'].str.len()
    pep_df['expected_peptides'] = pep_df['Prot_seq'].apply(count_expected_peptides_with_missed_cleavages)
    pep_df.drop(columns='Prot_seq', inplace=True)

    coverage_series = pep_df.groupby("Protein").apply(calculate_protein_coverage)
    pep_df['protein_coverage'] = pep_df['Protein'].map(coverage_series)

    peptide_features_df = pd.merge(gtf_df, pep_df, on=['Protein', 'Gene'])
    peptide_features_df = peptide_features_df[[
        'Peptide', 'Protein', 'Gene', 'Isoforms', 'splice_sites', 'Protein_specific',
        'Gene_specific', 'cds_start', 'cds_end', 'pep_len',
        'pep_start', 'pep_end', 'Prediction_score', 'prot_len', 'protein_coverage'
    ]]

    cds_dict = peptide_features_df.groupby('Protein')[['cds_start', 'cds_end']].apply(lambda x: list(x.itertuples(index=False, name=None))).to_dict()
    peptide_features_df['Splice_peptide'] = peptide_features_df.apply(lambda row: check_peptide_loc(row, cds_dict), axis=1)

    peptide_features_df['Stop_peptide'] = np.where(peptide_features_df['pep_end'] == peptide_features_df['prot_len'], '+', '-')
    peptide_features_df['Start_peptide'] = np.where(peptide_features_df['pep_start'] == 1, '+', '-')

    proteins_scores_df = peptide_features_df.groupby("Protein").agg(
        protein_length=("prot_len", "mean"),
        protein_coverage=("protein_coverage", "mean"),
        protein_isoforms=("Isoforms", "mean"),
        splice_sites=("splice_sites", "mean"),
        prediction_score=("Prediction_score", "mean"),
        mapped_peptides=("Peptide", "count"),
        start_peptides=("Start_peptide", lambda x: (x == "+").sum()),
        stop_peptides=("Stop_peptide", lambda x: (x == "+").sum()),
        protein_specific_peptides=("Protein_specific", lambda x: (x == "+").sum()),
        gene_specific_peptides=("Gene_specific", lambda x: (x == "+").sum()),
        splice_peptides=("Splice_peptide", lambda x: (x == "+").sum()),
        internal_peptides=("Splice_peptide", lambda x: (x == "-").sum())
    ).reset_index()

    proteins_scores_df['splice_sites'] = proteins_scores_df['Protein'].map(splice_sites_dict).fillna(0).astype(int)
    # proteins_scores_df.to_csv(output_dir / 'protein_scores.tsv', sep='\t', index=False)

    new_proteins = gtf_df[~gtf_df['Protein'].isin(proteins_scores_df['Protein'])]
    new_entries = new_proteins[['Protein', 'Prediction_score']].drop_duplicates().copy()
    new_entries['prediction_score'] = pd.to_numeric(new_entries['Prediction_score'], errors='coerce')
    for col in proteins_scores_df.columns.difference(['Protein', 'prediction_score']):
        new_entries[col] = 0
    all_proteins_scores_df = pd.concat([proteins_scores_df, new_entries], ignore_index=True).drop(columns='Prediction_score')

    psauron_df = pd.read_csv(psauron_csv, sep=',', names=['Protein', 'psauron_is_protein', 'psauron_score']).drop(columns='psauron_is_protein')
    psauron_df['psauron_score'] = pd.to_numeric(psauron_df['psauron_score'], errors='coerce')
    all_proteins_scores_df = pd.merge(all_proteins_scores_df, psauron_df, on='Protein', how='left')
    all_proteins_scores_df['prediction_score'] = all_proteins_scores_df['prediction_score'].fillna(0)
    all_proteins_scores_df.to_csv(output_dir / 'all_proteins_scores.tsv', sep='\t', index=False)

    plot_protein_coverage_hist(all_proteins_scores_df, output_dir)
    plot_prediction_scores(all_proteins_scores_df, output_dir)
    plot_psauron_scores(all_proteins_scores_df, output_dir)
    plot_protein_metrics(all_proteins_scores_df, output_dir)
