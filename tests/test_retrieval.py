"""
Minimal retrieval check against the local ChromaDB index.

The test is skipped when the index does not exist (the index is built locally
from the PDFs and is not part of the repository). Run it from the repo root:

    pytest
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = Path(os.getenv("CHROMA_DIR", "data/chroma_db"))

pytestmark = pytest.mark.skipif(
    not (CHROMA_DIR / "chroma.sqlite3").exists(),
    reason=f"Local index not found at {CHROMA_DIR}; run scripts/indexar.py first.",
)

# Query about arterial hypertension in primary care. The guideline
# IMSS-076-08-ER ("Diagnostico y Tratamiento de la Hipertension Arterial en el
# Primer Nivel de Atencion") is expected to be the best match.
QUERY = "¿Cuál es el tratamiento de la hipertensión arterial en el primer nivel de atención?"
EXPECTED_TOP = "IMSS-076-08-ER"


@pytest.fixture(scope="module")
def backend():
    from backend import main
    if main.collection is None:
        pytest.skip("Collection 'guias_medicas' not found in the local index.")
    return main


def test_expected_guideline_is_first(backend):
    resultados = backend.buscar_chunks(QUERY)
    assert resultados, "buscar_chunks returned no results"
    assert resultados[0]["archivo"] == EXPECTED_TOP


def test_results_have_unique_chunks(backend):
    resultados = backend.buscar_chunks(QUERY)
    llaves = [(r["archivo"], r["pagina"], r["chunk"]) for r in resultados]
    assert len(llaves) == len(set(llaves))
    assert len(resultados) <= 8
