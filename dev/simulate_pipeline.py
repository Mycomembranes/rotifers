#!/usr/bin/env python3
"""Simulate a rotifer analysis pipeline.

Given a GenBank accession, this script walks through the main rotifer
modules used for a typical analysis: sequence retrieval, PSI-BLAST
searches, multiple sequence alignment, MMseqs clustering, and gene
neighborhood diagram generation. The implementation uses lightweight
placeholders so it can run without external binaries or network access
while still exercising the relevant modules.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from rotifer.db.ncbi import entrez
try:
    from rotifer.db import neighbors  # may fail due to legacy syntax
except Exception:  # pragma: no cover - best effort import
    neighbors = None
import importlib.util
from pathlib import Path
import pandas.compat
from io import StringIO as _StringIO

pandas.compat.StringIO = _StringIO

# Load alignment module directly to avoid heavy package imports
alignment_path = (
    Path(__file__).resolve().parent.parent / "lib" / "rotifer" / "seq" / "alignment.py"
)
spec = importlib.util.spec_from_file_location("rotifer.seq.alignment", alignment_path)
alignment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment)


def fetch_sequence(genbank_id: str):
    """Retrieve a sequence record for ``genbank_id``.

    If network access fails the function returns a synthetic
    :class:`Bio.SeqRecord.SeqRecord` instance so downstream steps can be
    exercised in a predictable fashion.
    """

    cursor = entrez.SequenceCursor(database="protein", progress=False)
    try:
        # Network access is skipped in this simulation; raise to use fallback
        raise RuntimeError("simulation")
    except Exception:
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        record = SeqRecord(Seq("MSEQUENCE"), id=genbank_id, description="synthetic")
    return record


def run_psiblast(record) -> List[Dict[str, Any]]:
    """Simulate a PSI-BLAST search for ``record``.

    Rotifer exposes wrappers for BLAST, but invoking them would require
    external binaries and large databases. Instead this function returns
    a short list of dummy hits that downstream steps can operate on.
    """

    print(f"Simulating PSI-BLAST for {record.id}", file=sys.stderr)
    return [
        {"hit_id": f"{record.id}_HIT1", "evalue": 1e-5},
        {"hit_id": f"{record.id}_HIT2", "evalue": 2e-5},
    ]


def run_alignment(record, hits):
    """Create a minimal multiple sequence alignment.

    The :mod:`rotifer.seq.alignment` module represents alignments as
    pandas ``DataFrame`` objects. Here we build an alignment composed of
    the query sequence and one synthetic hit sequence.
    """

    fasta_entries = [
        f">{record.id}\n{record.seq}",
        f">{hits[0]['hit_id']}\n{record.seq}",
    ]
    fasta = "\n".join(fasta_entries)
    msa = alignment.MSA.read(fasta, input_format="fasta")
    print("Simulated alignment contains", len(msa), "sequences", file=sys.stderr)
    return msa


def run_mmseqs(msa) -> Dict[str, List[str]]:
    """Cluster aligned sequences using a trivial strategy.

    MMseqs2 integration in rotifer relies on external executables. To
    keep this example self-contained we place all sequences into a
    single cluster and report it.
    """

    cluster = {"cluster_1": list(msa.index)}
    print("Simulating MMseqs clustering", cluster, file=sys.stderr)
    return cluster


def generate_gene_neighborhood(clusters) -> Dict[str, Any]:
    """Generate a placeholder gene neighborhood diagram.

    The :mod:`rotifer.db.neighbors` module usually connects to a SQL
    database to build diagrams. For the simulation we simply reshape the
    cluster information into a dictionary that mimics a drawing
    specification.
    """

    diagram = {"blocks": []}
    for cid, proteins in clusters.items():
        diagram["blocks"].append({"cluster": cid, "members": proteins})
    print(
        "Synthesized gene neighborhood diagram with",
        len(diagram["blocks"]),
        "blocks",
        file=sys.stderr,
    )
    return diagram


def simulate_pipeline(genbank_id: str) -> Dict[str, Any]:
    """Execute the simulated analysis pipeline."""

    record = fetch_sequence(genbank_id)
    hits = run_psiblast(record)
    msa = run_alignment(record, hits)
    clusters = run_mmseqs(msa)
    diagram = generate_gene_neighborhood(clusters)
    return {
        "genbank_id": genbank_id,
        "sequence_length": len(record.seq),
        "psi_blast_hits": hits,
        "clusters": clusters,
        "neighborhood_diagram": diagram,
    }


if __name__ == "__main__":
    accession = sys.argv[1] if len(sys.argv) > 1 else "TEST123"
    result = simulate_pipeline(accession)
    print(json.dumps(result, indent=2))

