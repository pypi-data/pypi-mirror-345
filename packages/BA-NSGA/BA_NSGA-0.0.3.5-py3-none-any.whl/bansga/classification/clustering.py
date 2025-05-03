"""
soap_cluster_analyzer_refactored.py
==================================
A pythonic rewrite of the original *SOAPClusterAnalyzer* utility that

* Computes Smooth Overlap of Atomic Positions (SOAP) descriptors for a list
  of **ase**-compatible containers.
* Performs dimensionality reduction (PCA) followed by K‑means clustering
  (with a simple *elbow* placeholder for *k* optimisation).
* Consolidates per‑structure cluster populations into a matrix and evaluates
  Mahalanobis distances as an anomaly score.

The public interface stays **backwards‑compatible** with the original script:

>>> analyzer = SOAPClusterAnalyzer()
>>> scores   = analyzer.compute(structures)
>>> counts   = analyzer.get_cluster_counts(structures)

A convenience *extract_cluster_counts* function is provided for quick access
from procedural code.

Unit tests are included at the bottom of the file – they can be executed
with

    python soap_cluster_analyzer_refactored.py

or via *pytest* / *unittest discover*.
"""

from __future__ import annotations

###############################################################################
# Standard‑library imports
###############################################################################
import logging
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

###############################################################################
# Third‑party imports – grouped by provider
###############################################################################
import numpy as np
from numpy.linalg import LinAlgError, inv
from scipy.spatial.distance import mahalanobis
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning

# *sage_lib* is an external dependency shipped with SAGE‑Lab.
from sage_lib.partition.Partition import Partition  # type: ignore

###############################################################################
# Library‑wide configuration
###############################################################################
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence scikit‑learn convergence spam in unit tests.
import warnings

warnings.filterwarnings("ignore", category=ConvergenceWarning)

__all__ = [
    "SOAPClusterAnalyzer",
    "extract_cluster_counts",
]

###############################################################################
# Helper utilities
###############################################################################

def find_optimal_kmeans_k(data: np.ndarray, max_k: int=15) -> int:
    """
    Finds an optimal number of clusters (between 2..max_k) using silhouette score.
    If data has fewer samples than 2, returns 1 cluster by default.
    """
    if data.shape[0] < 2:
        return 1

    best_k = 2
    best_silhouette = -1

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(data)
            # If fewer than 2 distinct clusters are found, skip this iteration.
            if len(set(labels)) < 2:
                continue

            try:
                score = silhouette_score(data, labels)
                if score > best_silhouette:
                    best_silhouette = score
                    best_k = k
            except Exception:
                # If silhouette_score fails, skip to the next value of k.
                pass

    return best_k


