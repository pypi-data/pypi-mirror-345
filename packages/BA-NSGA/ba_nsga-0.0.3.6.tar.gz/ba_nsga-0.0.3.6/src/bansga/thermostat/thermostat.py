from typing import Tuple, List, Optional
import numpy as np

from ..utils.helper_functions import (
    oscillation_factor,
    decay_factor,
)

class Thermostat:
    """
    The Thermostat class manages and updates a "temperature" parameter
    within a genetic algorithm (GA). It supports periodic oscillations,
    exponential decay, and adaptive adjustments based on performance metrics
    or consecutive failures. It also includes functionality to clamp the
    temperature within predefined bounds.

    Attributes
    ----------
    initial_temperature : float
        Base temperature used for initialization and resets.
    current_temperature : float
        The most recently computed temperature value.
    decay_rate : float
        Rate at which the temperature decays over generations.
    period : float
        Period for oscillatory temperature adjustments.
    increase_factor : float
        Scaling factor for temperature increases when performance is below a threshold.
    decrease_factor : float
        Scaling factor for temperature decreases when performance is above a threshold.
    threshold : float
        Performance threshold controlling whether to increase or decrease the temperature.
    temperature_bounds : tuple of float
        Lower and upper limits on the temperature (inclusive).
    consecutive_failures : int
        Tracks the number of consecutive failures, used to adapt the temperature.
    reset_count : int
        Tracks how many times the thermostat has been reset.
    """

    def __init__(
        self,
        initial_temperature: float,
        decay_rate: float = 0.01,
        period: float = 40.0,
        temperature_bounds: Tuple[float, float] = (0.0, 1.1),
        max_stall_offset:float=1.0,
        stall_growth_rate=0.05, 
        constant_temperature: bool = False, 
    ):
        """
        Initializes the Thermostat with default parameters for decay, oscillation,
        adaptive updates, and clamping.

        Parameters
        ----------
        initial_temperature : float
            The starting temperature of the system.
        decay_rate : float, optional
            Exponential decay rate applied to temperature over generations (default=0.01).
        period : float, optional
            Period for oscillatory adjustments (default=40.0).
        cooling_rate : float, optional
            Amount to subtract from the temperature if there are no failures (default=0.01).
        failure_increment : float, optional
            Base amount to add (per failure) to the temperature if there are consecutive 
            failures (default=0.05).
        temperature_bounds : Tuple[float, float], optional
            Lower and upper bounds for clamping the temperature (default=(0.0, 2.0)).
        """
        if temperature_bounds[0] > temperature_bounds[1]:
            raise ValueError("Lower bound of temperature cannot exceed upper bound.")

        self.initial_temperature = initial_temperature
        self.current_temperature = initial_temperature

        self.decay_rate = decay_rate
        self.period = period
        self.temperature_bounds = temperature_bounds

        self.consecutive_stall = 0
        self.reset_count = 0

        self.max_stall_offset = max_stall_offset
        self.stall_growth_rate = stall_growth_rate

        self.constant_temperature = constant_temperature

    def get_temperature(self, ) -> float:
        """
        """
        return self.current_temperature
        
    def actualizate_temperature(self, generation: int, stall:int = 0) -> float:
        """
        Computes and returns the temperature for a given generation, taking into
        account exponential decay and periodic oscillations (via helper functions),
        while also applying any adaptive offsets (e.g., from consecutive failures).

        Parameters
        ----------
        generation : int
            The current generation of the GA.

        Returns
        -------
        float
            The newly computed temperature for this generation.
        """
        # Example: first compute a base decay, then an oscillation, 
        # then optionally combine with some other factors.

        # If “constant” mode is on, skip all update logic:
        if self.constant_temperature:
            return self.current_temperature

        decay_temperature_factor = decay_factor(
            decay_rate=self.decay_rate,
            generation=generation
        )
        oscillation_temperature_factor = oscillation_factor(
            period=self.period,
            generation=generation
        )

        max_cycles = int(1.0 / self.stall_growth_rate)  
        if stall > 0:
            self.consecutive_stall += 1
            if self.consecutive_stall > 2 * max_cycles:
                self.consecutive_stall = 2 * max_cycles
        else:
            if self.consecutive_stall > max_cycles/2:
                self.consecutive_stall = max(
                   0, self.consecutive_stall - max_cycles
                )
            self.consecutive_stall -= 1

        #self.consecutive_stall += 1 if stall > 0 else -1
        #self.consecutive_stall = max(0, min( float(1.0)/float(self.stall_growth_rate) , self.consecutive_stall))

        # Combine them (this is just an example, adapt to your actual logic).
        # E.g., if combined_rate is your function to merge these two values:
        new_temp = decay_temperature_factor * oscillation_temperature_factor + self.stall_coefficient() 

        # Update current_temperature and clamp it
        self.current_temperature = new_temp
        self.clamp_temperature()

        return self.current_temperature

    def stall_coefficient(self, function: str = '') -> float:
        """
        Computes a small additive offset that increases with the number of consecutive stalls.
        The function is designed to saturate such that the maximum contribution is bounded
        by self.max_stall_offset.

        Parameters
        ----------
        self.consecutive_stall : int
            The number of consecutive stalls (failures).

        Returns
        -------
        float
            A stall coefficient that grows with 'stall' but is limited to a maximum value.
        """
        # Use an exponential saturation function.
        full_cycle = int(2.0 / self.stall_growth_rate)  
        phase = self.consecutive_stall % full_cycle
        half_cycle = full_cycle // 2

        if phase <= half_cycle:
            coef = self.max_stall_offset * (phase / half_cycle)
        else:
            coef = self.max_stall_offset * (1 - ((phase - half_cycle) / half_cycle))

        return coef
        #return self.max_stall_offset * (1 - np.exp(-self.stall_growth_rate * self.consecutive_stall))

    def clamp_temperature(self):
        """
        Ensures the current temperature remains within the predefined bounds.
        If it falls outside, it is clamped to the min or max limit.
        """
        lower, upper = self.temperature_bounds
        if self.current_temperature < lower:
            self.current_temperature = lower
        elif self.current_temperature > upper:
            self.current_temperature = upper

    def force_max_temperature(self) -> float:
        """
        Forces the temperature to the maximum allowed bound, useful if the GA
        is stuck and an aggressive exploration phase is needed.

        Returns
        -------
        float
            The temperature after forcing it to the upper bound.
        """
        _, upper = self.temperature_bounds
        self.current_temperature = upper
        return self.current_temperature

    def force_min_temperature(self) -> float:
        """
        Forces the temperature to the minimum allowed bound, useful if 
        the system is moving too randomly and needs to be reined in.

        Returns
        -------
        float
            The temperature after forcing it to the lower bound.
        """
        lower, _ = self.temperature_bounds
        self.current_temperature = lower
        return self.current_temperature

    def reset(self):
        """
        Resets the current temperature and consecutive failure count to the
        initial conditions. Additionally, increments an internal counter that
        tracks how many resets have been performed.
        """
        self.current_temperature = self.initial_temperature
        self.consecutive_stall = 0
        self.reset_count += 1

    def evaluate_temperature_over_generations(self, max_generations: int=1000) -> List[float]:
        """
        Predicts how the temperature would evolve over a specified number
        of generations. This is useful for plotting or debugging to see how
        oscillation and decay would behave in isolation (i.e., ignoring real-time
        performance-based updates).

        Parameters
        ----------
        max_generations : int
            Number of generations to simulate.

        Returns
        -------
        List[float]
            A list of temperature values for each generation from 0 to max_generations-1.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import random

        generations_array = np.arange(1, max_generations, 1)
        temperature_array = np.array([ self.actualizate_temperature(g, random.choice([1, 0,0,0,0])  ) for g in generations_array], dtype=np.float64)
        
        temperature_array = []
        for g in generations_array:
            if g < 50:
                temperature_array.append( self.actualizate_temperature(g, random.choice([1, 0,0,0,0])) )
            else:
                temperature_array.append( self.actualizate_temperature(g, random.choice([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0])) )
        temperature_array = np.array(temperature_array)

        plt.plot( generations_array, temperature_array )
        plt.show()

        return generations_array, temperature_array

    def record_temperature_evolution(
        self, 
        generations: int, 
        performance_metrics: Optional[List[float]] = None
    ) -> List[float]:
        """
        Records the evolution of the temperature over the specified number of generations,
        optionally factoring in a list of performance metrics for each generation
        (thus simulating more realistic adaptive behavior).

        Parameters
        ----------
        generations : int
            How many generations to simulate.
        performance_metrics : list of float, optional
            Performance metrics to consider each generation. If None or shorter than
            `generations`, the thermostat will assume a neutral performance metric.

        Returns
        -------
        List[float]
            The sequence of temperature values for each generation.
        """
        temp_evolution = []
        for gen in range(generations):
            # 1) Get baseline temperature from decay + oscillation
            baseline_temp = self.get_temperature(generation=gen)
            # 2) If a performance metric is provided, adapt accordingly
            if performance_metrics is not None and gen < len(performance_metrics):
                self.update_by_performance(performance_metrics[gen])

            temp_evolution.append(self.current_temperature)

        return temp_evolution
