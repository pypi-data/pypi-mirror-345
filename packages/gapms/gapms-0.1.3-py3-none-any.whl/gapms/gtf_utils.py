import re
import pandas as pd

def extract_id(suppl_value, pattern):
    if isinstance(suppl_value, str):
        match = re.search(pattern, suppl_value)
        if match:
            return match.group(1)
    return None

def gtf_to_df_with_genes(gtf_file):
    column_names = ['Seqid', 'Source', 'Type', 'Start', 'End', 'Score', 'Strand', 'Frame', 'Suppl']
    df = pd.read_csv(gtf_file, sep='\t', index_col=False, names=column_names)
    from .gtf_utils import extract_id
    df['Gene'] = df.apply(lambda row: extract_id(row['Suppl'], r'Parent=([^;]+)') if row['Source'] in ['Helixer'] else extract_id(row['Suppl'], r'gene_id "([^"]+)"') , axis=1)
    df['Protein'] = df.apply(lambda row: extract_id(row['Suppl'], r'Parent=([^;]+)') if row['Source'] in ['Helixer'] else extract_id(row['Suppl'], r'transcript_id "([^"]+)"'), axis=1)
    df["Score"] = df["Score"].replace(".", 0).fillna(0)
    return df
