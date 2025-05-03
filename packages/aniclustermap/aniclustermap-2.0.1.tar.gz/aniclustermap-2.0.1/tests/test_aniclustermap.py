import shlex
import subprocess as sp
from pathlib import Path


def test_aniclustermap_cli_fastani_mode(genome_fasta_dir: Path, tmp_path: Path):
    """Test ANIclustermap CLI (mode=fastani)"""
    aniclustermap_cli(genome_fasta_dir, tmp_path, "fastani")


def test_aniclustermap_cli_skani_mode(genome_fasta_dir: Path, tmp_path: Path):
    """Test ANIclustermap CLI (mode=skani)"""
    aniclustermap_cli(genome_fasta_dir, tmp_path, "skani")


def aniclustermap_cli(genome_fasta_dir: Path, tmp_path: Path, mode: str):
    """Run ANIclustermap CLI"""
    cmd = f"ANIclustermap -i {genome_fasta_dir} -o {tmp_path} --mode {mode}"
    cmd_args = shlex.split(cmd)
    result = sp.run(cmd_args)
    assert result.returncode == 0
    outfile_names = [
        "ANIclustermap.png",
        "ANIclustermap.svg",
        "ANIclustermap_dendrogram.nwk",
        "ANIclustermap_matrix.tsv",
        "aniclustermap.log",
    ]
    for outfile_name in outfile_names:
        assert (tmp_path / outfile_name).exists()
