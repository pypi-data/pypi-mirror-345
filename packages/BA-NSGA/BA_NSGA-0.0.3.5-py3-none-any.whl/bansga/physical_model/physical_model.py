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
    """
    Runs a two-stage Langevin MD simulation (with two different calculators)
    followed by a final geometry optimization.

    Parameters
    ----------
    symbols : list
        Atomic symbols for the structure.
    positions : np.ndarray
        Atomic coordinates (Nx3).
    cell : np.ndarray
        Simulation cell vectors.
    calc1_path : str, optional
        Path to the first MACE model file, by default 'MACE_model.model'.
    calc2_path : str, optional
        Path to the second MACE model file, by default 'MACE_model2.model'.
    output_path : str, optional
        Name of the output trajectory file, by default 'MD_out.xyz'.
    nvt_steps_min : int
        Minimum number of NVT steps (for P = 0).
    nvt_steps_max : int
        Maximum number of NVT steps (for P = 1).
    fmax_min : float
        Minimum fmax value (for P = 0).
    fmax_max : float
        Maximum fmax value (for P = 1).
    debug : bool, optional
        Debug flag to skip MD calculations (default is False).
    debug : bool, optional
        If True, bypass actual calculations and return mock values, by default True.

    Returns
    -------
    tuple
        (positions, symbols, cell, final_energy) after MD and relaxation.
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
