"""
ranking.py
----------

Provides routines to filter the top structures in a population based on energy, anomaly,
and diversity. Implements a Pareto-based selection function.
"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import zscore
from scipy.spatial.distance import mahalanobis
from sklearn.linear_model import Ridge

def filter_top_structures(structures, N, atom_labels=None, cluster_counts=None,
                          temperature=0.3, inflection_point_shift=2,
                          energy_weight=0.8, distance_weight=0.1):
    """
    Filters the top N structures based on a custom energy-based ranking and composition similarity penalty.

    Parameters
    ----------
    structures : list
        A list of structures, each with an energy attribute: structure.AtomPositionManager.E.
    N : int
        Number of top structures to select.
    atom_labels : list, optional
        List of atomic labels considered in the composition. Defaults to ['Fe', 'V', 'Ni', 'H', 'O', 'K'].
    cluster_counts : np.ndarray, optional
        Matrix of cluster counts per structure. Each row corresponds to a structure; each column is a cluster.
    temperature : float, optional
        Temperature-like parameter controlling the selection distribution, by default 0.3.
    inflection_point_shift : float, optional
        Shift in the inflection point of the selection function, by default 2.
    energy_weight : float, optional
        Relative weight given to low-energy preference (vs. anomaly), by default 0.8.
    distance_weight : float, optional
        Relative weight for diversity, by default 0.1.

    Returns
    -------
    list
        The top N structures, sorted by the custom multi-objective selection function.
    """
    if atom_labels is None:
        atom_labels = ['Fe', 'V', 'Ni', 'H', 'O', 'K']

    # Composition matrix X
    X = np.array([
        [
            np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
            for label in atom_labels
        ]
        for structure in structures
    ])

    # Extract energies
    y = np.array([structure.AtomPositionManager.E for structure in structures])

    # Fit a linear model for chemical potentials
    model = Ridge(alpha=1e-5, fit_intercept=False)
    model.fit(X, y)
    chemical_potentials = model.coef_
    formation_energies = y - X.dot(chemical_potentials)

    print('Chemical potentials:', ' '.join([f'{label}: {mu}' for label, mu in zip(atom_labels, chemical_potentials)]))

    # Select structures using a Pareto-based approach
    selected_indices, dominant_indices = select_pareto_anomalous_diverse_low_energy(
        data_matrix=cluster_counts,
        energy_vector=formation_energies,
        M=N,
        temperature=0.2,
        inflection_point_shift=0.5,
        energy_weight=energy_weight,
        distance_weight=distance_weight
    )

    return [structures[dominant_indices[i]] for i in selected_indices]


def select_pareto_anomalous_diverse_low_energy(data_matrix, energy_vector, M,
                                               temperature=5.0, inflection_point_shift=1.0,
                                               energy_weight=0.8, distance_weight=0.1):
    """
    Selects M structures from a dataset by optimizing for anomaly (Mahalanobis distance), diversity,
    and low energy with a probabilistic selection from a multi-dimensional Pareto front.

    Parameters
    ----------
    data_matrix : np.ndarray
        NxD matrix where each row is a structure's cluster-count vector or composition descriptor.
    energy_vector : np.ndarray
        1D array of length N, containing the energy of each structure.
    M : int
        Number of structures to select.
    temperature : float, optional
        Controls randomness in selection; lower values -> more deterministic, by default 5.0.
    inflection_point_shift : float, optional
        Shift applied to the inflection point in the sigmoid function, by default 1.0.
    energy_weight : float, optional
        Weighting factor between 0 and 1 for emphasizing energy vs. anomaly, by default 0.8.
    distance_weight : float, optional
        Weight factor for diversity-based penalty, by default 0.1.

    Returns
    -------
    list
        Indices of the M selected structures in data_matrix.
    list
        Indices of the non-dominated points from the original dataset (the "dominant" subset).
    """
    # Step 1: Compute Mahalanobis distance for anomaly detection
    normalized_data = zscore(data_matrix, axis=0)
    normalized_data = np.nan_to_num(normalized_data, nan=0.0)
    mean_vector = np.mean(normalized_data, axis=0)
    cov_matrix_inv = inv(np.cov(normalized_data, rowvar=False) + 1e-6 * np.eye(normalized_data.shape[1]))

    mahalanobis_distances = np.array([
        mahalanobis(row, mean_vector, cov_matrix_inv) for row in normalized_data
    ])

    # Step 2: Identify non-dominated (Pareto) points
    unique_compositions, inverse_indices = np.unique(data_matrix, axis=0, return_inverse=True)
    dominant_indices = []

    for unique_idx in range(len(unique_compositions)):
        matching_indices = np.where(inverse_indices == unique_idx)[0]

        group_dominant = []
        for i in matching_indices:
            dominated = False
            for j in matching_indices:
                if (energy_vector[j] <= energy_vector[i] and
                    mahalanobis_distances[j] >= mahalanobis_distances[i] and
                    (energy_vector[j] < energy_vector[i] or mahalanobis_distances[j] > mahalanobis_distances[i])):
                    dominated = True
                    break
            if not dominated:
                group_dominant.append(i)
        dominant_indices.extend(group_dominant)

    # Step 3: Probabilistic selection
    pareto_energy = energy_vector[dominant_indices]
    pareto_anomaly = mahalanobis_distances[dominant_indices]
    pareto_data = data_matrix[dominant_indices]

    inflection_point = np.min(pareto_energy) + inflection_point_shift

    # Weighted combination of energy and anomaly
    energy_term = 1 / (1 + np.exp((pareto_energy - inflection_point) / temperature))
    energy_term /= np.sum(energy_term)

    anomaly_term = pareto_anomaly / np.sum(pareto_anomaly)

    probabilities = energy_weight * energy_term + (1 - energy_weight) * anomaly_term
    probabilities /= np.sum(probabilities)

    # Step 4: Iterative selection with diversity
    selected_indices = []
    for _ in range(M):
        if selected_indices:
            selected_data = pareto_data[selected_indices]
            distances_to_selected = np.min(
                np.linalg.norm(pareto_data[:, np.newaxis] - selected_data, axis=2), axis=1
            )

            # Normalize
            prob_norm = probabilities / np.sum(probabilities)
            distances_term = distances_to_selected / np.sum(distances_to_selected)

            probabilities_corrected = ((1 - distance_weight) * prob_norm
                                       + distance_weight * distances_term)
            probabilities_corrected /= np.sum(probabilities_corrected)
        else:
            probabilities_corrected = probabilities

        # If all probabilities vanish, reset to uniform
        probabilities_corrected_nan = np.nan_to_num(probabilities_corrected, nan=0.0)
        if np.sum(probabilities_corrected_nan) == 0:
            probabilities_corrected_nan = np.ones(len(dominant_indices)) / len(dominant_indices)

        chosen_idx = np.random.choice(len(dominant_indices), p=probabilities_corrected_nan)
        selected_indices.append(chosen_idx)
        probabilities[chosen_idx] = 0  # "Remove" this index from future draws
        probabilities /= np.sum(probabilities)

    return np.array(selected_indices), dominant_indices
