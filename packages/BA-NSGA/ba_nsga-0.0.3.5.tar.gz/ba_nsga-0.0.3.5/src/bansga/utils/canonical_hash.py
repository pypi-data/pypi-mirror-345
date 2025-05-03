import hashlib
import spglib
from scipy.spatial import KDTree, cKDTree
import copy 

def _serialize_kdtree_node(node):
    """
    Recursively serialize a KDTree node into a compact, deterministic string.
    Leaf–nodes expose .idx (an array of point‐indices).
    Inner–nodes expose .split_dim, .split, and pointers .less/.greater.
    """
    # Leaf?
    if hasattr(node, "idx"):
        # node.idx is a numpy array of indices
        idx_list = ",".join(map(str, node.idx.tolist()))
        return f"L[{idx_list}]"

    # Inner node
    # Always format the split coordinate to a fixed precision
    split_dim = node.split_dim
    split_val = f"{node.split:.8f}"
    left  = _serialize_kdtree_node(node.less)
    right = _serialize_kdtree_node(node.greater)
    return f"I{split_dim}:{split_val}({left})({right})"

def serialize_kdtree(tree):
    """
    Given either a KDTree or cKDTree, return a deterministic serialization
    of its splitting structure.
    """
    # If it's a cKDTree, rebuild as pure-Python KDTree
    if isinstance(tree, cKDTree):
        data     = tree.data
        leafsize = getattr(tree, "leafsize", None)
        # default leafsize=10 if not set
        tree = KDTree(data, leafsize=leafsize or 10)
    # Now walk the KDTree.tree
    return _serialize_kdtree_node(tree.tree)

