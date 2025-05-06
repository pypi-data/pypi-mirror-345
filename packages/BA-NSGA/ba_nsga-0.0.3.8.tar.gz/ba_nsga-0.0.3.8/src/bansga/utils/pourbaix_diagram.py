import numpy as np
from numpy.linalg import lstsq

import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.linear_model import Ridge
from scipy.optimize import minimize
from scipy.optimize import lsq_linear

import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection

from joblib import Parallel, delayed
import csv
import re, copy
from collections import defaultdict
from scipy.ndimage import measurements
import matplotlib.colors as mcolors

from sage_lib.partition.Partition import Partition
from sage_lib.miscellaneous.data_mining import *

import pandas as pda
import time
import holoviews as hv
from holoviews.operation.datashader import datashade, dynspread




import re
from collections import defaultdict
from typing import Dict, Tuple

debug = True
#https://cran.r-project.org/web/packages/CHNOSZ/vignettes/equilibrium.html
#https://cran.r-project.org/web/packages/CHNOSZ/vignettes/multi-metal.html
def parse_species(species: str) -> Tuple[int, Dict[str, int]]:
    """Parse a chemical species string and return its charge and composition.

    The parser interprets a subset of the Hill‑style chemical grammar with a
    trailing charge annotation.

    Parameters
    ----------
    species : str
        A chemical species given as an ASCII string, e.g. ``"K+"``, ``"Fe2+"``,
        ``"Fe(OH)3"``. The final token must encode the charge using ``+`` or
        ``-`` symbols optionally preceded by an integer magnitude (``"+"``,
        ``"-"``, ``"2+"``, ``"3-"``). Everything before the charge token is
        considered the molecular formula. Element symbols start with a capital
        letter followed optionally by a lowercase letter; stoichiometric
        subscripts are expressed as decimal integers; groups may be enclosed in
        round brackets and multiplied by an integer sub‑script.

    Returns
    -------
    Tuple[int, Dict[str, int]]
        * **charge** – Algebraic charge of the species (e.g. ``+1``, ``-2``).
        * **composition** – Mapping from element symbols to their integer
          multiplicities.

    Examples
    --------
    >>> parse_species("K+")
    (1, {'K': 1})
    >>> parse_species("Fe2+")
    (2, {'Fe': 1})
    >>> parse_species("Fe(OH)3")
    (0, {'Fe': 1, 'O': 3, 'H': 3})
    >>> parse_species("H2O")
    (0, {'H': 2, 'O': 1})
    >>> parse_species("VO2+")
    (1, {'V': 1, 'O': 2})
    """

    # ---------------------------------------------------------------------
    # 1. Separate the formula from the trailing charge annotation.
    # ---------------------------------------------------------------------
    s = species.strip()
    charge_match = re.search(r"([0-9]*[+-])$", s)  # '', '2+', '+', '3‑', etc.
    if charge_match:
        charge_str = charge_match.group(1)
        formula_part = s[: charge_match.start()]
    else:
        charge_str = "0"  # implicit neutral species
        formula_part = s

    # ---------------------------------------------------------------------
    # 2. Convert the textual charge fragment to an integer.
    # ---------------------------------------------------------------------
    def _charge_to_int(token: str) -> int:
        """Return the signed integer encoded by *token* ("+", "2-", "0", …)."""
        if token == "0":
            return 0
        sign = 1 if "+" in token else -1
        magnitude = token.rstrip("+-") or "1"  # '+' → '1'
        return sign * int(magnitude)

    charge = _charge_to_int(charge_str)

    # ---------------------------------------------------------------------
    # 3. Recursively expand the formula into element counts.
    # ---------------------------------------------------------------------
    element_re = re.compile(r"([A-Z][a-z]?)(\d*)")  # e.g. 'Fe2' → ('Fe', '2')

    def _merge(dst: Dict[str, int], src: Dict[str, int]) -> None:
        """In‑place addition of two element‑count dictionaries."""
        for k, v in src.items():
            dst[k] += v

    def _scale(counts: Dict[str, int], factor: int) -> Dict[str, int]:
        """Return *counts* multiplied by *factor* (pure function)."""
        return {k: v * factor for k, v in counts.items()}

    def _parse_block(block: str) -> Dict[str, int]:
        """Parse a formula *block* without parentheses."""
        counts: Dict[str, int] = defaultdict(int)
        for elem, digits in element_re.findall(block):
            counts[elem] += int(digits) if digits else 1
        return counts

    def _expand(formula: str) -> Dict[str, int]:
        """Recursively expand nested parenthetical groups in *formula*."""
        if "(" not in formula:
            return _parse_block(formula)

        total: Dict[str, int] = defaultdict(int)
        paren_re = re.compile(r"\(([^)]*)\)(\d*)")
        pos = 0
        while True:
            match = paren_re.search(formula, pos)
            if not match:
                break

            # Anything preceding the current '(' belongs to *before*.
            before = formula[pos : match.start()]
            _merge(total, _parse_block(before))

            inner_formula, multiplier_txt = match.groups()
            multiplier = int(multiplier_txt) if multiplier_txt else 1
            inner_counts = _expand(inner_formula)
            _merge(total, _scale(inner_counts, multiplier))

            pos = match.end()

        # Remainder after the last ')' (or the entire string if no parentheses).
        tail = formula[pos:]
        _merge(total, _parse_block(tail))
        return total

    composition = dict(sorted(_expand(formula_part).items()))
    return charge, composition

def generate_allowed_transitions(
    N,
    allow_cyclic=False,
    allow_diagonal=False,
    allow_backward=False,
    allow_wraparound=False
):
    """
    Generates a dictionary of possible transitions for each state (i, j), 
    depending on the specified options.
    
    :param N: The size of the grid (N x N).
    :param allow_cyclic: If True, allows the addition of cyclic (catalytic or other) transitions.
    :param allow_diagonal: If True, enables diagonal movements.
    :param allow_backward: If True, allows backward (up and left) movements.
    :param allow_wraparound: If True, applies toroidal wrapping at the grid boundaries.
    
    :return: A dictionary whose keys are (i, j) tuples representing states, 
             and whose values are lists of reachable next states (as tuples).
    """

    transitions = {}

    for i in range(N):
        for j in range(N):
            next_states = []

            # ====================================================
            # Default forward movements
            # ====================================================
            # 1. Down
            if allow_wraparound:
                # Wrap around the grid boundaries
                next_i = (i + 1) % N
                next_states.append((next_i, j))
            else:
                # Only if within bounds
                if i + 1 < N:
                    next_states.append((i + 1, j))

            # 2. Right
            if allow_wraparound:
                next_j = (j + 1) % N
                next_states.append((i, next_j))
            else:
                if j + 1 < N:
                    next_states.append((i, j + 1))

            # ====================================================
            # Backward movements (optional)
            # ====================================================
            if allow_backward:
                # 3. Up
                if allow_wraparound:
                    prev_i = (i - 1) % N
                    next_states.append((prev_i, j))
                else:
                    if i - 1 >= 0:
                        next_states.append((i - 1, j))

                # 4. Left
                if allow_wraparound:
                    prev_j = (j - 1) % N
                    next_states.append((i, prev_j))
                else:
                    if j - 1 >= 0:
                        next_states.append((i, j - 1))

            # ====================================================
            # Diagonal movements (optional)
            # ====================================================
            if allow_diagonal:
                # Down-right
                if allow_wraparound:
                    d_i = (i + 1) % N
                    d_j = (j + 1) % N
                    next_states.append((d_i, d_j))
                else:
                    if (i + 1 < N) and (j + 1 < N):
                        next_states.append((i + 1, j + 1))

                # Down-left
                if allow_wraparound:
                    d_i = (i + 1) % N
                    d_j = (j - 1) % N
                    next_states.append((d_i, d_j))
                else:
                    if (i + 1 < N) and (j - 1 >= 0):
                        next_states.append((i + 1, j - 1))

                # Up-right
                if allow_wraparound:
                    d_i = (i - 1) % N
                    d_j = (j + 1) % N
                    next_states.append((d_i, d_j))
                else:
                    if (i - 1 >= 0) and (j + 1 < N):
                        next_states.append((i - 1, j + 1))

                # Up-left
                if allow_wraparound:
                    d_i = (i - 1) % N
                    d_j = (j - 1) % N
                    next_states.append((d_i, d_j))
                else:
                    if (i - 1 >= 0) and (j - 1 >= 0):
                        next_states.append((i - 1, j - 1))

            # ====================================================
            # Cyclic transitions (catalytic or other)
            # ====================================================
            if allow_cyclic:
                # Examples (uncomment or modify as needed):
                # 1. Transition back to the same state
                # next_states.append((i, j))

                # 2. Transition back to the origin
                # next_states.append((0, 0))
                pass

            # Assign the list of next states to the transitions dictionary
            transitions[(i, j)] = next_states

    return transitions

def evaluate_path(path, E):
    """
    Instead of calculating a global (final - initial) energy difference,
    compute the difference step by step and take the *maximum* of those
    stepwise differences. This represents the highest 'barrier' along
    the path.

    Returns that maximum difference.
    """
    if len(path) < 2:
        return 0.0  # if there's only one state, no actual steps

    max_diff = 0.0
    # Iterate over consecutive transitions
    for i in range(len(path) - 1):
        current_energy = E[path[i][0]][path[i][1]]
        next_energy = E[path[i+1][0]][path[i+1][1]]
        
        # Energy difference for this step
        diff = next_energy - current_energy
        #if path[i] == (2,0) and path[i+1] == (3,4):
        #    diff = .005
        #if path[i] == (0,2) and path[i+1] == (4,3):
        #    diff = .005

        # Check if this is the largest difference so far
        if diff > max_diff:
            max_diff = diff

    return max_diff


def dfs_search_paths(current, destination, transitions, E,
                     visited=None, current_path=None, all_paths=None
):
    """
    Depth-First Search to enumerate all possible paths from 'current' to 'destination'.
    
    - current: (i, j) tuple for the current state
    - destination: (i, j) tuple for the target state
    - transitions: dict specifying which states can be reached from each state
    - E: matrix of energies (included for consistency, but unused by DFS itself)
    - visited: set of visited states (to avoid cycles)
    - current_path: path taken so far
    - all_paths: list to store all completed paths
    """
    if visited is None:
        visited = set()
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    visited.add(current)
    current_path.append(current)

    if current == destination:
        # Reached the final state, record the path
        all_paths.append(current_path.copy())
    else:
        # Explore neighbors
        for nxt in transitions[current]:
            if nxt not in visited:
                dfs_search_paths(nxt, destination, transitions, E,
                                 visited, current_path, all_paths)

    # Backtrack
    current_path.pop()
    visited.remove(current)

    return all_paths

