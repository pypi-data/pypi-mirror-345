#!/usr/bin/env python3
import warnings
import time
warnings.filterwarnings("ignore")

import sys
import argparse
from pathlib import Path
from datetime import datetime

from gapms.filter import filter_predictions
from gapms.tools import run_proteomapper, run_psauron
from gapms.translate import get_proteins_from_cds_gtf


def main():
    start_time = time.time()

    parser = argparse.ArgumentParser(
        description="Filter GTF predictions using mass-spec data and mapping information."
    )
    parser.add_argument("-f", "--proteins", type=Path, help="Path to the protein FASTA file")
    parser.add_argument("-g", "--gtf", type=Path, help="Path to the prediction GTF file (required if -f is not used)")
    parser.add_argument("-a", "--assembly", type=Path, help="Path to the genome assembly file (required if -f is not used)")
    parser.add_argument("-p", "--peptides", type=Path, help="Path to the peptides TXT file")
    parser.add_argument("-m", "--mapping", type=Path, help="Optional precomputed peptide-to-protein mapping file")
    parser.add_argument("-o", "--output", type=Path, help="Optional output directory")

    args = parser.parse_args()

    try:
        if args.output:
            output_dir = args.output
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            if args.gtf:
                base_dir = args.gtf.parent.parent
                output_dir = base_dir / "GAPMS_Output"
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                parser.error("No GTF file was provided, you must specify --gtf.")

        # Prepare logging
        log_file_path = output_dir / "log.txt"
        log_file = open(log_file_path, "w")
        sys.stdout = log_file
        sys.stderr = log_file

        # Print to terminal
        print(f"Starting GAP-MS. Check the log file in {log_file_path}", file=sys.__stdout__)

        # Start the pipeline
        if args.proteins:
            protein_fasta = args.proteins
        else:
            if not (args.gtf and args.assembly):
                raise ValueError("If --proteins is not provided, both --gtf and --assembly must be specified.")
            print(f"{Path().cwd()} - Generating protein FASTA from GTF and genome assembly...")
            protein_fasta = get_proteins_from_cds_gtf(args.assembly, args.gtf)

        if args.mapping:
            mapping = args.mapping
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Using provided mapping file: {mapping}")
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Mapping peptides to proteins with Proteomapper....")
            mapping = run_proteomapper(protein_fasta, args.peptides, output_dir)

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Running Psauron....")
        psauron = run_psauron(protein_fasta, output_dir)

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Running gapms....")
        filter_predictions(args.gtf, protein_fasta, mapping, psauron, output_dir)

        # Final messages
        total_time = (time.time() - start_time) / 60
        print("\n✅ Pipeline completed", file=sys.__stdout__)
        print(f"\nTotal time run: {total_time:.2f} minutes", file=sys.__stdout__)

    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}", file=sys.__stdout__)
        print(f"Please check the log file for more details: {log_file_path}", file=sys.__stdout__)
        raise

    finally:
        try:
            log_file.close()
        except:
            pass

if __name__ == "__main__":
    main()