class CanonicalHashMap:
    """
    A manager for storing canonical hashes of periodic crystal structures
    indexed by composition. This allows efficient duplicate detection
    among structures with the *same* composition.

    In practice, you create an instance of this class, and for each
    structure (with a known composition):
        1) Compute the canonical hash via spglib standardization
        2) Store or check if it has already been stored
    using the provided methods.

    Attributes
    ----------
    symprec : float
        Symmetry tolerance used by spglib for standardizing the cell.
    _hash_map : dict
        Internal dictionary: composition_key -> set of canonical hashes.

        Each 'composition_key' is derived from a dictionary of elements
        mapping to their integer amounts (e.g., {"Fe": 2, "Co": 1})
        turned into a string such as 'Co1-Fe2'.
    """

    def __init__(self, symprec: float = 1e-2, include_tree:bool=True, debug: bool = False):
        """
        Initialize the CompositionHashMap with a chosen symmetry precision.

        Parameters
        ----------
        symprec : float, optional (default=1e-2)
            Symmetry detection tolerance for spglib.standardize_cell(). 
            Larger values are more lenient; smaller values are stricter.
        """
        self.symprec = symprec
        self._hash_map = {}  # { 'comp_key': set([hash1, hash2, ...]) }
        self._include_tree = include_tree
        self.debug = debug
        
    @staticmethod
    def _composition_key(composition: dict) -> str:
        """
        Convert a composition dictionary (e.g., {"Fe":2, "Co":1})
        into a canonical string that can be used as a dictionary key.

        Sorting the items ensures that {"Co":1, "Fe":2} and {"Fe":2, "Co":1}
        produce the same key.

        Parameters
        ----------
        composition : dict
            Dictionary of element symbols (or IDs) mapped to integer stoichiometry.

        Returns
        -------
        str
            A canonical string representing the composition (e.g. "Co1-Fe2").
        """
        # Sort by element symbol to ensure a consistent order
        items_sorted = sorted(composition.items())  
        # Build a string like "Co1-Fe2" for the composition
        return "-".join(f"{elem}{amt}" for elem, amt in items_sorted)
 
    def _canonical_hash(self, container) -> str:
        """
        Compute a canonical SHA256 hash for the given periodic structure.

        This relies on spglib to standardize the crystal cell, making the
        resulting hash invariant under translations, rotations, and site
        ordering (within the tolerance 'symprec').

        The 'container' object must expose:
            container.AtomPositionManager.latticeVectors    # shape (3,3)
            container.AtomPositionManager.atomPositions_fractional  # shape (N,3)
            container.AtomPositionManager.get_atomic_numbers()       # length N

        Parameters
        ----------
        container : object
            A structure-like object which provides the necessary lattice/atom info.

        Returns
        -------
        str
            The canonical (SHA256) hash string for this structure.
        """
        # Extract lattice and atomic data (must match your container's API)
        container.AtomPositionManager.wrap()
        lattice_matrix = container.AtomPositionManager.latticeVectors
        frac_coords    = container.AtomPositionManager.atomPositions_fractional
        species_list   = container.AtomPositionManager.get_atomic_numbers()

        # Prepare data for spglib
        cell = (lattice_matrix, frac_coords, species_list)

        # -- Option A: Niggli reduction --
        # spglib modifies the array in-place, so make a copy if needed
        # The function returns lattice, positions, and species in a single
        # updated 'cell' variable
        #spglib.niggli_reduce(cell, eps=self.symprec)

        # After Niggli reduction, we still have to be sure the fractional coords
        # are wrapped in [0,1), so let's do that:
        #lattice, positions, species = cell
        #positions = positions % 1.0  # wrap back to 0-1

        # Alternatively:
        # -- Option B: standardize_cell --
        try:
            lattice, positions, species = spglib.standardize_cell(
                 cell,
                 to_primitive=False,   # produce the primitive cell
                 no_idealize=False,   # "idealize" can unify nearly-identical cells
                 symprec=self.symprec,
                 # angle_tolerance=0.5, # if needed
             )
        except:
            lattice, positions, species = lattice_matrix, frac_coords, species_list

        # Build a stable, sorted representation
        data_list = []
        for s, coord in zip(species, positions):
            # Sort or round to some precision
            data_list.append((
                s, 
                round(coord[0] / self.symprec) * self.symprec, 
                round(coord[1] / self.symprec) * self.symprec,
                round(coord[2] / self.symprec) * self.symprec 
            ))
        # Sort by (species, x, y, z)
        data_list.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

        # Flatten the lattice
        lat_str = ",".join(f"{val:.8f}" for row in lattice for val in row)
        # Flatten the sorted site data
        coords_str = ";".join(f"{site[0]}:{site[1]:.8f},{site[2]:.8f},{site[3]:.8f}" for site in data_list)

        # Final fingerprint
        fingerprint = lat_str + "|" + coords_str

        if self._include_tree:
            try:
                # Reset any old tree so that building will actually occur
                container.AtomPositionManager.kdtree = None

                # Attempt to build (or copy) the new tree
                tree = copy.copy(container.AtomPositionManager.kdtree)
                
                # Attempt serialization
                tree_repr = serialize_kdtree(tree)

            except Exception as exc:
                # Log the failure and use a sentinel value in the fingerprint
                logger.warning(f"KD-tree generation failed: {exc!r}")
                tree_repr = "ERROR"

            finally:
                # Always clear the manager’s kdtree so you don’t leave stale state
                container.AtomPositionManager.kdtree = None

            # Append either the real tree or the error‐marker
            fingerprint += f"|TREE:{tree_repr}"

        return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    def add_structure(self, container) -> bool:
        """
        Attempt to register the canonical hash of 'container' under the given composition.

        If the hash is already present, that implies this structure
        (under the same composition) is a duplicate.

        Parameters
        ----------
        container : object
            The structure to be hashed.

        Returns
        -------
        bool
            True if this is a newly added hash (i.e., not seen before),
            False if this exact structure hash was already registered 
            under the same composition.
        """
        # Build a canonical key for the composition
        comp_key = self._composition_key( container.AtomPositionManager.atomCountDict )
        # Compute the canonical hash
        hval = self._canonical_hash(container)

        # If no entry for this composition yet, create one
        if comp_key not in self._hash_map:
            self._hash_map[comp_key] = set()

        if not hasattr(container.AtomPositionManager, 'metadata'):
              container.AtomPositionManager.metadata = {}
        if not isinstance(container.AtomPositionManager.metadata, dict):
            container.AtomPositionManager.metadata = {}

        container.AtomPositionManager.metadata['hash'] = hval

        # Check if the hash is already known
        if hval in self._hash_map[comp_key]:
            # Duplicate for that composition
            return False
        else:
            # This is a new structure hash
            self._hash_map[comp_key].add(hval)
            return True

    def already_visited(self, container) -> bool:
        """
        Check whether 'container' (for the given composition) is already registered.

        This method *does not* add the structure if missing. It just tests duplication.

        Parameters
        ----------
        container : object
            The structure to be hashed.

        Returns
        -------
        bool
            True if the structure's hash is already known for this composition,
            False otherwise.
        """
        # Build the composition key
        comp_key = self._composition_key(container.AtomPositionManager.atomCountDict)
        # If composition not seen, it can't be visited
        if comp_key not in self._hash_map:
            return False

        # Compute hash
        hval = self._canonical_hash(container)
        # Return True if it exists in the set, else False
        return (hval in self._hash_map[comp_key])

    def get_num_structures_for_composition(self, composition: dict) -> int:
        """
        Retrieve how many *unique* structures have been registered under 'composition'.

        Parameters
        ----------
        composition : dict
            The composition to query, e.g. {"Fe":2, "Co":1}.

        Returns
        -------
        int
            The count of distinct structure hashes for that composition.
        """
        comp_key = self._composition_key(composition)
        if comp_key not in self._hash_map:
            return 0
        return len(self._hash_map[comp_key])

    def total_compositions(self) -> int:
        """
        Return how many distinct compositions are currently registered.

        Returns
        -------
        int
            The number of unique composition keys in this HashMap.
        """
        return len(self._hash_map)
