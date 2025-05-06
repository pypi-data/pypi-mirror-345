from sage_lib.partition.Partition import Partition
import numpy as np
from tqdm import tqdm

def mace_calculator(
        calc_path:str='MACE_model.model',
        output_path:str='MD_out.xyz',
        nvt_steps_min: int = 1000, 
        nvt_steps_max: int = 5000, 
        fmax_min: float = 0.03, 
        fmax_max: float = 0.50,
        device: str = 'cuda',
        default_dtype: str = 'float32',
        T:float = 900,
        debug=False
    ):
    r"""
    Create and return a two‐stage Langevin MD + final relaxation routine using a MACE model.

    This factory returns a function `run(symbols, positions, cell, sampling_temperature)`
    which performs:

    1. **Stage I – NVT Langevin dynamics**  
       A constant‐friction Langevin integrator at gradually ramped temperature  
       .. math::
          m_i \\frac{d^2 \\mathbf{r}_i}{dt^2} = -\\nabla_i V(\\{\\mathbf{r}\\}) - \\gamma m_i \\frac{d\\mathbf{r}_i}{dt}
            + \\sqrt{2 m_i \\gamma k_B T(t)}\\;\\boldsymbol{\\xi}_i(t),
       where:
       - \\(T(t)\\) is the thermostat schedule (here constant at \\(T\\) K),  
       - \\(\\gamma=0.01\\) fs⁻¹ is the friction coefficient,  
       - \\(k_B\\) is Boltzmann’s constant,  
       - \\(\\boldsymbol{\\xi}_i(t)\\) is unit‐variance Gaussian noise.  
       The number of steps  
       .. math::
          N_{\\rm MD} = N_{\\min} + P\\,(N_{\\max}-N_{\\min}),
       with  
       \\[
         P = \\texttt{sampling\_temperature} \\in [0,1],
         \\quad N_{\\min} = \\texttt{nvt\_steps\_min}, 
         \\quad N_{\\max} = \\texttt{nvt\_steps\_max}.
       \\]

    2. **Stage II – Geometry optimization**  
       Conjugate‐gradient / FIRE relaxation to force tolerance  
       .. math::
          f_{\\max} = f_{\\min} + P\\,(f_{\\max}^{\\rm tol}-f_{\\min}),  
       where \\(f_{\\min}\\), \\(f_{\\max}^{\\rm tol}\\) are inputs.

    3. **I/O**  
       - Trajectory and final frame written to `output_path` in XYZ format.  
       - Returns updated `(positions, symbols, cell, final_energy)`.

    **Parameters**
    ----------
    calc_path : str, optional
        Path to the trained MACE model file.
    output_path : str, optional
        File path to write the final structure (`.xyz`).
    nvt_steps_min : int
        Minimum NVT steps when `sampling_temperature=0`.
    nvt_steps_max : int
        Maximum NVT steps when `sampling_temperature=1`.
    fmax_min : float
        Minimum force‐convergence threshold (eV/Å) when `sampling_temperature=0`.
    fmax_max : float
        Maximum force‐convergence threshold when `sampling_temperature=1`.
    device : str, optional
        Device for MACE (`'cpu'` or `'cuda'`).
    default_dtype : str, optional
        Floating‐point precision for MACE predictions.
    T : float, optional
        Target temperature (K) for the Langevin thermostat.
    debug : bool, optional
        If True, skip MD and return mock results immediately.

    **Returns**
    -------
    function
        A function with signature  
        ```python
        run(symbols, positions, cell, sampling_temperature) -> (pos, sym, cell, energy)
        ```
        which executes the two‐stage MD and relaxation as described.

    **Raises**
    ------
    RuntimeError
        If the MACE model cannot be loaded or MD/optimization fails irrecoverably.
    """
    from mace.calculators.mace import MACECalculator
    import ase.io
    from ase import Atoms, units
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.optimize import BFGS, FIRE
    from ase.optimize.precon.fire import PreconFIRE
    from ase.optimize.precon import Exp

    from ase.units import fs
    from ase.constraints import FixAtoms
    import time

    calc = MACECalculator(model_paths=calc_path, device=device, default_dtype=default_dtype)

    def run(
        symbols:np.array, 
        positions:np.array, 
        cell:np.array,
        sampling_temperature:float=0.0,
        ):
        """
        """
        def printenergy(dyn, start_time=None):
            """
            Prints potential, kinetic, and total energy for the current MD step.

            Parameters
            ----------
            dyn : ase.md.md.MDLogger
                The MD dynamics object.
            start_time : float, optional
                Start time for elapsed-time measurement, by default None.
            """
            a = dyn.atoms
            epot = a.get_potential_energy() / len(a)
            ekin = a.get_kinetic_energy() / len(a)
            elapsed_time = 0 if start_time is None else time.time() - start_time
            temperature = ekin / (1.5 * units.kB)
            total_energy = epot + ekin
            print(
                f"{elapsed_time:.1f}s: Energy/atom: Epot={epot:.3f} eV, "
                f"Ekin={ekin:.3f} eV (T={temperature:.0f}K), "
                f"Etot={total_energy:.3f} eV, t={dyn.get_time()/units.fs:.1f} fs, "
                f"Eerr={a.calc.results.get('energy', 0):.3f} eV, "
                f"Ferr={np.max(np.linalg.norm(a.calc.results.get('forces', np.zeros_like(a.get_forces())), axis=1)):.3f} eV/Å",
                flush=True,
            )

        def temperature_ramp(initial_temp, final_temp, total_steps):
            """
            Generates a linear temperature ramp function.

            Parameters
            ----------
            initial_temp : float
                Starting temperature (K).
            final_temp : float
                Ending temperature (K).
            total_steps : int
                Number of MD steps over which to ramp.

            Returns
            -------
            function
                A function ramp(step) -> temperature at the given MD step.
            """
            def ramp(step):
                return initial_temp + (final_temp - initial_temp) * (float(step) / total_steps)
            return ramp

        if debug:
            # Skip actual MD
            print(f"DEBUG mode: skipping MD calculations. Returning input positions.")
            return positions, symbols, cell, -2000.0

        # Atoms objects:
        atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
        fix_index = [atom.index for atom in atoms if atom.position[2] < 4.0]
        atoms.set_constraint(FixAtoms(indices=fix_index))
        atoms.calc = calc

        if nvt_steps_max > 0:
            # Stage 1: NVT with first model
            nvt_steps = int(nvt_steps_min + sampling_temperature * (nvt_steps_max - nvt_steps_min))
            temp_ramp = temperature_ramp(T, T, nvt_steps)
            MaxwellBoltzmannDistribution(atoms, temperature_K=temp_ramp(0))

            dyn = Langevin(
                atoms=atoms,
                timestep=1 * fs,
                temperature_K=temp_ramp(0),
                friction=0.01
            )
            #dyn.attach(lambda d=dyn: d.set_temperature(temp_ramp(d.nsteps)), interval=10)
            dyn.attach(printenergy, interval=5000, dyn=dyn, start_time=time.time())
            dyn.run(nvt_steps)

        # Stage 2: OPT
        fmax = fmax_min + sampling_temperature * (fmax_max - fmax_min)
        relax = FIRE(atoms,logfile=None)
        relax.run(fmax=fmax, steps=200)

        #precon = Exp(A=1)
        #relax = PreconFIRE(atoms, precon=precon,)# logfile=None)
        #relax.run(fmax=fmax, steps=200)

        ase.io.write(output_path, atoms)

        return np.array(atoms.get_positions()), np.array(atoms.get_chemical_symbols()), np.array(atoms.get_cell()), float(atoms.get_potential_energy())

    return run