def _safe_inverse(cov: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Return *cov*⁻¹, falling back to *Tikhonov* regularisation when singular."""

    try:
        return inv(cov)
    except LinAlgError:
        return inv(cov + np.eye(cov.shape[0]) * eps)


###############################################################################
# Main public API
###############################################################################


@dataclass
class SOAPClusterAnalyzer:
    """Analyse structural anomalies in a *SOAP* feature space.

    Parameters
    ----------
    n_components
        Number of principal components (PCA) to keep per species.
    r_cut, n_max, l_max, sigma
        Hyper‑parameters forwarded to :py:meth:`Partition.get_SOAP`.
    max_clusters
        Upper bound on *k* for the *k*‑means stage.
    """

    n_components: int = 5
    r_cut: float = 5.0
    n_max: int = 3
    l_max: int = 3
    sigma: float = 0.5
    max_clusters: int = 10

    # ---------------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------------

    def compute(self, structures: Sequence) -> np.ndarray:
        """Return one Mahalanobis anomaly score per structure."""

        n_structures = self._validate_input(structures)
        if n_structures == 0:
            return np.empty(0)
        if n_structures < self.n_components:
            # Not enough data for a stable covariance estimate – return zeros.
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 1. Compute species‑resolved SOAP descriptors.
        # ------------------------------------------------------------------
        partition = Partition()
        partition.containers = list(structures)  # *Partition* expects a list.
        desc_by_species, idx_by_species = partition.get_SOAP(
            r_cut=self.r_cut,
            n_max=self.n_max,
            l_max=self.l_max,
            sigma=self.sigma,
            save=False,
            cache=False,
        )
        if not desc_by_species:
            # No atoms – return zeros.
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 2. Reduce dimensionality + cluster per species.
        # ------------------------------------------------------------------
        cluster_matrices: List[np.ndarray] = []

        for specie, descriptors in desc_by_species.items():
            if descriptors.size == 0:
                continue  # No atoms of this species.

            atom_indices = idx_by_species[specie]
            feature_dim = descriptors.shape[1]

            if feature_dim < self.n_components:
                # Degenerate case – one column fit.
                cluster_matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            # *PCA* can throw if rank < n_components; catch and skip gracefully.
            try:
                compressed = PCA(n_components=self.n_components).fit_transform(
                    descriptors
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("PCA failed for %s: %s", specie, exc)
                cluster_matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            k_max = min(compressed.shape[0], self.max_clusters)
            k_opt = find_optimal_kmeans_k(compressed, k_max)

            cluster_counts = np.zeros((n_structures, max(k_opt, 1)), dtype=int)

            if k_opt <= 1:
                # All atoms belong to a single cluster – just count per structure.
                for atom_idx in range(compressed.shape[0]):
                    struct_idx = atom_indices[atom_idx][0]
                    cluster_counts[struct_idx, 0] += 1
            else:
                labels = KMeans(n_clusters=k_opt, random_state=42).fit_predict(
                    compressed
                )
                for atom_idx, lbl in enumerate(labels):
                    struct_idx = atom_indices[atom_idx][0]
                    cluster_counts[struct_idx, lbl] += 1

            cluster_matrices.append(cluster_counts)

        if not cluster_matrices:
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 3. Stack species matrices → shape = (n_structures, total_clusters).
        # ------------------------------------------------------------------
        combined = np.hstack(cluster_matrices)
        if combined.shape[1] == 0:
            return np.zeros(n_structures)

        # ------------------------------------------------------------------
        # 4. Mahalanobis anomaly score per row.
        # ------------------------------------------------------------------
        mean_vec = combined.mean(axis=0)
        cov = np.cov(combined, rowvar=False)
        inv_cov = _safe_inverse(cov)

        return np.array(
            [mahalanobis(row, mean_vec, inv_cov) for row in combined]
        )

    # ------------------------------------------------------------------

    def get_cluster_counts(self, structures: Sequence) -> np.ndarray:
        """Return the concatenated cluster count matrix."""

        n_structures = self._validate_input(structures)
        if n_structures == 0:
            return np.empty((0, 0), dtype=int)

        partition = Partition()
        partition.containers = list(structures)
        desc_by_species, idx_by_species = partition.get_SOAP(
            r_cut=self.r_cut,
            n_max=self.n_max,
            l_max=self.l_max,
            sigma=self.sigma,
            save=False,
            cache=False,
        )

        matrices: List[np.ndarray] = []
        for specie, descriptors in desc_by_species.items():
            if descriptors.size == 0:
                continue
            atom_indices = idx_by_species[specie]
            feature_dim = descriptors.shape[1]

            if feature_dim < self.n_components:
                matrices.append(np.zeros((n_structures, 1), dtype=int))
                continue

            compressed = PCA(n_components=self.n_components).fit_transform(
                descriptors
            )
            k_max = min(compressed.shape[0], self.max_clusters)
            k_opt = find_optimal_kmeans_k(compressed, k_max)

            counts = np.zeros((n_structures, max(k_opt, 1)), dtype=int)
            if k_opt <= 1:
                for atom_idx in range(compressed.shape[0]):
                    struct_idx = atom_indices[atom_idx][0]
                    counts[struct_idx, 0] += 1
            else:
                labels = KMeans(n_clusters=k_opt, random_state=42).fit_predict(
                    compressed
                )
                for atom_idx, lbl in enumerate(labels):
                    struct_idx = atom_indices[atom_idx][0]
                    counts[struct_idx, lbl] += 1
            matrices.append(counts)

        return np.hstack(matrices) if matrices else np.zeros((n_structures, 0))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_input(structures: Sequence) -> int:
        """Validate *structures* and return *len(structures)*."""

        if not isinstance(structures, (list, tuple)):
            raise TypeError("'structures' must be a list or tuple of containers.")
        return len(structures)


###############################################################################
# Procedural helper – kept for backward compatibility
###############################################################################

def extract_cluster_counts(containers: Sequence, **kwargs) -> np.ndarray:
    """Return the cluster‑count matrix for *containers* using keyword overrides."""

    return SOAPClusterAnalyzer(**kwargs).get_cluster_counts(containers)


###############################################################################
# Unit‑tests (can be run with `python soap_cluster_analyzer_refactored.py`)
###############################################################################

if __name__ == "__main__":
    # Register under canonical name so *unittest.mock.patch* works in scripts.
    sys.modules["soap_cluster_analyzer"] = sys.modules[__name__]

    import unittest
    from unittest.mock import patch

    import matplotlib.pyplot as plt

    # ------------------------------------------------------------------
    # Test‑helpers
    # ------------------------------------------------------------------

    def _synthetic_containers(n: int) -> List[str]:
        """Return dummy identifiers – SOAP will be patched in tests."""

        return [f"structure_{i}" for i in range(n)]

    # ------------------------------------------------------------------
    # Test‑suite
    # ------------------------------------------------------------------

    class TestSOAPClusterAnalyzer(unittest.TestCase):
        """Minimal non‑exhaustive smoke tests – extend as required."""

        def setUp(self) -> None:  # noqa: D401 – short description style.
            self.n_structures = 5
            self.structures = _synthetic_containers(self.n_structures)

        # -------------------------- compute() ---------------------------
        @patch("soap_cluster_analyzer.Partition")
        def test_empty_input(self, mock_partition):  # noqa: ANN001
            analyzer = SOAPClusterAnalyzer()
            result = analyzer.compute([])
            self.assertEqual(result.size, 0)
            mock_partition.assert_not_called()

        @patch("soap_cluster_analyzer.Partition")
        def test_synthetic_scores(self, mock_partition):  # noqa: ANN001
            n_atoms, n_features = 50, 10
            descriptors = np.random.rand(n_atoms, n_features)
            atom_info = [(i % self.n_structures, i) for i in range(n_atoms)]

            mock_inst = mock_partition.return_value
            mock_inst.get_SOAP.return_value = ({"A": descriptors}, {"A": atom_info})

            analyzer = SOAPClusterAnalyzer(n_components=3, max_clusters=4)
            scores = analyzer.compute(self.structures)
            self.assertEqual(scores.shape, (self.n_structures,))

        # ----------------- plotting & cluster matrix -------------------
        @patch("soap_cluster_analyzer.Partition")
        def test_plot_and_matrix(self, mock_partition):  # noqa: ANN001
            n_atoms, n_features = 30, 8
            descriptors = np.random.rand(n_atoms, n_features)
            atom_info = [(i % self.n_structures, i) for i in range(n_atoms)]

            mock_inst = mock_partition.return_value
            mock_inst.get_SOAP.return_value = ({"B": descriptors}, {"B": atom_info})

            analyzer = SOAPClusterAnalyzer(n_components=2, max_clusters=3)
            scores = analyzer.compute(self.structures)

            # Quick plot – verifies nothing crashes during I/O.
            plt.figure()
            plt.plot(range(len(scores)), scores)
            plt.xlabel("Structure Index")
            plt.ylabel("Anomaly Score")
            plt.title("Synthetic Anomaly Scores")
            plt.close()

            counts = extract_cluster_counts(
                self.structures, n_components=2, max_clusters=3
            )
            self.assertEqual(counts.shape[0], self.n_structures)

    # ------------------------------------------------------------------
    # Execute tests when the module is run directly.
    # ------------------------------------------------------------------
    unittest.main()
