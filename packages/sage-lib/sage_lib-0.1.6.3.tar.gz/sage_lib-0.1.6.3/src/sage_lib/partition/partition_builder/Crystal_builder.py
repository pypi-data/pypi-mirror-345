try:
    import numpy as np
    from .BasePartition import BasePartition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class Crystal_builder(BasePartition):
    """
    A class for generating crystalline structures.

    This class provides methods to generate various types of crystal cells,
    including but not limited to cubic, face-centered cubic (FCC), body-centered
    cubic (BCC), tetragonal, body-centered tetragonal (BCT), orthorhombic,
    hexagonal, rhombohedral, monoclinic, triclinic as well as 2D lattices such as
    square, rectangular, oblique, and hexagonal (2D). The lattice vectors and atomic
    positions are computed based on the selected lattice type and provided parameters.
    The resulting structure is used to populate the AtomPositionManager attributes
    within a container.

    Attributes
    ----------
    lattice_type : str
        Identifier for the crystal lattice type (e.g. 'cubic', 'fcc', 'bcc',
        'tetragonal', 'bct', 'orthorhombic', 'hexagonal', 'rhombohedral',
        'monoclinic', 'triclinic', 'square2d', 'rectangular2d', 'oblique2d', 'hexagonal2d').
    lattice_parameters : dict
        Dictionary holding the parameters specific to the chosen lattice type.
    atom_positions : numpy.ndarray
        Array containing the atomic positions within the unit cell.
    lattice_vectors : numpy.ndarray
        3x3 array representing the lattice vectors.
    atom_labels : list
        List of atom labels for each atom in the structure.
    atom_count : int
        Total number of atoms in the unit cell.
    pbc : list
        Periodic boundary conditions in each direction (typically [True, True, True]).

    Methods
    -------
    set_lattice_type(lattice_type: str, **params)
        Set the lattice type and its required parameters.
    generate_lattice_vectors()
        Compute the lattice vectors based on the chosen lattice type.
    generate_atom_positions(atom_label: str = 'H')
        Generate the atomic positions for the cell.
    build_crystal(lattice_type: str, lattice_parameters: dict)
        Build the complete crystal structure and populate the AtomPositionManager.
    """

    def __init__(self, *args, **kwargs):
        """
        """

        # Initialize lattice-related attributes with default values
        self.lattice_type = None
        self.lattice_parameters = {}
        self.atom_positions = None
        self.lattice_vectors = None
        self.atom_labels = []
        self.atom_count = 0
        self.pbc = [True, True, True]

        super().__init__(*args, **kwargs)
    
    def set_lattice_type(self, lattice_type: str, **params):
        """
        Set the lattice type and its associated parameters.

        Parameters
        ----------
        lattice_type : str
            Identifier for the crystal lattice type. Supported types include:
            'cubic', 'fcc', 'bcc', 'tetragonal'.
        **params
            Lattice-specific parameters. For example, for a cubic lattice provide 'a',
            for a tetragonal cell provide 'a' and 'c', etc.
        """
        self.lattice_type = lattice_type.lower()
        self.lattice_parameters = params

    def generate_lattice_vectors(self):
        """
        Compute lattice vectors based on the selected lattice type and parameters.

        Returns
        -------
        numpy.ndarray
            A 3x3 array containing the lattice vectors.

        Raises
        ------
        ValueError
            If the lattice type is not set or required parameters are missing.
        """
        if self.lattice_type is None:
            raise ValueError("Lattice type not set. Use set_lattice_type() first.")

        lp = self.lattice_parameters  # shorthand
        # 3D lattices
        if self.lattice_type == 'cubic':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for cubic lattice.")
            self.lattice_vectors = a * np.eye(3)

        elif self.lattice_type == 'fcc':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for FCC lattice.")
            self.lattice_vectors = 0.5 * np.array([[0, a, a],
                                                    [a, 0, a],
                                                    [a, a, 0]])

        elif self.lattice_type == 'bcc':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for BCC lattice.")
            self.lattice_vectors = 0.5 * np.array([[-a, a, a],
                                                    [a, -a, a],
                                                    [a, a, -a]])

        elif self.lattice_type == 'tetragonal':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for tetragonal lattice.")
            self.lattice_vectors = np.diag([a, a, c])

        elif self.lattice_type == 'bct':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for body-centered tetragonal lattice.")
            # Primitive cell for body-centered tetragonal (analogous to BCC with tetragonal distortion)
            self.lattice_vectors = 0.5 * np.array([[ a,  a,  c],
                                                    [-a,  a,  c],
                                                    [ a, -a,  c]])

        elif self.lattice_type == 'orthorhombic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', and 'c' must be provided for orthorhombic lattice.")
            self.lattice_vectors = np.diag([a, b, c])

        elif self.lattice_type == 'hexagonal':
            try:
                a = float(lp['a'])
                c = float(lp['c'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'c' must be provided for hexagonal lattice.")
            self.lattice_vectors = np.array([[ a,        0, 0],
                                             [-a/2, a*np.sqrt(3)/2, 0],
                                             [ 0,        0, c]])

        elif self.lattice_type == 'rhombohedral':
            try:
                a = float(lp['a'])
                alpha = float(lp['alpha'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'alpha' must be provided for rhombohedral lattice.")
            alpha_rad = np.deg2rad(alpha)
            v1 = np.array([a, 0, 0])
            v2 = np.array([a * np.cos(alpha_rad), a * np.sin(alpha_rad), 0])
            # A common representation for a rhombohedral cell:
            # v3 is defined so that the angle between any two vectors equals alpha.
            v3_x = a * np.cos(alpha_rad)
            # Using an equivalent formulation: v3_y = a*(1 - cos(alpha))/tan(alpha)
            v3_y = a * (1 - np.cos(alpha_rad)) / np.tan(alpha_rad) if np.tan(alpha_rad) != 0 else 0
            v3_z = a * np.sqrt(1 - 3*np.cos(alpha_rad)**2 + 2*np.cos(alpha_rad)**3)
            v3 = np.array([v3_x, v3_y, v3_z])
            self.lattice_vectors = np.array([v1, v2, v3])

        elif self.lattice_type == 'monoclinic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
                beta = float(lp['beta'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', 'c', and 'beta' must be provided for monoclinic lattice.")
            beta_rad = np.deg2rad(beta)
            v1 = np.array([a, 0, 0])
            v2 = np.array([0, b, 0])
            v3 = np.array([c * np.cos(beta_rad), 0, c * np.sin(beta_rad)])
            self.lattice_vectors = np.array([v1, v2, v3])

        elif self.lattice_type == 'triclinic':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                c = float(lp['c'])
                alpha = float(lp['alpha'])
                beta  = float(lp['beta'])
                gamma = float(lp['gamma'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', 'c', 'alpha', 'beta', and 'gamma' must be provided for triclinic lattice.")
            alpha_rad = np.deg2rad(alpha)
            beta_rad  = np.deg2rad(beta)
            gamma_rad = np.deg2rad(gamma)
            v1 = np.array([a, 0, 0])
            v2 = np.array([b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0])
            v3_x = c * np.cos(beta_rad)
            v3_y = c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad)
            term = 1 - np.cos(beta_rad)**2 - ((np.cos(alpha_rad) - np.cos(beta_rad)*np.cos(gamma_rad)) / np.sin(gamma_rad))**2
            if term < 0:
                term = 0
            v3_z = c * np.sqrt(term)
            v3 = np.array([v3_x, v3_y, v3_z])
            self.lattice_vectors = np.array([v1, v2, v3])

        # 2D lattices (assume the third row is zero)
        elif self.lattice_type == 'square2d':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for square2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [0, a, 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'rectangular2d':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
            except KeyError:
                raise ValueError("Parameters 'a' and 'b' must be provided for rectangular2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [0, b, 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'oblique2d':
            try:
                a = float(lp['a'])
                b = float(lp['b'])
                gamma = float(lp['gamma'])
            except KeyError:
                raise ValueError("Parameters 'a', 'b', and 'gamma' must be provided for oblique2d lattice.")
            gamma_rad = np.deg2rad(gamma)
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0],
                                             [0, 0, 0]])
        elif self.lattice_type == 'hexagonal2d':
            try:
                a = float(lp['a'])
            except KeyError:
                raise ValueError("Parameter 'a' must be provided for hexagonal2d lattice.")
            self.lattice_vectors = np.array([[a, 0, 0],
                                             [a/2, a*np.sqrt(3)/2, 0],
                                             [0, 0, 0]])
        else:
            raise ValueError(f"Lattice type '{self.lattice_type}' not supported.")

        return self.lattice_vectors

    def generate_atom_positions(self, atom_label: str = 'H'):
        """
        Generate atomic positions for the unit cell based on the lattice type.

        Returns
        -------
        numpy.ndarray
            An array of atomic positions.

        Notes
        -----
        For primitive cells a single atom is placed at the origin. For lattices with a basis,
        such as FCC, BCC, and BCT, multiple atomic positions are provided. In 2D systems the z-coordinate
        is set to zero.
        """
        if self.lattice_type is None:
            raise ValueError("Lattice type not set. Use set_lattice_type() first.")

        # Ensure lattice vectors are generated
        if self.lattice_vectors is None:
            self.generate_lattice_vectors()

        lt = self.lattice_type
        if lt in ['cubic', 'tetragonal', 'orthorhombic', 'hexagonal', 
                  'rhombohedral', 'monoclinic', 'triclinic', ]:
            self.atom_positions = np.dot(np.array([[0.0, 0.0, 0.0]]), self.lattice_vectors)
            self.atom_labels = [atom_label]
            self.atom_count = 1

        elif lt == 'fcc':
            self.atom_positions = np.dot(np.array([[0.0, 0.0, 0.0]]), self.lattice_vectors)
            self.atom_labels = [atom_label] 
            self.atom_count = 1

        elif lt == 'bcc':
            self.atom_positions = np.dot(np.array([[0.0, 0.0, 0.0]]), self.lattice_vectors)
            self.atom_labels = [atom_label] * 1
            self.atom_count = 1

        elif lt == 'bct':
            # Similar to BCC but with tetragonal distortion
            self.atom_positions = np.dot(np.array([[0.0, 0.0, 0.0]]), self.lattice_vectors)
            self.atom_labels = [atom_label] * 1
            self.atom_count = 1

        # 2D lattices: one atom at the origin (z=0)
        elif lt in ['square2d', 'rectangular2d', 'oblique2d', 'hexagonal2d']:
            self.atom_positions = np.dot(np.array([[0.0, 0.0, 0.0]]), self.lattice_vectors)
            self.atom_labels = [atom_label]
            self.atom_count = 1

        else:
            raise ValueError(f"Atom positions generation for lattice type '{lt}' is not implemented.")

        return self.atom_positions

    def build_crystal(self, lattice_type:str='fcc', lattice_parameters:dict={'a':1}, atom_label:str='H'):
        """
        Build the crystal structure and populate the AtomPositionManager attributes.

        This method calculates the lattice vectors and atomic positions using the
        specified lattice type and parameters. The generated structure data can then
        be assigned to the container's AtomPositionManager.

        Returns
        -------
        dict
            A dictionary with keys:
            - 'atomCount': number of atoms in the cell.
            - 'atomPositions': numpy array of atomic positions.
            - 'atomLabelsList': list of atomic labels.
            - 'latticeVectors': 3x3 array of lattice vectors.
            - 'pbc': periodic boundary conditions list.
        
        Example
        -------
        >>> container = SingleRun('')
        >>> cpb = Crystal_builder()
        >>> cpb.set_lattice_type('fcc', a=4.0)
        >>> structure = cpb.build_crystal()
        >>> container.AtomPositionManager.atomCount = structure['atomCount']
        >>> container.AtomPositionManager.atomPositions = structure['atomPositions']
        >>> container.AtomPositionManager.atomLabelsList = structure['atomLabelsList']
        >>> container.AtomPositionManager.latticeVectors = structure['latticeVectors']
        >>> container.AtomPositionManager.pbc = structure['pbc']
        >>> self.add_container(container)
        """

        container = self.add_empty_container()

        self.set_lattice_type(lattice_type, 
            a=lattice_parameters.get('a', 0), 
            b=lattice_parameters.get('b', 0), 
            c=lattice_parameters.get('c', 0),
            alpha=lattice_parameters.get('alpha', 0),
            beta=lattice_parameters.get('beta', 0),
            gamma=lattice_parameters.get('gamma', 0) )

        self.generate_lattice_vectors()
        self.generate_atom_positions(atom_label=atom_label)

        structure_data = {
            'atomCount': self.atom_count,
            'atomPositions': self.atom_positions,
            'atomLabelsList': self.atom_labels,
            'latticeVectors': self.lattice_vectors,
            'pbc': self.pbc
        }   

        container.AtomPositionManager.set_latticeVectors( structure_data['latticeVectors'] )
        container.AtomPositionManager.add_atom(structure_data['atomLabelsList'], structure_data['atomPositions'])
        self.add_container(container)

        return container