def physical_model(structures, physical_model_func, temperature: float=1.0, logger:object=None, debug:bool=False):
    """
    Runs molecular dynamics simulations on the provided structures.

    Parameters
    ----------
    structures : list
        List of structure objects to be simulated.
    physical_model_func : function
        The function used to run the MD simulation on a single structure.
    temperature : float, optional
        Simulation temperature, by default 1.0.
    logger : object, optional
        Logger for recording progress information, by default None.
    debug : bool, optional
        If True, bypasses actual calculations and uses mock values, by default False.

    Returns
    -------
    Partition
        An instance of Partition that contains the updated structures.
    """
    logger.info(f"Starting MD simulations on structures ({len(structures)}). T = {temperature}")

    partitions_physical_model = Partition()
    partitions_physical_model.containers = structures

    for idx, structure in enumerate(tqdm(partitions_physical_model.containers, desc="Processing Structures")):

        structure.AtomPositionManager.charge = None
        structure.AtomPositionManager.magnetization = None
        
        if not  debug:
            # Run MD simulation
            positions, symbols, cell, energy = physical_model_func(
                symbols=structure.AtomPositionManager.atomLabelsList,
                positions=structure.AtomPositionManager.atomPositions,
                cell=structure.AtomPositionManager.latticeVectors,
                sampling_temperature = temperature,
            )
        else: 

            positions = structure.AtomPositionManager.atomPositions 
            symbols = structure.AtomPositionManager.atomLabelsList
            cell = structure.AtomPositionManager.latticeVectors
            energy = -657.2 + np.random.rand()*6

        structure.AtomPositionManager.atomPositions = positions
        structure.AtomPositionManager.atomLabelsList = symbols
        structure.AtomPositionManager.latticeVectors = cell
        structure.AtomPositionManager.E = energy

    logger.info(f"MD simulations completed. {len(partitions_physical_model.containers)} Structures processed.") 
    return partitions_physical_model

def EMT(positions, symbols, cell):
    r"""
    Perform a quick EMT relaxation and return updated atomic data.

    1. **Initialize Atoms:**  
       \\(\\mathrm{Atoms}(symbols, positions, cell, pbc=True)\\)

    2. **Maxwell–Boltzmann velocities:**  
       Sample initial velocities at 400 K  
       via  
       .. math::
         \tfrac12 m_i \langle v_i^2 \\rangle = \tfrac32 k_B T.

    3. **Minimization:**  
       Use BFGS to minimize forces to  
       .. math::
         \\max_i |F_i| < 0.05\\,\\mathrm{eV/Å}.

    **Parameters**
    ----------
    positions : ndarray, shape (N,3)
        Initial atomic positions.
    symbols : list of str
        Atomic symbols.
    cell : ndarray, shape (3,3)
        Lattice vectors.

    **Returns**
    -------
    tuple
        `(new_positions, new_symbols, new_cell, energy)`.
    """

    from ase.calculators.emt import EMT
    from ase import Atoms, units
    from ase.md.langevin import Langevin
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.optimize import BFGS

    atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
    MaxwellBoltzmannDistribution(atoms, temperature_K=400)

    atoms.calc = EMT()
    print('Relaxing starting candidate')
    dyn = BFGS(atoms, trajectory=None, logfile=None)
    dyn.run(fmax=0.05, steps=100)
    #atoms.info['key_value_pairs']['raw_score'] = -a.get_potential_energy()

    return atoms.get_positions(), atoms.get_chemical_symbols(), atoms.get_cell(), atoms.get_potential_energy()
