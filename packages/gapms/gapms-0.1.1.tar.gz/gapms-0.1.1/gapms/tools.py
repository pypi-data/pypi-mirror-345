import subprocess
import os
from pathlib import Path

def run_proteomapper(protdb_path: str, peptides_path: str, output_dir):
    # Get the directory of this Python file (assuming Perl scripts are in the same dir)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to the local Perl scripts
    clips_path = os.path.join(base_dir, "clips.pl")
    promast_path = os.path.join(base_dir, "promast.pl")

    # Output file in the same directory as peptides
    output_file = output_dir / "proteomapper.tsv"
    # output_file = peptides_path.with_suffix(".proteomapper.tsv")

    # Run clips.pl
    clips_cmd = ["perl", clips_path, "-f", protdb_path]
    clips_result = subprocess.run(clips_cmd, capture_output=True, text=True)

    if clips_result.returncode != 0:
        raise RuntimeError(f"clips.pl failed:\n{clips_result.stderr}")

    # Run promast.pl
    promast_cmd = f"perl {promast_path} {protdb_path} {peptides_path} > {output_file}"
    promast_result = subprocess.run(promast_cmd, shell=True, capture_output=True, text=True)

    if promast_result.returncode != 0:
        raise RuntimeError(f"promast.pl failed:\n{promast_result.stderr}")
    
    pep_idx_file = str(protdb_path) +'.pep.idx'
    if os.path.exists(pep_idx_file):
        os.remove(pep_idx_file)
    return output_file

def run_psauron(protdb_path: Path, output_dir):
    # output_file = protdb_path.with_suffix(".psauron.csv")
    output_file = output_dir / "psauron.csv"

    command = [
        "psauron",
        "-i", str(protdb_path),
        "-o", str(output_file),
        "-p"
    ]

    psauron_result = subprocess.run(command, capture_output=True, text=True)

    if psauron_result.returncode != 0:
        raise RuntimeError(f"psauron failed:\n{psauron_result.stderr}")

    print("STDOUT:\n", psauron_result.stdout)
    print("STDERR:\n", psauron_result.stderr)

    return output_file