class PhaseDiagram():
    """
    Class for modeling and plotting a phase diagram of chemical reactions involving electrochemical states. 
    The diagram considers pH and potential (U) variations to determine the state of different species in equilibrium. 
    """
    def __init__(self, Kb:float=8.617333262e-5, T:float=298, regularization_strength:float=0.000000):
        """
        Initializes the phase diagram with specified parameters, temperature, and regularization strength.

        Parameters:
        - Kb: Boltzmann constant in eV/K (default: 8.617333262e-5 eV/K).
        - T: Temperature in Kelvin (default: 298 K).
        - regularization_strength: Regularization strength for Ridge regression (default: 1e-6).
        """
        self.Kb = Kb
        self.T = T        
        self.KbT = self.Kb * self.T  # Calculate the thermal energy (kBT).

        # pH range for the phase diagram
        self.pH_min, self.pH_max, self.pH_points = 13, 14, 1
        self.pH_values = np.linspace(self.pH_min, self.pH_max, self.pH_points)

        # Potential (U) range for the phase diagram
        self.U_min, self.U_max, self.U_points = -0, 2. , 100
        self.U_values = np.linspace(self.U_min, self.U_max, self.U_points)

        # Create meshgrid for plotting the pH and U plane
        self.PH_grid, self.U_grid = np.meshgrid(self.pH_values, self.U_values)

        # Regularization strength for Ridge Regression
        self.regularization_strength = regularization_strength

        # Dictionary for storing states and their properties
        self.states = {}
        self.N_states = 0

        self.species = []

        # Number and list of reaction vectors
        self.R_num = 0
        self._R = []
        self._reaction_list = []

        # Number and list of relevant reaction vectors
        self.RR_num = 0
        self._RR = []
        self._relevant_reaction_list = []

        # Free energy change and dependency on pH/U for reactions
        self.dG = []
        self.CC = {}

        # Number and list of relevant reaction vectors
        self.NR_states = {}
        self.NR_states_N = 0
        self.NR_species = []
        self.NR_num = 0
        self._NR = []
        self._nonrelevant_reaction_list = []
        self.NR_dG = []
        self.NR_CC = {}
        self._NR_G = {}

        self.color = [
            '#DC143C', '#ADFF2F', '#40E0D0', '#FF8C00', '#BA55D3', '#1E90FF',
            '#FF1493', '#8B4513', '#FFD700', '#808000', '#808080', '#FF00FF',
            '#00FFFF', '#000000']

    @property
    def R(self) -> np.ndarray:
        """
        Devuelve un array (2D) donde cada fila corresponde a un vector de reacción.
        Si no hay reacciones, retorna un array vacío con la forma (0, N_states).
        """
        if self._reaction_list:
            return np.vstack(self._reaction_list)
        else:
            return np.empty((0, self.N_states))

    @property
    def RR(self) -> np.ndarray:
        """
        Devuelve un array (2D) donde cada fila corresponde a un vector de reacción.
        Si no hay reacciones, retorna un array vacío con la forma (0, N_states).
        """
        if self._relevant_reaction_list:
            return np.vstack(self._relevant_reaction_list)
        else:
            return np.empty((0, self.N_states))

    @property
    def NR(self) -> np.ndarray:
        """
        Devuelve un array (2D) donde cada fila corresponde a un vector de reacción.
        Si no hay reacciones, retorna un array vacío con la forma (0, N_states).
        """
        if self._nonrelevant_reaction_list:
            return np.vstack(self._nonrelevant_reaction_list)
        else:
            return np.empty((0, self.NR_states))

    @property
    def NR_G(self) -> np.ndarray:
        """
        """
        return self._NR_G

    def non_relevant_specie_by_idx(self, idx):
        idx = int(idx)

        species_list = ['' for n in range(self.NR_states_N)]
        for i, (key, value) in enumerate(self.NR_states.items()):
            species_list[value[0]] = key
        return species_list[idx]
    
    def specie_by_idx(self, idx):
        idx = int(idx)

        species_list = ['' for n in range(self.N_states)]
        for i, (key, value) in enumerate(self.states.items()):
            species_list[value[0]] = key
        return species_list[idx]

    def print(self):
        """
        Prints the state index, name, and charge of each state in the 'states' dictionary.

        Each state consists of a key-value pair, where:
        - The key represents the name of the state.
        - The value is a tuple, where the first element is a descriptive label, and the second is the charge value.
        """
        # Header for the output
        print(self.PH_grid[0,0], self.U_grid[0,0])
        print(f'{"State index".ljust(12)} : {"Name".ljust(10)} : {"Charge"} : ')
        
        # Iterates through the dictionary of states, printing index, name, and charge for each state
        for i, (key, value) in enumerate(self.states.items()):
            # 'value[0]' is the name, 'key' is the state identifier, and 'value[1]' is the charge
            print(f'{str(i).ljust(12)} : {str(key).ljust(10)} : {str(value[1])} :  {self.mu_pH_U[0, 0, i]:.2f}')

        """
        Prints all equilibria reactions stored in the given matrix.
        Each row represents an equilibrium reaction with coefficients for reactants and products.
        
        Parameters:
        - matrix: A NumPy array where each row represents an equilibrium reaction vector.
        """
        matrix = self.R
        for idx, row in enumerate(matrix):
            reactants = []
            products = []
            
            # Iterate through the row to determine reactants and products
            for state_name, (state_index, _) in self.states.items():
                coefficient = row[state_index]
                # Round coefficient if it's close to an integer
                coefficient = round(coefficient) if abs(coefficient - round(coefficient)) < 1e-6 else coefficient
                if coefficient > 0:
                    reactants.append(f"{coefficient} {state_name}")
                elif coefficient < 0:
                    products.append(f"{-coefficient} {state_name}")
            
            # Convert lists to strings
            reactants_str = " + ".join(reactants)
            products_str = " + ".join(products)
            
            # Print the reaction
            print(f"Reaction {idx + 1} ( dG={self.dG[idx]:.2f}eV - {self.K[0,0,idx]:.2f}eV = {self.dG[idx]-self.K[0,0,idx]:.2}) : {reactants_str} <=> {products_str}")

    @staticmethod
    def set_pH(self, pH_min, pH_max, pH_points):
        """
        Set the pH range for the phase diagram.

        Parameters:
        - pH_min: Minimum pH value.
        - pH_max: Maximum pH value.
        - pH_points: Number of pH points for generating the grid.
        """
        self.pH_min, self.pH_max, self.pH_points = pH_min, pH_max, pH_points
        self.pH_values = np.linspace(self.pH_min, self.pH_max, self.pH_points)

        return True

    @staticmethod
    def set_U(self, U_min, U_max, U_points):
        """
        Set the potential (U) range for the phase diagram.

        Parameters:
        - U_min: Minimum potential value.
        - U_max: Maximum potential value.
        - U_points: Number of U points for generating the grid.
        """
        self.U_min, self.U_max, self.U_points = U_min, U_max, U_points
        self.U_values = np.linspace(self.U_min, self.U_max, self.U_points)

        return True

    def add_state(self, name:str, charge:int=0, CC:float=1.0):
        """
        Add a new chemical state to the phase diagram.

        Parameters:
        - name: The name of the chemical state.
        - charge: The electric charge of the state (default: 0).
        """
        if name not in self.states:
            self.states[name] = [self.N_states, charge]
            self.N_states += 1
            self.CC[name] = CC

            for key in parse_species(name)[1].keys():
                if not key in self.species:
                    self.species.append(key)

        else:
            print(f'{name} is already a state')

    def add_non_relevant_state(self, name:str, charge:int=0, CC:float=1.0):
        """
        Add a new chemical state to the phase diagram.

        Parameters:
        - name: The name of the chemical state.
        - charge: The electric charge of the state (default: 0).
        """
        if name not in self.NR_states:
            self.NR_states[name] = [self.NR_states_N, charge]
            self.NR_states_N += 1
            self.NR_CC[name] = CC

            for key in parse_species(name)[1].keys():
                if not key in self.NR_species:
                    self.NR_species.append(key)

        else:
            print(f'{name} is already a state')

    def add_reaction(self, reactants:dict, products:dict, free_energy_change:float):
        """
        Add a new reaction to the list of reactions.

        Parameters:
        - reactants: Dictionary of reactants and their coefficients.
        - products: Dictionary of products and their coefficients.
        - free_energy_change: Free energy change for the reaction.
        - dG_U_change: Index for identifying if reaction free energy is dependent on potential (default: False).
        - dG_pH_change: Index for identifying if reaction free energy is dependent on pH (default: False).
        """
        reaction_vector = np.zeros(self.N_states)

        # Add reactants with positive coefficients
        for r_name, r_coeffs in reactants.items():
            idx = self.states[r_name][0]
            reaction_vector[idx] += r_coeffs

        #reactant_indices = [self.states[specie][0] for specie in reactants]
        #reactant_coeffs = np.array(list(reactants.values()))
        #np.add.at(reaction_vector, reactant_indices, reactant_coeffs)

        # Add products with negative coefficients
        for r_name, r_coeffs in products.items():
            idx = self.states[r_name][0]
            reaction_vector[idx] -= r_coeffs
        
        self._reaction_list.append(reaction_vector)
        self.dG.append(free_energy_change)
        self.R_num += 1
        
        return True 

    def add_relevant_reaction(self, reactants:dict, products:dict, ):
        """
        Add a new relevant reaction to the list of relevant reactions.
        These reactions are used for further computations in the phase diagram.

        Parameters:
        - reactants: Dictionary of reactants and their coefficients.
        - products: Dictionary of products and their coefficients.
        """
        reaction_vector = np.zeros(self.N_states)

        # Add reactants with positive coefficients
        for r_name, r_coeffs in reactants.items():
            idx = self.states[r_name][0]
            reaction_vector[idx] = r_coeffs

        # Add products with negative coefficients
        for r_name, r_coeffs in products.items():
            idx = self.states[r_name][0]
            reaction_vector[idx] = -r_coeffs

        self._relevant_reaction_list.append(reaction_vector)
        self.RR_num += 1

        return True 

    def add_non_relevant_reaction(self, reactants:dict, products:dict, free_energy_change:float):
        """
        Add a new reaction to the list of reactions.

        Parameters:
        - reactants: Dictionary of reactants and their coefficients.
        - products: Dictionary of products and their coefficients.
        - free_energy_change: Free energy change for the reaction.
        - dG_U_change: Index for identifying if reaction free energy is dependent on potential (default: False).
        - dG_pH_change: Index for identifying if reaction free energy is dependent on pH (default: False).
        """
        reaction_vector = np.zeros(self.NR_states_N)

        # Add reactants with positive coefficients
        for r_name, r_coeffs in reactants.items():
            idx = self.NR_states[r_name][0]
            reaction_vector[idx] += r_coeffs

        #reactant_indices = [self.NR_states[specie][0] for specie in reactants]
        #reactant_coeffs = np.array(list(reactants.values()))
        #np.add.at(reaction_vector, reactant_indices, reactant_coeffs)

        # Add products with negative coefficients
        for r_name, r_coeffs in products.items():
            idx = self.NR_states[r_name][0]
            reaction_vector[idx] -= r_coeffs
        
        self._nonrelevant_reaction_list.append(reaction_vector)
        self.NR_dG.append(free_energy_change)
        self.NR_num += 1

        if len(reactants) + len(products) == 1:
            if len(reactants) == 1:
                self._NR_G[next(iter(reactants))] = free_energy_change
            else:
                self._NR_G[next(iter(products))] = -free_energy_change

        return True 

    def generate_R(self, C=None, parallel:bool=True) -> np.array:
        """
        Generate the phase diagram by calculating the chemical potential (mu) for each state.
        Uses Ridge regression to predict the equilibrium states over a 2D grid of pH and U values.

        Returns:
        - A NumPy array representing the chemical potentials of each state over the pH-U grid.
        """
        # Initialize C if not provided
        if C is None:
            C = np.ones(self.N_states)

        # Update C with custom values from CC dictionary
        for C_name, C_CC in self.CC.items():
            C[self.states[C_name][0]] = C_CC

        # Precompute CH+ and COH- values for all grid points to avoid repeated calculations
        CHp_values = 10 ** -self.PH_grid.ravel()  # Flatten grid for easier indexing
        COHm_values = 10 ** (14 - self.PH_grid.ravel())

        # Initialize arrays for storing results
        mu_pH_U = np.zeros((self.pH_points, self.U_points, self.N_states))
        K = np.zeros((self.pH_points, self.U_points, self.R.shape[0]))

        # Ridge model initialization
        model = Ridge(alpha=self.regularization_strength, fit_intercept=False)


        # Function to process each grid point
        def process_grid_point(index):
            dG_local = np.array(self.dG)  # Local copy to avoid modifying the original
            i, j = divmod(index, self.pH_points)

            # Retrieve precomputed H+ and OH- values
            CHp = CHp_values[index]
            U = self.U_grid[i, j]

            # Calculate chemical concentrations
            CC_local = np.array(C)
            CC_local[self.states['e-'][0]] = 1
            CC_local[self.states['H+'][0]] = CHp

            # Apply concentration corrections
            correction = self.KbT * np.log(CC_local)
            dG_local += np.einsum('ij,j->i', self.R, correction)

            # Apply potential correction
            potential_correction = np.zeros(self.N_states)
            potential_correction[self.states['e-'][0]] = -U
            dG_local += np.einsum('ij,j->i', self.R, potential_correction)

            # Fit Ridge regression model
            model.fit(self.R, dG_local)

            # Store results
            return model.coef_, np.dot(self.R, model.coef_)

        if parallel:
            # Parallel processing of grid points
            def process_grid_chunk(start_index, end_index):
                results = []
                for index in range(start_index, end_index):
                    results.append(process_grid_point(index))
                return results

            n_jobs = -1
            total_points = self.pH_points * self.U_points
            chunk_size = 100  # Adjust based on profiling
            chunks = [(i, min(i + chunk_size, total_points)) for i in range(0, total_points, chunk_size)]

            results_chunks = Parallel(n_jobs=n_jobs)(
                delayed(process_grid_chunk)(start, end) for start, end in chunks
            )
            # Flatten the list of results
            results = [res for chunk in results_chunks for res in chunk]

        else:
            results = []
            for index in range(self.pH_points * self.U_points):
                results.append(process_grid_point(index))

        # Store the results in mu_pH_U and K arrays
        for index, (coef, k) in enumerate(results):
            i, j = divmod(index, self.U_points)
            mu_pH_U[i, j, :] = coef
            K[i, j, :] = k

        # Assign results to class attributes
        self.mu_pH_U = mu_pH_U
        self.K = K

        return mu_pH_U

    def Mosaic_Stacking(self, relevant_species=None, parallel=True, reference=None, reference_idx=None) -> np.array:

        def compare_loop(rs_i, id_i, id_j):
            rs = relevant_species[rs_i]

            for i, (state_name, state_data) in enumerate(self.states.items()):
                if rs in parse_species(state_name)[1]  and state_name != min_name[rs_i]:
                    charge, composition = parse_species(state_name)
                    if composition.get(rs, 0) > 0:
                        # compare specie rs
                        R = np.zeros( self.mu_pH_U.shape[2] )
                        R[state_data[0]] = 1
                        ratio = float(composition.get(rs, 0)) / float(min_composition[rs_i].get(rs, 0))
                        R[min_ID[rs_i]] += - ratio

                        # evaluate diferences 
                        delta_dict = {
                            s:float(composition.get(s, 0)) - float(min_composition[rs_i].get(s, 0))*ratio
                            for s in self.species
                        }

                        dC = charge - min_charge[rs_i]*ratio

                        # ==== Oxigen O ==== #
                        if 'O' in self.species:
                            try:
                                R[self.states['H2O'][0]] += -float(delta_dict.get('O',0))/2 * 2
                                R[self.states['e-'][0]] += float(delta_dict.get('O',0))/2 * 4
                                R[self.states['H+'][0]] += float(delta_dict.get('O',0))/2 * 4
                            except: print('Can not equilibrate O')

                        # ==== Hidrogen H ==== #
                        if 'H' in self.species:
                            try:
                                R[self.states['e-'][0]] += -float(delta_dict.get('H',0))/2 * 2
                                R[self.states['H+'][0]] += -float(delta_dict.get('H',0))/2 * 2
                            except: print('Can not equilibrate H')

                        # ==== Potasium K ==== #
                        if 'K' in self.species:
                            try:
                                R[self.states['e-'][0]] += -float(delta_dict.get('K',0)) 
                                R[self.states['K+'][0]] += -float(delta_dict.get('K',0)) 
                            except: print('Can not equilibrate K')
                        
                        # ==== Iron Fe ==== #
                        if 'Fe' in self.species:
                            try:
                                R[self.states['FeOOH'][0]] += -float(delta_dict.get('Fe',0))/2 * 2
                                R[self.states['H2O'][0]] += float(delta_dict.get('Fe',0))/2 * 2 * 2
                                R[self.states['e-'][0]] += -float(delta_dict.get('Fe',0))/2 * 2 * 3
                                R[self.states['H+'][0]] += -float(delta_dict.get('Fe',0))/2 * 2 * 3
     
                            except: print('Can not equilibrate Fe')

                        # ==== Vanadium V ==== #
                        if 'V' in self.species:
                            try:
                                R[self.states['HV2O5 -'][0]] += -float(delta_dict.get('V',0))/2 
                                R[self.states['H2O'][0]] += float(delta_dict.get('V',0))/2*5
                                R[self.states['H+'][0]] += -float(delta_dict.get('V',0))/2*9
                                R[self.states['e-'][0]] += -float(delta_dict.get('V',0))/2*8

                            except: print('Can not equilibrate V')

                        # ==== Niquel Ni ==== #
                        if 'Ni' in self.species:
                            try: 
                                R[self.states['NiO2'][0]] += -float(delta_dict.get('Ni',0))/2 * 2
                                R[self.states['H2O'][0]] += float(delta_dict.get('Ni',0))/2 * 4
                                R[self.states['e-'][0]] += -float(delta_dict.get('Ni',0))/2*8
                                R[self.states['H+'][0]] += -float(delta_dict.get('Ni',0))/2*8

                            except: print('Can not equilibrate Ni')

                        # ==== Charge ==== #
                        try:
                            R[self.states['e-'][0]] += float(dC)
                        except: pass

                        dG = np.dot(R, self.mu_pH_U[id_i, id_j, :] )

                        if (dG <= 0 and composition.get('K', 0) == 0) or min_composition[rs_i].get('K', 0) > 0:
                            min_charge[rs_i], min_composition[rs_i] = charge, composition

                            min_ID[rs_i] = state_data[0]
                            min_name[rs_i] = state_name

            stable_index_array[id_i, id_j, rs_i] = min_ID[rs_i]

            return (rs_i, id_i, id_j, min_ID[rs_i])

        def compare_loop_dinamic_reference(rs_i, id_i, id_j):
            rs = relevant_species[rs_i]

            for i, (state_name, state_data) in enumerate(self.states.items()):
                if rs in parse_species(state_name)[1]  and state_name != min_name[rs_i]:
                    charge, composition = parse_species(state_name)
                    if composition.get(rs, 0) > 0:
                        # compare specie rs
                        R = np.zeros( self.mu_pH_U.shape[2] )
                        R[state_data[0]] = 1
                        ratio = float(composition.get(rs, 0)) / float(min_composition[rs_i].get(rs, 0))
                        R[min_ID[rs_i]] += - ratio

                        # evaluate diferences 
                        delta_dict = {
                            s:float(composition.get(s, 0)) - float(min_composition[rs_i].get(s, 0))*ratio
                            for s in self.species
                        }

                        dC = charge - min_charge[rs_i]*ratio

                        stable_species = { specie:self.specie_by_idx( reference[id_i, id_j, reference_idx[specie]] ) for specie in ['Ni', 'Fe', 'V'] }

                        # ==== Oxigen O ==== #
                        if 'O' in self.species:
                            try:
                                R[self.states['H2O'][0]] += -float(delta_dict.get('O',0))/2 * 2
                                R[self.states['e-'][0]] += float(delta_dict.get('O',0))/2 * 4
                                R[self.states['H+'][0]] += float(delta_dict.get('O',0))/2 * 4
                            except: print('Can not equilibrate O')

                        # ==== Hidrogen H ==== #
                        if 'H' in self.species:
                            try:
                                R[self.states['e-'][0]] += -float(delta_dict.get('H',0))/2 * 2
                                R[self.states['H+'][0]] += -float(delta_dict.get('H',0))/2 * 2
                            except: print('Can not equilibrate H')

                        # ==== Potasium K ==== #
                        if 'K' in self.species:
                            try:
                                R[self.states['e-'][0]] += -float(delta_dict.get('K',0)) 
                                R[self.states['K+'][0]] += -float(delta_dict.get('K',0)) 
                            except: print('Can not equilibrate K')
                        
                        # ==== Iron Fe ==== #
                        if 'Fe' in self.species:
                            #try:
                                charge_stable_Fe, composition_stable_Fe = parse_species( stable_species['Fe'] )
                                Fe_ratio = float(delta_dict.get('Fe',0))/float(composition_stable_Fe.get('Fe', 0))
                                
                                R[self.states[stable_species['Fe']][0]] += -Fe_ratio
                                R[self.states['H2O'][0]] += Fe_ratio * float(composition_stable_Fe.get('O', 0)) 
                                R[self.states['H+'][0]] += -Fe_ratio * ( 2*float(composition_stable_Fe.get('O', 0)) - composition_stable_Fe.get('H', 0))
                                R[self.states['e-'][0]] += -Fe_ratio * ( 2*float(composition_stable_Fe.get('O', 0)) - composition_stable_Fe.get('H', 0) + charge_stable_Fe)
                            
                            #except: print('Can not equilibrate Fe')

                        # ==== Vanadium V ==== #
                        if 'V' in self.species:
                            try:
                                charge_stable_V, composition_stable_V = parse_species( stable_species['V'] )
                                V_ratio = float(delta_dict.get('V',0))/float(composition_stable_V.get('V', 0))
                                R[self.states[stable_species['V']][0]] += -V_ratio
                                R[self.states['H2O'][0]] += V_ratio * float(composition_stable_V.get('O', 0)) 
                                R[self.states['H+'][0]] += -V_ratio * ( 2*float(composition_stable_V.get('O', 0)) - composition_stable_V.get('H', 0))
                                R[self.states['e-'][0]] += -V_ratio * ( 2*float(composition_stable_V.get('O', 0)) - composition_stable_V.get('H', 0) + charge_stable_V)
                            
                            except: print('Can not equilibrate V')

                        # ==== Niquel Ni ==== #
                        if 'Ni' in self.species:
                            try: 
                                charge_stable_Ni, composition_stable_Ni = parse_species( stable_species['Ni'] )
                                Ni_ratio = float(delta_dict.get('Ni',0))/float(composition_stable_Ni.get('Ni', 0))
                                R[self.states[stable_species['Ni']][0]] += -Ni_ratio
                                R[self.states['H2O'][0]] += Ni_ratio * float(composition_stable_Ni.get('O', 0)) 
                                R[self.states['H+'][0]] += -Ni_ratio * ( 2*float(composition_stable_Ni.get('O', 0)) - composition_stable_Ni.get('H', 0))
                                R[self.states['e-'][0]] += -Ni_ratio * ( 2*float(composition_stable_Ni.get('O', 0)) - composition_stable_Ni.get('H', 0) + charge_stable_Ni)
                            
                            except: print('Can not equilibrate Ni')

                        # ==== Charge ==== #
                        try:
                            R[self.states['e-'][0]] += float(dC)
                        except: pass

                        dG = np.dot(R, self.mu_pH_U[id_i, id_j, :] )

                        if dG <= 0 and composition.get('K', 0) > 0 or min_composition[rs_i].get('K', 0) == 0:
                            #if dG <= 0:
                            min_charge[rs_i], min_composition[rs_i] = charge, composition

                            min_ID[rs_i] = state_data[0]
                            min_name[rs_i] = state_name

            stable_index_array[id_i, id_j, rs_i] = min_ID[rs_i]

            return (rs_i, id_i, id_j, min_ID[rs_i])

        relevant_species_N = len(relevant_species)

        # initialization
        min_charge, min_composition, min_ID, min_name = [],[],[],[]
        for rs in relevant_species:
            for i, (state_name, state_data) in enumerate(self.states.items()):
                ps = parse_species(state_name)

                if rs in parse_species(state_name)[1]:
                    min_charge.append( ps[0] )
                    min_composition.append( ps[1] )
                    min_ID.append( state_data[0] )
                    min_name.append( state_name )
                    break

        stable_index_array = np.zeros( (self.mu_pH_U.shape[0], self.mu_pH_U.shape[1], relevant_species_N) )
        stable_index_idx = {n:i for i, n in enumerate(relevant_species) }

        print(f' >> List of Considered Species : {self.species}' )

        if parallel:
            inicio = time.time()
            relevant_species_list = range( len(relevant_species) )
            mu_pH_U_list_i = range( self.mu_pH_U.shape[0] )
            mu_pH_U_list_j = range( self.mu_pH_U.shape[1] )
            compare_jobs = [(rs_i, id_i, id_j) for rs_i in relevant_species_list for id_i in mu_pH_U_list_i for id_j in mu_pH_U_list_j]

            function = compare_loop if reference is None else compare_loop_dinamic_reference
            
            results = np.array(Parallel(n_jobs=-1)(delayed(function)(i, j, k) for i, j, k in compare_jobs))

            rs_i_array, id_i_array, id_j_array, min_ID_array = zip(*results)
            
            rs_i_array = np.array(rs_i_array, dtype=np.int32)
            id_i_array = np.array(id_i_array, dtype=np.int32)
            id_j_array = np.array(id_j_array, dtype=np.int32)
            min_ID_array = np.array(min_ID_array, dtype=stable_index_array.dtype)
            
            stable_index_array[id_i_array, id_j_array, rs_i_array] = min_ID_array
            print(f"Execution time: {time.time()-inicio:.4f} s")

        else:
            inicio = time.time()
            for rs_i, rs in enumerate(relevant_species): 
                for id_i in range(self.mu_pH_U.shape[0]):
                    for id_j in range(self.mu_pH_U.shape[1]):
                        stable_index_array[id_i, id_j, rs_i] = compare_loop(rs_i, id_i, id_j)[3] if reference is None else compare_loop_dinamic_reference(rs_i, id_i, id_j)[3]

            print(f"Execution time: {time.time()-inicio:.4f} s")

        return stable_index_array, stable_index_idx

    def plot_phase_diagrams(self, ans, name):
        """
        Plots the 2D array 'ans' using the 'Blues' colormap.
        Labels each species once at the centroid of its occurrences.
        Configures the axes to represent pH and Potential (U) ranges.

        Parameters
        ----------
        ans : np.ndarray
            2D array of species indices with shape (U_points, pH_points).
        """
        # ----- Step 1: Map unique values to consecutive integers -----
        # Use np.unique to obtain unique values and their inverse indices
        unique_values, inverse_indices = np.unique(ans, return_inverse=True)
        num_species = len(unique_values)
        
        # Reshape the inverse indices to get the array with consecutive numbers
        consecutive_array = inverse_indices.reshape(ans.shape)
        
        # ----- Step 2: Create a discrete color map -----
        cmap = plt.get_cmap('Blues', num_species)
        
        # ----- Step 3: Create the figure and axes -----
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # ----- Step 4: Display the matrix with imshow using the color map -----
        extent = [self.pH_min, self.pH_max, self.U_min, self.U_max]  # [xmin, xmax, ymin, ymax]
        im = ax.imshow(consecutive_array, cmap=cmap, origin='lower', extent=extent, aspect='auto')
        
        # ----- Step 5: Add a colorbar -----
        # The colorbar ticks correspond to the mapped indices
        cbar = fig.colorbar(im, ax=ax, ticks=np.arange(num_species), fraction=0.046, pad=0.04)
        cbar.set_label('Species', fontsize=12)
        
        # Assign original labels to the colorbar ticks
        labels = [self.specie_by_idx(sp) for sp in unique_values]
        cbar.set_ticklabels(labels)
        
        # ----- Step 6: Configure axis ticks based on pH and U ranges -----
        num_ticks = 10
        ax.set_xticks(np.linspace(self.pH_min, self.pH_max, num_ticks))
        ax.set_yticks(np.linspace(self.U_min, self.U_max, num_ticks))
        
        # ----- Step 7: Add grid lines for better readability -----
        ax.grid(which='both', color='white', linestyle='-', linewidth=0.5, alpha=0.7)
        
        # ----- Step 8: Calculate and add labels for each species at their centroid -----
        for mapped_idx, sp_idx in enumerate(unique_values):
            # Find the coordinates where the original species appears
            coords = np.argwhere(ans == sp_idx)
            if coords.size == 0:
                continue  # Skip if there are no occurrences
            
            # Calculate the mean of the coordinates to find the centroid
            row_mean = np.mean(coords[:, 0])
            col_mean = np.mean(coords[:, 1])
            
            # Convert matrix indices to actual pH and U values
            pH_center = self.pH_min + (col_mean / (self.pH_points - 1)) * (self.pH_max - self.pH_min)
            U_center = self.U_min + (row_mean / (self.U_points - 1)) * (self.U_max - self.U_min)
            
            # Get the species name
            species_name = self.specie_by_idx(int(sp_idx))
            
            # Add the text label at the centroid with a semi-transparent background for readability
            ax.text(
                pH_center,
                U_center,
                species_name,
                ha='center',
                va='center',
                fontsize=10,
                color='black',
                weight='bold',
                bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1)
            )
        
        # ----- Step 9: Set labels and title -----
        ax.set_xlabel('pH', fontsize=12)
        ax.set_ylabel('Potential (U)', fontsize=12)
        ax.set_title('Phase Diagram of Chemical Species', fontsize=14)
        
        # ----- Step 10: Adjust layout to accommodate the colorbar and labels -----
        plt.tight_layout()
        plt.savefig(f'phase_diagram_{name}.png', dpi=300)

        # ----- Step 11: Display the plot -----
        plt.show()

    def oxigen_reaccion(self, C=None, verbose=False) -> np.array:
        """
        Generate the phase diagram by calculating the chemical potential (mu) for each state.
        Uses Ridge regression to predict the equilibrium states over a 2D grid of pH and U values.

        Parameters:
        - C (array-like, optional): Initial concentrations. If None, defaults to ones.
        - verbose (bool, optional): If True, prints detailed execution information.

        Returns:
        - A tuple containing:
            - model.coef_: Coefficients from the Ridge regression model.
            - np.dot(self.R, model.coef_): The chemical potentials calculated.
        """
        # Initialize C if not provided
        if C is None:
            C = np.ones(self.N_states)
            if verbose:
                print("Initialized concentration C to ones.")

        # Update C with custom values from CC dictionary
        if hasattr(self, 'CC') and self.CC:
            for C_name, C_CC in self.CC.items():
                index = self.states[C_name][0]
                C[index] = C_CC

        else:
            if verbose:
                print("No custom concentration values provided in CC dictionary.")

        # Initialize arrays for storing results
        mu_pH_U = np.zeros((self.pH_points, self.U_points, self.N_states))
        K = np.zeros((self.pH_points, self.U_points, self.R.shape[0]))
        if verbose:
            print("Initialized mu_pH_U and K arrays.")

        # Ridge model initialization
        model = Ridge(alpha=self.regularization_strength, fit_intercept=False)
        if verbose:
            print(f"Initialized Ridge regression model with alpha={self.regularization_strength}.")

        def mu_U_calc(U):
            if verbose:
                print(f"Calculating chemical potentials for U = {U} V.")
            
            dG_local = np.array(self.dG)  # Local copy to avoid modifying the original

            # Calculate chemical concentrations
            CC_local = np.array(C)
            CC_local[self.states['e-'][0]] = 1

            if verbose:
                print("Calculated local chemical concentrations (CC_local).")

            # Apply concentration corrections
            try:
                correction = self.KbT * np.log(CC_local)
                dG_local += np.einsum('ij,j->i', self.R, correction)
                if verbose:
                    print("Applied concentration corrections to dG_local.")
            except Exception as e:
                print(f"Error applying concentration corrections: {e}")
                raise

            # Apply potential correction
            potential_correction = np.zeros(self.N_states)
            potential_correction[self.states['e-'][0]] = U
            dG_local += np.einsum('ij,j->i', self.R, potential_correction)
            
            if verbose:
                print("Applied potential corrections to dG_local.")

            # Fit Ridge regression model
            model.fit(self.R, dG_local)
            if verbose:
                print("Fitted Ridge regression model.")

            return model.coef_

        # Calculate mu_U for specific U values
        try:
            self.mu_U = np.array([mu_U_calc(U=0), mu_U_calc(U=-0.40)])
            if verbose:
                print("Calculated mu_U for U=0 V and U=-0.40 V.")
        except Exception as e:
            print(f"Error during mu_U calculation: {e}")
            raise

        # Final output
        coef = model.coef_
        chemical_potentials = np.dot(self.R, coef)
        if verbose:
            print("Computed final chemical potentials.")

        return coef, chemical_potentials

    def plot_oxigen_reaccion(self, ):

        def plot_free_energy_changes(values, labels):
            
            """
            Plot the free energy change profile for the Oxygen Evolution Reaction (OER) mechanism.

            Parameters:
            - OER_free_energy_change_Ueq: List or numpy array containing the free energy change for each step at equilibrium potential.
            - OER_free_energy_change_U0: List or numpy array containing the free energy change for each step at standard potential.
            """
            # Crear la figura y los ejes
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

            # Configurar el eje y los límites para el primer plot
            labels = labels
            values = values
            N = values.shape[0]

            # Calculamos los valores acumulativos de energía libre
            y_values = np.array([np.sum(values[:i]) for i in range(N + 1)])

            # Determinamos el paso limitante de la reacción
            limiting_step = np.argmax(values) + 1
            values_std = np.std(y_values)

            # Configuración del primer panel (perfil de energía)
            ax1.set_xlim(0, N + 1)
            ax1.set_ylim(np.min(y_values) - values_std * 0.1, np.max(y_values) + values_std * 0.1)
            ax1.set_xlabel('Reaction Step', fontsize=12)
            ax1.set_ylabel('Free Energy Change (eV)', fontsize=12)
            ax1.set_title('Oxygen Evolution Reaction (OER) Energy Profile', fontsize=14)
            ax1.grid(True, linestyle='--', alpha=0.6)

            # Añadir línea de referencia en y = 0
            ax1.plot([0, N + 1], [0, 0], color='black', alpha=.4, linestyle='--', linewidth=2, label='Reference Line')

            # Dibujar cada estado como una línea horizontal y vertical en el perfil de energía
            for i in range(N + 1):
                ax1.plot([i, i + 1], [y_values[i], y_values[i]], color='blue', linewidth=3)
                if i < values.shape[0]:
                    ax1.plot([i + 1, i + 1], [y_values[i], y_values[i + 1]], color='blue', linewidth=3)
                ax1.text(i + 0.5, y_values[i] + 0.1, labels[i], ha='center', va='bottom', fontsize=10, color='blue')

            # Dibujar una flecha indicando el paso limitante
            ax1.arrow(limiting_step - 0.1, y_values[limiting_step - 1], 0, values[limiting_step - 1],
                      head_width=0.05, head_length=0.2, fc='red', ec='red', linewidth=2)
            ax1.text(limiting_step - 0.2, y_values[limiting_step - 1] + values[limiting_step - 1] / 2, f'Limiting Step : {np.max(values):.2f} eV',
                     fontsize=10, color='red', rotation=90, va='center')

            # Configurar el segundo plot (barras de energía libre para cada reacción)
            ax2.set_xlabel('Reaction Step', fontsize=12)
            ax2.set_ylabel('Free Energy Change (eV)', fontsize=12)
            ax2.set_title('Free Energy Change at Standard Potential (U = 0)', fontsize=14)
            ax2.grid(True, linestyle='--', alpha=0.6)

            reactions = [f'R{i}' for i, n in enumerate(values) ]
            ax2.bar(reactions, values, color='green', alpha=0.7)

            # Configurar el tercer panel para mostrar una tabla con los valores sin usar pandas
            ax3.axis('off')
            column_labels = ['Step', 'Free Energy Change (eV)']
            table_data = [[i + 1, f'{values[i]:.2f}'] for i in range(N)]

            # Añadir la tabla al tercer panel
            table = ax3.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center', bbox=[0.2, 0, 0.6, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)

            # Ajustar el layout y mostrar la gráfica
            plt.tight_layout()
            plt.subplots_adjust(hspace=0.5)
            plt.show()

        include_O2 = True
        resting_state = 'OH'

        OER_ads = ['OH', 'O', 'OOH', '*'] if not include_O2 else ['OH', 'O', 'OOH', 'O2', '*']
        OER_ads = OER_ads[OER_ads.index(resting_state):] + OER_ads[:OER_ads.index(resting_state)]

        O2_n, H2O_n, e_n, OH_n = 0, 0, 0, 0
        step_n = len(OER_ads)

        reactants = {
            f"{ads if ads=='*' else f'*{ads}'}{'i' if i == 0 else 'f' if i == 4 else ''}": {
                'OH-': 4 - i,
                'e-': i,
                'O2': (O2_n := O2_n + (1 if (ads == '*' and  i > 0) or (ads == '*' and i == 4) else 0)),
                'H2O': (H2O_n := H2O_n + (1 if (ads == 'O' and i > 0) or (ads == '*' and i == 4) or (ads == '*' and  i > 0) else 0)),
            }
            for i, ads in enumerate(OER_ads + [OER_ads[0]])
        } if not include_O2 else {
            f"{ads if ads=='*' else f'*{ads}'}{'i' if i == 0 else 'f' if i == 5 else ''}": {
                'OH-': 4-(OH_n := OH_n + (1 if (ads != '*' and i > 0) else 0)),
                'e-': (e_n := e_n + (1 if (ads != '*' and i > 0) else 0)),
                'O2': (O2_n := O2_n + (1 if (ads == '*' and  i > 0) or (ads == '*' and i == 5) else 0)),
                'H2O': (H2O_n := H2O_n + (1 if (ads == 'O' and i > 0) or (ads == 'O2' and i > 0) else 0)),
            }
            for i, ads in enumerate(OER_ads + [OER_ads[0]])
        }

        states_labels = [
            f"{('*' + n) if '*' not in n else n}{'i' if i == 0 else 'f' if i == step_n else ''}"
            for i, n in enumerate(OER_ads + [OER_ads[0]])
        ]

        labels = np.array(states_labels)
        for  (reac_i,reac), reac_ads in zip(reactants.items(), OER_ads+[OER_ads[0]]):
            reac_ads_key = reac_ads if reac_ads == '*' else f'*{reac_ads}'
            self.add_relevant_reaction({reac_ads_key: 1, **reac}, {})

        U0 = np.dot(self.RR, self.mu_U[0])
        Ueq = np.dot(self.RR, self.mu_U[1])
        
        OER_free_energy_change_Ueq = Ueq[1:] - Ueq[:-1] 
        OER_free_energy_change_U0 = U0[1:] - U0[:-1] 
        
        ORR_free_energy_change_Ueq = Ueq[::-1][1:] - Ueq[::-1][:-1] 
        ORR_free_energy_change_U0 = U0[::-1][1:] - U0[::-1][:-1] 

        plot_free_energy_changes(OER_free_energy_change_Ueq, labels)
        plot_free_energy_changes(ORR_free_energy_change_Ueq, labels[::-1])

    def plot_oxigen_reaccion_dual_site(self, ):

        def plot_free_energy_changes(values, labels):
            
            """
            Plot the free energy change profile for the Oxygen Evolution Reaction (OER) mechanism.

            Parameters:
            - OER_free_energy_change_Ueq: List or numpy array containing the free energy change for each step at equilibrium potential.
            - OER_free_energy_change_U0: List or numpy array containing the free energy change for each step at standard potential.
            """
            from matplotlib.gridspec import GridSpec

            # Crear la figura y los ejes
            #fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

            # Configurar el tamaño de la figura
            fig = plt.figure(figsize=(10, 8))

            # Crear la disposición de la cuadrícula
            gs = GridSpec(2, 2, figure=fig)

            # Crear los ejes
            ax1 = fig.add_subplot(gs[0, 0])  # Primer gráfico (arriba izquierda)
            ax2 = fig.add_subplot(gs[1, 0])  # Segundo gráfico (abajo izquierda)
            ax3 = fig.add_subplot(gs[:, 1])  # Tercer gráfico (derecha, ocupa ambas filas)

            # Configurar el eje y los límites para el primer plot
            labels = labels
            values = values
            N = values.shape[0]

            # Calculamos los valores acumulativos de energía libre
            y_values = np.array([np.sum(values[:i]) for i in range(N + 1)])

            # Determinamos el paso limitante de la reacción
            limiting_step = np.argmax(values) + 1
            values_std = np.std(y_values)

            # Configuración del primer panel (perfil de energía)
            ax1.set_xlim(0, N + 1)
            ax1.set_ylim(np.min(y_values) - values_std * 0.1, np.max(y_values) + values_std * 0.1)
            ax1.set_xlabel('Reaction Step', fontsize=12)
            ax1.set_ylabel('Free Energy Change (eV)', fontsize=12)
            ax1.set_title('Oxygen Evolution Reaction (OER) Energy Profile', fontsize=14)
            ax1.grid(True, linestyle='--', alpha=0.6)

            # Añadir línea de referencia en y = 0
            ax1.plot([0, N + 1], [0, 0], color='black', alpha=.4, linestyle='--', linewidth=2, label='Reference Line')

            # Dibujar cada estado como una línea horizontal y vertical en el perfil de energía
            for i in range(N + 1):
                ax1.plot([i, i + 1], [y_values[i], y_values[i]], color='blue', linewidth=3)
                if i < values.shape[0]:
                    ax1.plot([i + 1, i + 1], [y_values[i], y_values[i + 1]], color='blue', linewidth=3)
                ax1.text(i + 0.5, y_values[i] + 0.1, labels[i], ha='center', va='bottom', fontsize=10, color='blue')

            # Dibujar una flecha indicando el paso limitante
            ax1.arrow(limiting_step - 0.1, y_values[limiting_step - 1], 0, values[limiting_step - 1],
                      head_width=0.05, head_length=0.2, fc='red', ec='red', linewidth=2)
            ax1.text(limiting_step - 0.2, y_values[limiting_step - 1] + values[limiting_step - 1] / 2, f'Limiting Step : {np.max(values):.2f} eV',
                     fontsize=10, color='red', rotation=90, va='center')

            # Configurar el segundo plot (barras de energía libre para cada reacción)
            ax2.set_xlabel('Reaction Step', fontsize=12)
            ax2.set_ylabel('Free Energy Change (eV)', fontsize=12)
            ax2.set_title('Free Energy Change at Standard Potential (U = 0)', fontsize=14)
            ax2.grid(True, linestyle='--', alpha=0.6)

            reactions = [f'R{n}' for n in range(values.shape[0])]
            ax2.bar(reactions, values, color='green', alpha=0.7)

            # Configurar el tercer panel para mostrar una tabla con los valores sin usar pandas
            ax3.axis('off')
            column_labels = ['Step', 'Free Energy Change (eV)']
            table_data = [[i + 1, f'{values[i]:.2f}'] for i in range(N)]

            # Añadir la tabla al tercer panel
            table = ax3.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center', bbox=[0.2, 0, 0.6, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)

            # Ajustar el layout y mostrar la gráfica
            plt.tight_layout()
            #plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
            #plt.subplots_adjust(hspace=0.5)

        def plot_absotion_energy(states_matrix_energy, labels=None):
            num_states, num_conditions = states_matrix_energy.shape

            ind = np.arange(num_conditions)  # posiciones de las condiciones
            width = 0.15  # ancho de cada barra

            fig, ax = plt.subplots(figsize=(10, 6))

            pastel_colors = [
                '#AEC6CF',  # Azul pastel
                '#FFB347',  # Naranja pastel
                '#77DD77',  # Verde pastel
                '#FF6961',  # Rojo pastel
                '#CDA4DE'   # Morado pastel
            ]
            
            # Repetir la paleta de colores si hay más estados que colores
            if num_states > len(pastel_colors):
                pastel_colors = pastel_colors * (num_states // len(pastel_colors) + 1)
            
            # Graficar cada estado
            for i in range(num_states):
                ax.bar(ind + i*width, states_matrix_energy[i, :] - states_matrix_energy[0, 0], 
                       width, label=f'State {i+1}', color=pastel_colors[i])
            
            # Configurar etiquetas del eje x
            if labels is not None and len(labels) >= 1:
                condition_labels = labels[0]
            else:
                condition_labels = [f'Condición {j+1}' for j in range(num_conditions)]
            
            ax.set_xlabel('Condición', fontsize=12)
            ax.set_ylabel('dG', fontsize=12)
            ax.set_title('Energías de Adsorción por Estado y Condición', fontsize=14)
            ax.set_xticks(ind + width*(num_states-1)/2)
            ax.set_xticklabels(condition_labels, fontsize=10)
            
            # Configurar leyenda con nombres de los estados
            if labels is not None and len(labels) >= 2:
                state_labels = labels[1]
                # Actualizar etiquetas de la leyenda
                handles, _ = ax.get_legend_handles_labels()
                new_handles = []
                new_labels = []
                for i in range(num_states):
                    new_handles.append(handles[i])
                    new_labels.append(state_labels[i] if i < len(state_labels) else f'Estado {i+1}')
                

            # Añadir valores encima de las barras
            for i in range(num_states):
                for j in range(num_conditions):
                    ax.text(ind[j] + i*width, states_matrix_energy[i, j] - states_matrix_energy[0, 0] + 0.05, 
                            f'{labels[i, j].split('+')[0][1:]}', ha='center', va='bottom', fontsize=8)


            plt.tight_layout()
            #plt.savefig('plot_absotion_energy.png', dpi=300)

            plt.show()

        include_O2 = False
        allow_wraparound = True
        resting_state = '*'

        OER_ads = ['OH', 'O', 'OOH', '*'] if not include_O2 else ['OH', 'O', 'OOH', 'O2', '*']
        OER_ads = OER_ads[OER_ads.index(resting_state):] + OER_ads[:OER_ads.index(resting_state)]

        O2_n, H2O_n, e_n, OH_n = 0, 0, 0, 0
        step_n = len(OER_ads)

        reactants = {
            f"{ads if ads=='*' else f'*{ads}'}{'i' if i == 0 else 'f' if i == 4 else ''}": {
                'OH-': 4 - i,
                'e-': i,
                'O2': (O2_n := O2_n + (1 if (ads == '*' and  i > 0) or (ads == '*' and i == 4) else 0)),
                'H2O': (H2O_n := H2O_n + (1 if (ads == 'O' and i > 0) or (ads == '*' and i == 4) or (ads == '*' and  i > 0) else 0)),
            }
            for i, ads in enumerate(OER_ads + [OER_ads[0]])
        } if not include_O2 else {
            f"{ads if ads=='*' else f'*{ads}'}{'i' if i == 0 else 'f' if i == 5 else ''}": {
                'OH-': 4-(OH_n := OH_n + (1 if (ads != '*' and i > 0) else 0)),
                'e-': (e_n := e_n + (1 if (ads != '*' and i > 0) else 0)),
                'O2': (O2_n := O2_n + (1 if (ads == '*' and  i > 0) or (ads == '*' and i == 5) else 0)),
                'H2O': (H2O_n := H2O_n + (1 if (ads == 'O' and i > 0) or (ads == 'O2' and i > 0) else 0)),
            }
            for i, ads in enumerate(OER_ads + [OER_ads[0]])
        }

        states_labels = [
            f"{('*' + n) if '*' not in n else n}{'i' if i == 0 else 'f' if i == step_n else ''}"
            for i, n in enumerate(OER_ads + [OER_ads[0]])
        ]

        labels = []
        states_matrix_labels = np.zeros( (len(states_labels),len(states_labels) ), dtype='U90')
        states_matrix_energy = np.zeros( (len(states_labels),len(states_labels) ), dtype=np.float64)

        for A_i, state_A in enumerate(states_labels):
            for B_i, state_B in enumerate(states_labels):
                A =  state_A[:-1] if state_A[-1] in ['i','f'] else state_A
                B =  state_B[:-1] if state_B[-1] in ['i','f'] else state_B

                reaction_dict = {f'{A}_{B}': 1}
                for state in [state_A, state_B]:
                    
                    for key, item in reactants[state].items():
                        if key in reaction_dict:
                            reaction_dict[key] += item
                        else:
                            reaction_dict[key] = item

                name = ' + '.join( [f'{item} {key}' for key, item in reaction_dict.items() ] )

                labels.append( name )
                states_matrix_labels[A_i, B_i] = name 
                states_matrix_energy[A_i, B_i] = 0 

                self.add_relevant_reaction( reaction_dict, {} )

        labels = np.array(labels)

        U0 = np.dot(self.RR, self.mu_U[0])
        Ueq = np.dot(self.RR, self.mu_U[1])
        
        N = int(states_matrix_labels.shape[0])
        states_matrix_energy = U0.reshape((N, N))

        # 2. Define allowed transitions [transition graph]
        transitions = generate_allowed_transitions(N, allow_wraparound=allow_wraparound)
        
        # 3. Select the initial and final states (using 0-based indices)
        initial_states = [ (0, 0), (0, 0), (0, 0) ] # corresponds to (1,1) in 1-based notation
        final_states   = [ (N-1,N-1), (0,N-1), (N-1, 0) ] # corresponds to (4,4) in 1-based notation
        initial_states = [ (0, 0) ] # corresponds to (1,1) in 1-based notation
        final_states   = [ (N-1,N-1) ] # corresponds to (4,4) in 1-based notation

        all_paths = list(
            item 
            for initial_state, final_state in zip(initial_states, final_states)
            for item in dfs_search_paths(
                current=initial_state,
                destination=final_state,
                transitions=transitions,
                E=states_matrix_energy
            )
        )
        print(f"Found {len(all_paths)} possible paths.")

        # 5. Among all paths, we look for the path that MINIMIZES the maximum step difference
        best_path = None
        best_value = float("inf")  # For minimization, start at +∞
        path_lenth = float("inf")
        for path in all_paths:
            barrier = evaluate_path(path, states_matrix_energy)  # the highest step difference in the path
            if barrier < best_value:
                best_value = barrier
                best_path = path
                path_lenth = len(path)

            elif barrier == best_value and len(path) < path_lenth:
                best_value = barrier
                best_path = path
                path_lenth = len(path)

        # 6. Print results
        print(f"Found {len(all_paths)} possible paths.")
        print("Path with the smallest maximum energy difference (lowest barrier):")
        print('Best path: ', ['-'.join([np.array(OER_ads + [OER_ads[0]])[m] for m in n]) for n in best_path] )
        print(f"Barrier: {best_value:.3f}")
        
        #plot_free_energy_changes( np.array([states_matrix_energy[n[0], n[1]] for n in best_path[1:]]) - np.array([states_matrix_energy[n[0], n[1]] for n in best_path[:-1]]), 
        #        [states_matrix_labels[n[0], n[1]] for n in best_path] )
        #plt.show()

        plot_absotion_energy(states_matrix_energy, states_matrix_labels)
        plt.show()

    def convex_hull(self, non_relevant=True):
        f = 1
        
        composition_ref = {'Ni':6*f, 'Fe':2*f, 'V':0, 'K':2*f, 'H':8*f, 'O':20*f}
        E_ref = -168.707*f
        #composition_ref = {'Ni':8*f, 'Fe':0*f, 'V':0, 'K':2*f, 'H':8*f, 'O':20*f}
        #E_ref = -157.177*f

        G_U_spc = np.zeros( (2, self.N_states) )
        data_spc = np.zeros( (self.N_states, 6) )

        if non_relevant:
            G_U_spc = np.zeros( (2, self.NR_states_N) )
            data_spc = np.zeros( (self.NR_states_N, 6) )

            states = self.NR_states
            species = self.NR_species

        for Ui, Uidx in enumerate([0, self.U_points-1]):

            for i, (state_name, state_data) in enumerate(self.NR_states.items()):

                charge, composition = parse_species(state_name)
                if True:
                    R = np.zeros( self.mu_pH_U.shape[2] )
                    #R[state_data[0]] = 1
                    G_state = self.NR_G[state_name]

                    # evaluate diferences 
                    delta_dict = {
                        s: float(composition.get(s, 0)) - float(composition_ref.get(s, 0))
                        for s in self.species
                    }

                    if False:
                        # ==== Oxigen O ==== #
                        if 'O' in self.species:
                            try:
                                R[self.states['H2O'][0]] += -float(delta_dict.get('O',0))/2 * 2
                                R[self.states['e-'][0]] += float(delta_dict.get('O',0))/2 * 4
                                R[self.states['H+'][0]] += float(delta_dict.get('O',0))/2 * 4
                                
                            except: print('Can not equilibrate O')

                        # ==== Hidrogen H ==== #
                        if 'H' in self.species:
                            try:
                                R[self.states['e-'][0]] += -float(delta_dict.get('H',0))/2 * 2
                                R[self.states['H+'][0]] += -float(delta_dict.get('H',0))/2 * 2
                            except: print('Can not equilibrate H')

                        # ==== Potasium K ==== #
                        if 'K' in self.species:
                            try:
                                R1 = copy.deepcopy(R)
                                #R[self.states['e-'][0]] += -float(delta_dict.get('K',0)) 
                                #R[self.states['K+'][0]] += -float(delta_dict.get('K',0)) 
                                
                                R[self.states['KOH'][0]] += -float(delta_dict.get('K',0)) 
                                R[self.states['H2O'][0]] += float(delta_dict.get('K',0))
                                R[self.states['H+'][0]] += -float(delta_dict.get('K',0))
                                R[self.states['e-'][0]] += -float(delta_dict.get('K',0))
                                #R1 = copy.deepcopy(R)
                                '''
                                R[self.states['V2H8O14K2'][0]] += -float(delta_dict.get('K',0))/2
                                R[self.states['V2O4'][0]] += float(delta_dict.get('K',0))/2

                                R[self.states['H2O'][0]] +=  float(delta_dict.get('K',0))/2*14 - float(delta_dict.get('K',0))/2*4
                                R[self.states['H+'][0]]  +=  float(delta_dict.get('K',0))/2*8  - (float(delta_dict.get('K',0))/2*14 - float(delta_dict.get('K',0))/2*4)*2

                                R[self.states['e-'][0]]  += float(delta_dict.get('K',0))/2*8  - (float(delta_dict.get('K',0))/2*14 - float(delta_dict.get('K',0))/2*4)*2
                                '''
                                
                                '''
                                Rd = R - R1
                                delta_dict1 = {
                                    s: 0
                                    for s in self.species
                                }
                                for i1, (state_name1, state_data1) in enumerate(self.states.items()):
                                    if Rd[i1] != 0:
                                        charge1, composition1 = parse_species(state_name1)                                    
                                        for s in self.species:
                                            delta_dict1[s] += Rd[i1] * composition1.get(s, 0)

                                print(delta_dict1)
                                '''
                            except: print('Can not equilibrate K')
                        
                        # ==== Iron Fe ==== #
                        if 'Fe' in self.species:
                            try:
                                R1 = copy.deepcopy(R)
                                
                                '''
                                R[self.states['FeOOH'][0]] += -float(delta_dict.get('Fe',0))/2 * 2
                                R[self.states['H2O'][0]] += float(delta_dict.get('Fe',0))/2 * 2 * 2
                                R[self.states['e-'][0]] += -float(delta_dict.get('Fe',0))/2 * 2 * 3
                                R[self.states['H+'][0]] += -float(delta_dict.get('Fe',0))/2 * 2 * 3
                                '''
                                #'''
                                R[self.states['Fe2O3'][0]] += -float(delta_dict.get('Fe',0))/2 
                                R[self.states['H2O'][0]] += float(delta_dict.get('Fe',0))/2 * 3 
                                R[self.states['e-'][0]] += -float(delta_dict.get('Fe',0))/2 * 3 * 2
                                R[self.states['H+'][0]] += -float(delta_dict.get('Fe',0))/2 * 3 * 2
                                #'''

                                '''
                                R[self.states['V8Fe4H2O24'][0]] += -float(delta_dict.get('Fe',0))/4
                                R[self.states['V2O4'][0]] += float(delta_dict.get('Fe',0))/4*4
                                R[self.states['H2O'][0]] +=  float(delta_dict.get('Fe',0))/4*24 - float(delta_dict.get('Fe',0))/4*4*4
                                R[self.states['H+'][0]]  +=  float(delta_dict.get('Fe',0))/4*2  - (float(delta_dict.get('Fe',0))/4*24 - float(delta_dict.get('Fe',0))/4*4*4)*2
                                R[self.states['e-'][0]]  += float(delta_dict.get('Fe',0))/4*2  - (float(delta_dict.get('Fe',0))/4*24 - float(delta_dict.get('Fe',0))/4*4*4)*2
                                '''
                                '''
                                R[self.states['Fe2Ni2O6'][0]] += -float(delta_dict.get('Fe',0))/2
                                R[self.states['NiO2'][0]] += float(delta_dict.get('Fe',0))/2*2
                                R[self.states['H2O'][0]] +=  float(delta_dict.get('Fe',0))/2*6 - float(delta_dict.get('Fe',0))/2*2*2
                                R[self.states['H+'][0]]  +=  - (float(delta_dict.get('Fe',0))/2*6 - float(delta_dict.get('Fe',0))/2*2*2)*2
                                R[self.states['e-'][0]]  +=  - (float(delta_dict.get('Fe',0))/2*6 - float(delta_dict.get('Fe',0))/2*2*2)*2
                                '''

                            except: print('Can not equilibrate Fe')

                        # ==== Vanadium V ==== #
                        if 'V' in self.species:
                            try:
                                R1 = copy.deepcopy(R)
                                '''
                                R[self.states['HV2O5 -'][0]] += -float(delta_dict.get('V',0))/2 
                                R[self.states['H2O'][0]] += float(delta_dict.get('V',0))/2*5
                                R[self.states['H+'][0]] += -float(delta_dict.get('V',0))/2*9
                                R[self.states['e-'][0]] += -float(delta_dict.get('V',0))/2*8
                                '''
                                #'''
                                R[self.states['V2O4'][0]] += -float(delta_dict.get('V',0))/2 
                                R[self.states['H2O'][0]] += float(delta_dict.get('V',0))/2*4
                                R[self.states['H+'][0]] += -float(delta_dict.get('V',0))/2*8
                                R[self.states['e-'][0]] += -float(delta_dict.get('V',0))/2*8
                                #'''

                                '''
                                R[self.states['V8Fe4H2O24'][0]] += -float(delta_dict.get('V',0))/8
                                R[self.states['Fe2O3'][0]] += float(delta_dict.get('V',0))/8*2
                                R[self.states['H2O'][0]] +=  float(delta_dict.get('V',0))/8*24 - float(delta_dict.get('V',0))/8*2*3
                                R[self.states['H+'][0]]  +=  float(delta_dict.get('V',0))/8*2  - (float(delta_dict.get('V',0))/8*24 - float(delta_dict.get('V',0))/8*2*3)*2
                                R[self.states['e-'][0]]  += float(delta_dict.get('V',0))/8*2  - (float(delta_dict.get('V',0))/8*24 - float(delta_dict.get('V',0))/8*2*3)*2
                                '''

                            except: print('Can not equilibrate V')

                        # ==== Niquel Ni ==== #
                        if 'Ni' in self.species:
                            try: 
                                R1 = copy.deepcopy(R)
                                #'''
                                R[self.states['NiO2'][0]] += -float(delta_dict.get('Ni',0))/2 * 2
                                R[self.states['H2O'][0]] += float(delta_dict.get('Ni',0))/2 * 4
                                R[self.states['e-'][0]] += -float(delta_dict.get('Ni',0))/2*8
                                R[self.states['H+'][0]] += -float(delta_dict.get('Ni',0))/2*8
                                #'''

                                '''
                                R[self.states['V8Ni4H16O32'][0]] += -float(delta_dict.get('Ni',0))/4
                                R[self.states['V2O4'][0]] += float(delta_dict.get('Ni',0))/4*4
                                R[self.states['H2O'][0]] +=  float(delta_dict.get('Ni',0))/4*32 - float(delta_dict.get('Ni',0))/4*4*4
                                R[self.states['H+'][0]]  +=  float(delta_dict.get('Ni',0))/4*16  - (float(delta_dict.get('Ni',0))/4*32 - float(delta_dict.get('Ni',0))/4*4*4)*2
                                R[self.states['e-'][0]]  += float(delta_dict.get('Ni',0))/4*16  - (float(delta_dict.get('Ni',0))/4*32 - float(delta_dict.get('Ni',0))/4*4*4)*2
                                '''
                                '''
                                R[self.states['Fe2Ni2O6'][0]] += -float(delta_dict.get('Ni',0))/2
                                R[self.states['Fe2O3'][0]] += float(delta_dict.get('Ni',0))/2
                                R[self.states['H2O'][0]] +=  float(delta_dict.get('Ni',0))/2*6 - float(delta_dict.get('Ni',0))/2*3
                                R[self.states['H+'][0]]  +=  - (float(delta_dict.get('Ni',0))/2*6 - float(delta_dict.get('Ni',0))/2*3)*2
                                R[self.states['e-'][0]]  +=  - (float(delta_dict.get('Ni',0))/2*6 - float(delta_dict.get('Ni',0))/2*3)*2
                                '''
                                
                            except: print('Can not equilibrate Ni')

                        try:
                            R[self.states['e-'][0]] += float(dC)
                        except: pass

                    else:
                        names = [ 'V2K2H8O14', 'V2O4', 'Fe2O3', 'NiO2', 'FeO', 'H2O', 'H+', 'e-']
                        M = np.array([
                            [  0,  0,  0,  0,   0,   0,  1, -1],  # e-
                            [  2,  2,  0,  0,   0,   0,  0,  0],  # V
                            [  0,  0,  2,  0,   1,   0,  0,  0],  # Fe
                            [  0,  0,  0,  1,   0,   0,  0,  0],  # Ni
                            [  8,  0,  0,  0,   0,   2,  1,  0],  # H
                            [ 14,  4,  3,  2,   1,   1,  0,  0],  # O
                            [  2,  0,  0,  0,   0,   0,  0,  0],  # K
                        ], dtype=float)

                        names = [   'V2O4',  'NiO2', 'FeO', 'H2O', 'H+', 'e-']
                        M = np.array([
                            [    0,   0,  0,  0,  1, -1],  # e-
                            [    2,   0,  0,  0,  0,  0],  # V
                            [    0,   0,  1,  0,  0,  0],  # Fe
                            [    0,   1,  0,  0,  0,  0],  # Ni
                            [    0,   0,  0,  2,  1,  0],  # H
                            [    4,   2,  1,  1,  0,  0],  # O
                            [    0,   0,  0,  0,  0,  0],  # K
                        ], dtype=float)

                        b = np.array([0]+[float(delta_dict.get(s,0)) for s in ['V','Fe','Ni','H','O','K',] ], dtype=float)
                        
                        coeff, residuals, rank, s = lstsq(M, b, rcond=None)
                        
                        for coeff_i, coeff_v in enumerate(coeff):
                            R[self.states[ names[coeff_i] ][0]] = coeff_v

                    delta_dict1 = { s: 0 for s in self.species }
                    for i1, (state_name1, state_data1) in enumerate(self.states.items()):
                        if R[i1] != 0:
                            charge1, composition1 = parse_species(state_name1)                                    
                            for s in self.species:
                                delta_dict1[s] += R[i1] * composition1.get(s, 0)

                    Tcharge, Tcomposition = parse_species(state_name)
                    # evaluate diferences 
                    delta_list = [
                        float(Tcomposition.get(s, 0)) - float(composition_ref.get(s, 0)) - delta_dict1.get(s, 0)
                        for s in self.species
                    ]
                    if np.abs(np.sum(delta_list)) > .01:
                        print( np.sum(delta_list), delta_list )
                        print(delta_dict1, state_name)
                        print(delta_dict)
                    
                    #print('coef',b, coeff, delta_dict1)

                    dG = G_state - np.dot(R, self.mu_pH_U[0, Uidx, :] ) - E_ref
                    G_U_spc[Ui, i] = dG/f

                    #print(R , self.mu_pH_U[0, Uidx, :], np.dot(R, self.mu_pH_U[0, Uidx, :] ), E_ref, dG)
                    #afsdafsd
                    for si,ss in enumerate(self.species):
                        data_spc[i,si] = composition.get(ss, 0)


        species_name = [ self.non_relevant_specie_by_idx(specie_idx) for  specie_idx in range(self.NR_states_N) ]

        for si, ss in enumerate(self.species):
            # Intervalos deseados para los ejes
            xlim = (0, 2)
            ylim = (-10, 2)
            
            # Crear figura y ejes
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Crear colormap y normalizador para la especie actual
            cmap = plt.get_cmap("plasma")
            if ss=='V':
                norm = mcolors.Normalize(vmin=0, vmax=8)
            elif ss=='K':
                norm = mcolors.Normalize(vmin=28, vmax=36)
            elif ss=='O':
                norm = mcolors.Normalize(vmin=310, vmax=335)
            elif ss=='Fe':
                norm = mcolors.Normalize(vmin=0, vmax=8)
            elif ss=='Ni':
                norm = mcolors.Normalize(vmin=0, vmax=8)
            else:
                try:
                    norm = mcolors.Normalize(vmin=np.mean(data_spc[:, si]), vmax=np.max(data_spc[:, si]))
                except:
                    norm = mcolors.Normalize(vmin=0, vmax=10)

            # Número de líneas (asumiendo que G_U_spc tiene forma (2, n_estados))
            n_lines = G_U_spc.shape[1]
            
            # Construir de forma vectorizada el array de segmentos:
            # Cada segmento es [[x0, y0], [x1, y1]], usando self.U_values[0] y self.U_values[-1] como extremos en X
            segments = np.empty((n_lines, 2, 2))
            segments[:, 0, 0] = self.U_values[0]       # x0 para todos los segmentos
            segments[:, 1, 0] = self.U_values[-1]      # x1 para todos los segmentos
            segments[:, 0, 1] = G_U_spc[0, :]           # y0 para cada segmento
            segments[:, 1, 1] = G_U_spc[1, :]           # y1 para cada segmento
            
            # Calcular de forma vectorizada los colores para cada línea
            # Se utiliza data_spc[:, si], que contiene el valor asociado a cada estado para la especie actual
            colors = cmap(norm(data_spc[:, si]))
            
            # Crear la colección de líneas y agregarla al eje
            lc = LineCollection(segments, colors=colors, alpha=0.6)
            ax.add_collection(lc)
            
            # Configurar límites y etiquetas de los ejes
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_xlabel("X axis")
            ax.set_ylabel("Y axis")
            ax.set_title(f"Labeled Lines Plot {ss}")
            ax.grid(True)
            
            plt.show()

if __name__ == "__main__":
    pd = PhaseDiagram()

    pd.add_state('H2',)
    pd.add_state('O2')
    pd.add_state('H2O')
    pd.add_state('e-', -1)
    pd.add_state('H+', 1)

    #pd.add_state('Ni(OH)2', 0)           # Hidróxido de níquel (II)
    pd.add_state('NiOOH', 0)             # Oxohidróxido de níquel    
    #pd.add_state('Ni(OH)3 -', -1, CC=10**-6)  
    #pd.add_state('Ni(OH)4 2-', -2, CC=10**-6)  

    pd.add_state('Ni', 0)                # Níquel metálico
    pd.add_state('Ni2+', 2, CC=10**-6)              # Ion níquel (II)

    pd.add_state('NiO', 0)               # Óxido de níquel
    pd.add_state('NiO2', 0)              # Óxido de níquel (IV)

    pd.add_state('Ni(OH)3 -', -1, CC=10**-6)              # Ion níquel (II)
    pd.add_state('Ni3O4', 0)             # Óxido de níquel (III)
    pd.add_state('Ni2O3', 0)             # Óxido de níquel (III)
    pd.add_state('HNiO2 -', -1, CC=10**-6)             # Oxohidróxido de níquel   

    # Especies de vanadio
    pd.add_state('V', 0, )
    pd.add_state('V2+', 2, CC=1e-6)
    pd.add_state('VO', 0)
    pd.add_state('VOH +', 1, CC=1e-6)
    pd.add_state('VOH 2+', 2, CC=1e-6)
    pd.add_state('V3+', 3, CC=1e-6)
    pd.add_state('V2O3', 0)
    pd.add_state('VO+', 1, CC=1e-6)

    pd.add_state('VO 2+', 2, CC=1e-6)  # IV, nota el sufijo para diferenciar
    pd.add_state('V2O4', 0)
    pd.add_state('V5O9 2-', -2, CC=1e-6)
    pd.add_state('HV2O5 -', -1, CC=1e-6)
    pd.add_state('VO2 +', 1, CC=1e-6)   # V, sufijo para diferenciar
    pd.add_state('V2O5', 0)
    pd.add_state('V4O9 2-', -2, CC=1e-6)
    pd.add_state('H2V10O28 4-', -4, CC=1e-6)
    pd.add_state('HV10O28 5-', -5, CC=1e-6)
    pd.add_state('V10O28 6-', -6, CC=1e-6)
    pd.add_state('HV2O7 3-', -3, CC=1e-6)
    pd.add_state('V2O7 4-', -4, CC=1e-6)
    pd.add_state('V4O12 4-', -4, CC=1e-6)
    
    pd.add_state('H2VO4 -', -1, CC=1e-6)
    pd.add_state('HVO4 2-', -2, CC=1e-6)
    pd.add_state('VO4 3-', -3, CC=1e-6)

    pd.add_state('Fe', 0)  
    pd.add_state('FeO', 0)               
    pd.add_state('Fe(OH)2', 0)               
    pd.add_state('Fe3O4', 0)               
    pd.add_state('FeOOH', 0)                           
    pd.add_state('Fe2+', 2, CC=10**-6)               
    pd.add_state('Fe3+', 3, CC=10**-6)               
    pd.add_state('HFeO2 -', -1, CC=10**-6)               
    pd.add_state('FeO4 2-', -2, CC=10**-6)               
    pd.add_state('Fe2O3', 0)   

    pd.add_state('K', 0)               
    pd.add_state('KOH', 0)  
    pd.add_state('K+', 1, CC=10**-6)  

    #'''
    pd.add_state('V8Fe4H2O24', 0 )  
    pd.add_state('V2Fe2H4O10', 0 )
    pd.add_state('V8Ni4H16O32', 0 )
    pd.add_state('V2H8O14K2', 0 )
    pd.add_state('V4Fe1Ni1O12', 0 )
    pd.add_state('V11Ni1O18', 0 )
    pd.add_state('Fe2Ni2O6', 0 )
    pd.add_state('Fe26Ni4O40', 0 )
    pd.add_state('Fe26Ni4O40', 0 )
    #'''
    #pd.add_state('V8Fe4H2O24', 0 ) 
    #pd.add_state('Fe26Ni4O40', 0 )
    #pd.add_state('V2H8O14K2', 0 )
    #pd.add_state('V8Ni4H16O32', 0 )
    
    #Smolin, Yu.i., Shepelev, Yu.f., Lapshin, A.e., Schwendt, P., Gyepesova, D.(1990). Structure of dipotassium aquadioxotetraperoxodivanadate(V) trihydrate. Acta Crystallographica C (39,1983-), 46.
    #(Authors: Smolin, Yu.i. Shepelev, Yu.f. Lapshin, A.e. Schwendt, P. Gyepesova, D. )
    #(Journal: Acta Crystallographica C (39,1983-)
    pd.add_state('V2K2H8O14', 0 )
    #############################################
    #         #
    #############################################
    def add_state_LDH(Fe:int, Ni:int, V:int, K:int, H:int, O:int, q:0, pd):
        name = f'Fe{Fe}Ni{Ni}V{V}K{K}H{H}O{O}'
        pd.add_non_relevant_state(name, q)  
        return pd

    def add_reaction_LDH(Fe:int, Ni:int, V:int, K:int, H:int, O:int, G_LDH:float,
                G:dict, pd):

        name = f'Fe{Fe}Ni{Ni}V{V}K{K}H{H}O{O}'
        G[name] = G_LDH
     
        products_dict = { name:1 }

        pd.add_non_relevant_reaction(products_dict, {}, -G_LDH )

        return pd

    conversion_factor = -1 / 96.485
    fact = -1.0/23060.5

    #file_path = '/Users/dimitry/Documents/Data/LDH/Sampling/metadata_242_all.dat'
    #file_path = '/Users/dimitry/Documents/Data/LDH/Sampling/metadata2.dat'
    file_path = '/Users/dimitry/Documents/Data/LDH/Sampling/metadata_111_full.dat'

    dataset_partition = Partition()
    #dataset_partition.read_files(file_location=file_path, source='metadata', verbose=True)

    if debug:
        start_time = time.time()
    Fel, Nil, Vl, Hl, Kl, Ol, El = [], [], [], [], [], [], []

    df = pda.read_csv(file_path, usecols=["Fe", "Ni", "V", "H", "K", "O", "E"])
    #df = df[df["K"] > 25]
    #df = df[df["V"] < 1]
    #df = df[df["Fe"] < 45]
    #df = df[df["O"] > 310]
    print( np.max(df["O"]) )
    #df = df[df["V"] > 15]
    #df = df[df["Fe"] > 15]
    print( df["Fe"] )
    Fel = df["Fe"].astype(float).tolist()
    Nil = df["Ni"].astype(float).tolist()
    Vl  = df["V"].astype(float).tolist()
    Hl  = df["H"].astype(float).tolist()
    Kl  = df["K"].astype(float).tolist()
    Ol  = df["O"].astype(float).tolist()
    El  = df["E"].astype(float).tolist()
    
    if debug:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time : Load LDH data {elapsed_time:.6f} s")
        print( f'{len(El)} Structures ' )

    lower_composition_dict = {}
    #for c_i, c in enumerate(dataset_partition.containers[:]):
    for c_i, c in enumerate(El):
        f = 1
        #Fe, Ni, V, H, K, O = np.array([ c.AtomPositionManager.get_species_count(a) for a in ['Fe', 'Ni', 'V', 'H', 'K', 'O'] ]) * f
        #name = f'{Fe}{Ni}{V}{H}{K}{O}' * f
        #E = c.AtomPositionManager.E 
        
        Fe, Ni, V, H, K, O = Fel[c_i]*f, Nil[c_i]*f, Vl[c_i]*f, Hl[c_i]*f, Kl[c_i]*f, Ol[c_i]*f 
        name = f'{Fe}{Ni}{V}{H}{K}{O}'
        E = El[c_i]*f 

        if E < lower_composition_dict.get(name, [np.inf,0] )[0]:
            lower_composition_dict[f'{Fe}{Ni}{V}{H}{K}{O}'] = [E, {'Fe':Fe, 'Ni':Ni, 'V':V, 'H':H, 'K':K, 'O':O}] 

    for lcd_key, lcd_item in lower_composition_dict.items():
        Fe, Ni, V, H, K, O = np.array([ lcd_item[1][a] for a in ['Fe', 'Ni', 'V', 'H', 'K', 'O'] ])
        pd = add_state_LDH(Fe=Fe, Ni=Ni, V=V, O=O, H=H, K=K, q=0, pd=pd) 

    if debug:
        start_time = time.time()
    
    for lcd_key, lcd_item in lower_composition_dict.items():

        Fe, Ni, V, H, K, O = [ lcd_item[1][a] for a in ['Fe', 'Ni', 'V', 'H', 'K', 'O'] ]
        E = lcd_item[0]
        pd = add_reaction_LDH(Fe=Fe, Ni=Ni, V=V, O=O, H=H, K=K, G_LDH=-E ,#Fe2Ni6=167.7,
            G={'FeO': 8.71, 'NiO2':8.5, 'V2O4':44, 'KOH':11.35, 'H2O':12.202, 'H2':7.016,}, pd=pd)
    
    if debug:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time : Add LDH reactions {elapsed_time:.6f} s")
        print( f'{pd.N_states} states ' )

    if debug:
        start_time = time.time()

    '''
    # TEST #
    pd = add_state_LDH(Fe=0, Ni=8, V=0, O=20, H=8, K=2, q=0, pd=pd)
    pd = add_state_LDH(Fe=2, Ni=10, V=4, O=40, H=16, K=4, q=0, pd=pd)

    pd = add_reaction_LDH1(Fe=0, Ni=8, V=0, O=20, H=8, K=2, G_LDH=157.157 ,#Fe2Ni6=167.7,
    #         G={'Fe3O4': 70.24, 'Ni':13.48, 'V2O5':35.62, 'K+': 4.77, 'H2O':12.202, 'H2':7.016, 'O2':5.48}, pd=pd)
            G={'Fe3O4': 70.24, 'NiO2':11.6, 'V2O5':35.62, 'KOH':13.65, 'H2O':12.202, 'H2':7.016,}, pd=pd)

    pd = add_reaction_LDH1(Fe=2, Ni=10, V=4, O=40, H=16, K=4, G_LDH=360.253 ,#Fe2Ni6=167.7,
    #         G={'Fe3O4': 70.24, 'Ni':13.48, 'V2O5':35.62, 'K+': 4.77, 'H2O':12.202, 'H2':7.016, 'O2':5.48}, pd=pd)
            G={'Fe3O4': 70.24, 'NiO2':11.6, 'V2O5':35.62, 'KOH':13.65, 'H2O':12.202, 'H2':7.016,}, pd=pd)
    '''

    #pd.add_reaction({'K':2, 'V':2, 'H2':4, 'O2':7}, {'V2H8O14K2':1}, -1.527*26)
    #pd.add_reaction({'Ni':4, 'V':8, 'H2':8, 'O2':16}, {'V8Ni4H16O32':1}, -1.771*60)
    #pd.add_reaction({'Fe':2, 'Ni':2, 'O2':3}, {'Fe2Ni2O6':1}, -1.280*10)

    #pd.add_reaction({'KOH':2, 'V2O4':1, 'H2O':8}, {'V2H8O14K2':1, 'H2':5}, 130.04 - 12.202*8 - 44 - 11.35*2)
    #pd.add_reaction({'NiO2': 4, 'V2O4': 4, 'H2O': 8}, {'V8Ni4H16O32':1}, 332.714 - 12.202*8 - 44*4 - 65.5/8*4)
    #pd.add_reaction({'FeO': 2, 'NiO2': 2}, {'Fe2Ni2O6':1}, 47.77 - 8.71*2 - 65.5/8*2)

    names = [ 'V8Fe4H2O24', 'V2Fe2H4O10', 'V8Ni4H16O32', 'V2H8O14K2', 'V4Fe1Ni1O12', 'V11Ni1O18','Fe2Ni2O6', 'Fe26Ni4O40', 'V2K2H8O14']
    E = np.array([240.533, 103.890, 333.314, 131.04, 113.7817, 200.4, 47.77, 371.38, 130.5])
    #pd.add_reaction({'Fe26Ni4O40':1}, {}, -371.38)
    #pd.add_reaction({'V2H8O14K2':1}, {}, -131.04)
    #pd.add_reaction({'V8Fe4H2O24':1}, {}, -240.533)
    #pd.add_reaction({'V8Ni4H16O32':1}, {}, -333.314)
    #pd.add_reaction({'V8Ni4H16O32':1}, {}, -333.314)
           
    for n, e in zip(names, E):
        pd.add_reaction({n:1}, {}, -e)

    pd.add_reaction({'V2O4': 1, },           {}, -44)
    pd.add_reaction({'FeO': 1, },           {}, -10.71)
    pd.add_reaction({'NiO2': 1, },    {}, -65.5/8 ) # 323=-34.52/4  242=99.9/12=8.325   /13.325 65.5/8
    #pd.add_reaction({'Ni': 1, },           {}, -13.1) # 007. 13.25
    pd.add_reaction({'KOH': 1, },  {}, -11.65) # 208=11.3 233=11.65
    pd.add_reaction({'H2O': 1}, {}, -12.202)
    pd.add_reaction({'H2': 1}, {}, -7.0016)
    pd.add_reaction({'e-': 1}, {}, -0)

    #############################################
    # Reacciones para especies de V(II)         #
    #############################################
    pd.add_reaction({'H+': 2, 'e-': 2},             {'H2': 1}, 0.0)
    pd.add_reaction({'H+': 4, 'e-': 4, 'O2': 1},    {'H2O': 2}, 4.92)
    pd.add_reaction({'K': 1, 'O2': .5, 'H2': .5,},  {'KOH': 1, }, -379.08*conversion_factor )
    pd.add_reaction({'K': 1, },  {'K+': 1, 'e-': 1 }, -283.27*conversion_factor )

    #############################################
    # Reacciones para especies de Ni         #
    #############################################
    pd.add_reaction({'Ni': 1, 'O2': .5, },          {'NiO': 1, }, -51610*fact )
    pd.add_reaction({'Ni': 3, 'O2': 2},             {'Ni3O4': 1}, -170150*fact)
    pd.add_reaction({'Ni': 2, 'O2': 1.5},           {'Ni2O3': 1}, -112270*fact )
    pd.add_reaction({'Ni': 1, 'O2': 1},             {'NiO2': 1 }, -51420*fact)
    pd.add_reaction({'Ni': 1, },                    {'Ni2+': 1, 'e-': 2}, -11530*fact)
    pd.add_reaction({'Ni': 1, 'H2': .5, 'O2': 1, 'e-': 1},     {'HNiO2 -': 1}, -83465*fact)
    
    #pd.add_reaction({'Ni': 1, 'O2': 1, 'H2': 1},    {'Ni(OH)2': 1}, 4.74)
    pd.add_reaction({'Ni': 2, 'O2': 2, 'H2': 1},    {'NiOOH': 2, }, 3.406*2)
    #pd.add_reaction({'Ni': 1, 'O2': 1.5, 'H2': 1.5, 'e-': 1},    {'Ni(OH)3 -': 1, }, 6.079)
    #pd.add_reaction({'Ni': 1, 'O2': 2, 'H2': 2, 'e-': 2},    {'Ni(OH)4 2-': 1,}, 7.708)

    #############################################
    # Reacciones para especies de V(II)         #
    #############################################
    pd.add_reaction({'V':1, 'O2':.5}, {'VO':1, }, -404.2*conversion_factor )
    pd.add_reaction({'V':1}, {'V2+':1, 'e-':2}, -218*conversion_factor )
    pd.add_reaction({'V':1, 'O2':.5, 'H2':.5}, {'VOH +':1, 'e-':1 }, -417.4*conversion_factor )

    ############################################
    # Reacciones para especies de V(III)      #
    ############################################
    pd.add_reaction({'V':1}, {'V3+':1, 'e-':3}, -251.3*conversion_factor )
    pd.add_reaction({'V':1, 'O2':.5 }, {'VO+':1, 'e-':1 }, -451.8*conversion_factor )    
    pd.add_reaction({'V':1, 'O2':.5, 'H2':.5}, {'VOH 2+':1, 'e-':2 }, -471.9*conversion_factor)
    pd.add_reaction({'V':2, 'O2':1.5}, {'V2O3':1, }, -1139*conversion_factor )

    #############################################
    # Reacciones para especies de V(IV)        #
    #############################################
    pd.add_reaction({'V':1, 'O2':.5 }, {'VO 2+':1, 'e-':2 }, -446.4*conversion_factor )
    pd.add_reaction({'V':2, 'O2':2 }, {'V2O4':1, }, -1318.6*conversion_factor )
    pd.add_reaction({'V':4, 'O2':4.5, 'e-':2 }, {'V4O9 2-':1, }, -2784*conversion_factor )
    pd.add_reaction({'V':2, 'O2':2.5, 'H2':.5, 'e-':1 }, {'HV2O5 -':1, }, -1508.96*conversion_factor )

    #############################################
    # Reacciones para especies de V(V)         #
    #############################################
    pd.add_reaction({'V':1, 'O2':1, }, {'VO2 +':1, 'e-':1, }, -587*conversion_factor )
    pd.add_reaction({'V':2, 'O2':2.5, }, {'V2O5':1, }, -1419.4*conversion_factor )
    pd.add_reaction({'V':10, 'O2':14, 'H2':1, 'e-':4, }, {'H2V10O28 4-':1, }, -7729*conversion_factor )
    pd.add_reaction({'V':10, 'O2':14, 'H2':.5, 'e-':5, }, {'HV10O28 5-':1, }, -7708*conversion_factor )
    pd.add_reaction({'V':10, 'O2':14, 'e-':6, }, {'V10O28 6-':1, }, -7675*conversion_factor )
    pd.add_reaction({'V':2, 'O2':3.5, 'H2':.5, 'e-':3, }, {'HV2O7 3-':1, }, -1792*conversion_factor )
    pd.add_reaction({'V':2, 'O2':3.5, 'e-':4, }, {'V2O7 4-':1, }, -1720*conversion_factor )
    pd.add_reaction({'V':4, 'O2':6, 'e-':4, }, {'V4O12 4-':1, }, -3202*conversion_factor )

    pd.add_reaction({'V':1, 'O2':2, 'H2':1, 'e-':1, }, {'H2VO4 -':1, }, -1020.9*conversion_factor )
    pd.add_reaction({'V':1, 'O2':2, 'H2':.5, 'e-':2, }, {'HVO4 2-':1, }, -974.9*conversion_factor )
    pd.add_reaction({'V':1, 'O2':2, 'e-':3, }, {'VO4 3-':1, }, -899.1*conversion_factor )

    #############################################
    # Reacciones para especies de V(V)         #
    #############################################
    pd.add_reaction({'Fe': 2, 'O2': 1, },           {'FeO': 2, }, 2.51*2)
    pd.add_reaction({'Fe': 1, 'O2': 1, 'H2': 1,},   {'Fe(OH)2': 1, }, 5.06 )
    pd.add_reaction({'Fe': 3, 'O2': 2, },           {'Fe3O4': 1, }, 10.54 )
    pd.add_reaction({'Fe': 2, 'O2': 2, 'H2': 1,},   {'FeOOH': 2, }, 5.10*2 )
    pd.add_reaction({'Fe': 4, 'O2': 3, },           {'Fe2O3': 2, }, 7.70*2  )
    pd.add_reaction({'Fe': 1, },                    {'Fe2+': 1, 'e-':2}, 0.81764004) #0.88  )
    pd.add_reaction({'Fe': 1, },                    {'Fe3+': 1, 'e-':3}, 0.11  )
    pd.add_reaction({'Fe': 1, 'O2': 1, 'H2': .5, 'e-':1},  {'HFeO2 -': 1}, 3.93  )
    pd.add_reaction({'Fe': 1, 'O2': 2, 'e-':2},  {'FeO4 2-': 1}, 3.34 )

    np.set_printoptions(threshold=np.inf) 

    if debug:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time : add MOx reactions: {elapsed_time:.6f} segundos")
        print( f'{pd.R_num} Reactions ' )

    if debug:
        start_time = time.time()

    mu_pH_U = pd.generate_R(parallel=False)
    #pd.print()

    if debug:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time : evaluate conditions: {elapsed_time:.6f} segundos")
        print( f'{pd.R_num} Reactions ' )

    pd.convex_hull()

    asdconvex_hull

    stable_index_array, stable_index_idx = pd.Mosaic_Stacking(relevant_species=['Ni', 'Fe', 'V', ], 
                                                                parallel=True, reference=None)
    stable_index_array1 = stable_index_array

    stable_index_array, stable_index_idx = pd.Mosaic_Stacking(relevant_species=['Ni', 'Fe', 'V',], 
                                                                parallel=True, reference=stable_index_array, reference_idx=stable_index_idx)

    for i, n in enumerate(['Ni', 'Fe', 'V', ]):
        pd.plot_phase_diagrams( stable_index_array[:,:,i], name=f'{n}_LDH')


    for i, n in enumerate(['Ni', 'Fe', 'V', ]):
        pd.plot_phase_diagrams( stable_index_array1[:,:,i], name=f'{n}_base' )



