import numpy as np
import time

class ConvergenceChecker:
    def __init__(self, logger=None, detailed_record=False, stall_threshold:int=5, information_driven:bool=True):
        """
        Initializes the ConvergenceChecker with optional logging and a flag to maintain detailed records.

        Parameters
        ----------
        logger : logging.Logger, optional
            A logger instance to record events.
        detailed_record : bool, optional
            If True, a detailed history of objective values is stored.
        """
        self.logger = logger
        self.detailed_record = detailed_record
        self._objectives_for_features_history = {}
        self._no_improvement_count_objectives = 0
        self._no_improvement_count_information = 0
        self._no_improvement_count = 0

        self._stall_threshold = stall_threshold
        self._information_driven = information_driven
        self._convergence_type = 'and'

    def _record_objective_for_feature(self, feature_key, generation, current_obj):
        """
        Records and updates the objective history for a given feature combination.

        Parameters
        ----------
        feature_key : tuple
            A hashable tuple representing the structure's features.
        generation : int
            The current generation index.
        current_obj : np.ndarray
            The objective vector for the structure.
        """
        if feature_key not in self._objectives_for_features_history:
            self._objectives_for_features_history[feature_key] = {
                "best_objective": current_obj.copy(),
            }
        record = self._objectives_for_features_history[feature_key]
        if self.detailed_record:
            if 'history' not in record:
                record['history'] = {}
            if generation not in record['history']:
                record['history'][generation] = []
            record['history'][generation].append(current_obj)
        prev_best = record["best_objective"]
        if np.any(current_obj < prev_best):
            record["best_objective"] = np.minimum(prev_best, current_obj)

    def check_convergence(self, generation, objectives, features, debug=False, information_novelty_has_improved:bool=False, generation_start=None, time_log=None):
        """
        Checks convergence based on objective improvements over consecutive generations.
        
        The rule is:
          "If for M (stall_threshold) consecutive generations, no structure has a strictly
           better (lower) objective for any previously seen combination of features, 
           the search is considered converged."
        
        Parameters
        ----------
        generation : int
            The current generation index.
        objectives : np.ndarray
            Array of objective values, either shape (n_structures,) or (n_structures, k).
        features : np.ndarray
            Array of feature values, either shape (n_structures,) or (n_structures, d).
        debug : bool, optional
            If True, enables additional logging.
        generation_start : float, optional
            The start time of the current generation (used to compute elapsed time).
        time_log : dict, optional
            A dictionary to log timing information.
        
        Returns
        -------
        dict
            A dictionary with the following keys:
                - 'converge': bool, True if convergence is reached.
                - 'improvement_found': bool, True if any improvement was detected in the current generation.
                - 'stall_count': int, the current count of consecutive generations without improvement.
        """
        if self.logger:
            self.logger.info("Checking stall-based convergence with feature-objective mapping...")

        # Ensure objectives and features are at least 1D arrays
        objectives_arr = np.atleast_1d(objectives)
        features_arr = np.atleast_1d(features)

        n_structures = objectives_arr.shape[0]
        if features_arr.shape[0] != n_structures:
            if self.logger:
                self.logger.warning("Mismatch in number of structures between objectives and features!")

        # Reshape arrays if necessary
        if objectives_arr.ndim == 1:
            objectives_arr = objectives_arr.reshape(-1, 1)
        if features_arr.ndim == 1:
            features_arr = features_arr.reshape(-1, 1)

        improvement_found = False

        for i in range(n_structures):
            feature_key = tuple(features_arr[i, :])
            current_obj = objectives_arr[i, :]
            if feature_key in self._objectives_for_features_history:
                prev_best = self._objectives_for_features_history[feature_key]["best_objective"]
                if np.any(current_obj < prev_best):
                    improvement_found = True
            else:
                improvement_found = True
            self._record_objective_for_feature(feature_key, generation, current_obj)


        # Update objective stall count
        self._no_improvement_count_objectives = (
            0 if improvement_found 
            else self._no_improvement_count_objectives + 1
        )
        self._no_improvement_count_objectives = min( self._no_improvement_count_objectives, self._stall_threshold )

        # If using information-driven convergence, update info stall count
        if self._information_driven:
            self._no_improvement_count_information = (
                0 if not information_novelty_has_improved
                else self._no_improvement_count_information + 1
            )
            self._no_improvement_count_information = min( self._no_improvement_count_information, self._stall_threshold )

        # Determine convergence
        conv_type = self._convergence_type.lower()
        if self._information_driven:
            # Pair counts for [objectives, information]
            counts = (
                self._no_improvement_count_objectives,
                self._no_improvement_count_information
            )
            # Map 'and' → all, 'or' → any; default to any if unrecognized
            op = {'and': all, 'or': any}.get(conv_type, any)
            converge = op(count >= self._stall_threshold for count in counts)
        else:
            converge = self._no_improvement_count_objectives >= self._stall_threshold
            counts = self._no_improvement_count_objectives
            
        self._no_improvement_count = np.min( counts ) 

        elapsed_time = time.time() - generation_start if generation_start else 0.0
        if time_log is not None:
            time_log['generation'] = elapsed_time

        if self.logger:
            if self._information_driven:
                self.logger.info(f"[Gen={generation}] improvement={improvement_found}, stall_count={self._no_improvement_count_objectives}/{self._stall_threshold} (obj) {self._no_improvement_count_information}/{self._stall_threshold} (info), converged={converge}, time={elapsed_time:.2f}s")
            else:
                self.logger.info(f"[Gen={generation}] improvement={improvement_found}, stall_count={self._no_improvement_count_objectives}/{self._stall_threshold}, converged={converge}, time={elapsed_time:.2f}s")

        return {
            'converge': converge,
            'improvement_found': improvement_found,
            'stall_count_objetive': self._no_improvement_count_objectives,
            'stall_count_information': self._no_improvement_count_information,
        }
