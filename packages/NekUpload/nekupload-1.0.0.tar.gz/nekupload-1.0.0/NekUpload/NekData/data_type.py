from enum import Enum,auto

class BasisType(Enum):
    """Enum denoting what basis type is used in the construction of spectral elements in Nektar++.
    As defined in Nektar/library/LibUtilities/Foundations/BasisType.h
    """
    #Must be defined exactly as I/O files use integer values to reference these points
    NO_BASIS_TYPE = 1
    ORTHO_A = 2     # Principle Orthogonal Functions
                    # \f$\widetilde{\psi}^a_p(z_i)\f$
    ORTHO_B = 3     # Principle Orthogonal Functions
                    # \f$\widetilde{\psi}^b_{pq}(z_i)\f$
    ORTHO_C = 4     # Principle Orthogonal Functions
                    # \f$\widetilde{\psi}^c_{pqr}(z_i)\f$
    MODIFIED_A = 5  # Principle Modified Functions \f$ \phi^a_p(z_i) \f$
    MODIFIED_B = 6  # Principle Modified Functions \f$ \phi^b_{pq}(z_i) \f$
    MODIFIED_C = 7  # Principle Modified Functions \f$ \phi^c_{pqr}(z_i) \f$
    ORTHO_PYR_C = 8 # Principle Orthogonal Functions
                    # \f$\widetilde{\psi}^c_{pqr}(z_i) for Pyramids\f$
    MODIFIED_PYR_C = 9# Principle Modified Functions \f$ \phi^c_{pqr}(z_i) for
                    # Pyramids\f$
    FOURIER = 10    # Fourier Expansion \f$ \exp(i p\pi  z_i)\f$
    GLL_LAGRANGE = 11# Lagrange for SEM basis \f$ h_p(z_i) \f$
    GAUSS_LAGRANGE = 12# //!< Lagrange Polynomials using the Gauss points \f$
                    #!< h_p(z_i) \f$
    LEGENDRE = 13   # Legendre Polynomials \f$ L_p(z_i) = P^{0,0}_p(z_i)\f$. Same
                    # as Ortho_A
    CHEBYSHEV = 14  # Chebyshev Polynomials \f$ T_p(z_i) =
                    # P^{-1/2,-1/2}_p(z_i)\f$
    MONONMIAL = 15  # Monomial polynomials \f$ L_p(z_i) = z_i^{p}\f$
    FOURIER_SINGLE_MODE = 16    # Fourier ModifiedExpansion with just the first mode
                                #\f$ \exp(i \pi  z_i)\f$
    FOURIER_HALF_MODE_RE = 17  #//!< Fourier Modified expansions with just the real part
                                #//!< of the first mode  \f$ Re[\exp(i \pi  z_i)]\f$
    FOURIER_HALF_MODE_IM = 18  #//!< Fourier Modified expansions with just the imaginary
                                #//!< part of the first mode  \f$ Im[\exp(i \pi  z_i)]\f$
    SIZE_BASIS_TYPE = 19        #//!< Length of enum list    

class Elements(Enum):
    """Enum denoting element shape and type.
    """
    VERT = 1
    CURVE_NODE = 2
    SEG = 3
    CURVE_EDGE = 4
    TRI = 5
    QUAD = 6
    CURVE_FACE = 7
    HEX = 8
    PRISM = 9
    PYR = 10
    TET = 11
    COMPOSITE = 12
    DOMAIN = 13
    EDGE = 14
    FACE = 15

class ExpansionType(Enum):
    """Enum used for defining the expansion type of a spectral element in Nektar++.
    Same enums as defined in nektar/library/LibUtilities/Foundations/MeshGraph.h
    """
    #Must be defined exactly as I/O files use integer values to reference these points
    NO_EXPANSION_TYPE = 1           # No expansion type
    MODIFIED = 2                    # Modified expansion
    MODIFIED_QUAD_PLUS_1 = 3        # Modified quad plus 1
    MODIFIED_QUAD_PLUS_2 = 4        # Modified quad plus 2
    MODIFIED_GLL_RADAU_10 = 5       # Modified GLL Radau 10
    ORTHOGONAL = 6                  # Orthogonal expansion
    GLL_LAGRANGE = 7                # GLL Lagrange expansion
    GLL_LAGRANGE_SEM = 8            # GLL Lagrange SEM expansion
    GAUSS_LAGRANGE = 9              # Gauss Lagrange expansion
    GAUSS_LAGRANGE_SEM = 10         # Gauss Lagrange SEM expansion
    FOURIER = 11                    # Fourier expansion
    FOURIER_SINGLE_MODE = 12        # Fourier single mode expansion
    FOURIER_HALF_MODE_RE = 13       # Fourier half mode (real) expansion
    FOURIER_HALF_MODE_IM = 14       # Fourier half mode (imaginary) expansion
    CHEBYSHEV = 15                  # Chebyshev expansion
    FOURIER_CHEBYSHEV = 16          # Fourier-Chebyshev expansion
    CHEBYSHEV_FOURIER = 17          # Chebyshev-Fourier expansion
    FOURIER_MODIFIED = 18           # Fourier modified expansion
    EXPANSION_TYPE_SIZE = 19        # Size of the expansion type list

class IntegrationPoint(Enum):
    """Enum describing what integration/quadrature points are used for evaluation in spectral elements in Nektar++.
    Same enums as defined in nektar/library/LibUtilities/Foundations/PointsType.h
    """
    #Must be defined exactly as I/O files use integer values to reference these points
    GAUSS_GAUSS_LEGENDRE = 1                # 1D Gauss-Gauss-Legendre quadrature points
    GAUSS_RADAU_M_LEGENDRE = 2             # 1D Gauss-Radau-Legendre quadrature points, pinned at x=-1
    GAUSS_RADAU_P_LEGENDRE = 3             # 1D Gauss-Radau-Legendre quadrature points, pinned at x=1
    GAUSS_LOBATTO_LEGENDRE = 4             # 1D Gauss-Lobatto-Legendre quadrature points
    GAUSS_GAUSS_CHEBYSHEV = 5              # 1D Gauss-Gauss-Chebyshev quadrature points
    GAUSS_RADAU_M_CHEBYSHEV = 6            # 1D Gauss-Radau-Chebyshev quadrature points, pinned at x=-1
    GAUSS_RADAU_P_CHEBYSHEV = 7            # 1D Gauss-Radau-Chebyshev quadrature points, pinned at x=1
    GAUSS_LOBATTO_CHEBYSHEV = 8            # 1D Gauss-Lobatto-Chebyshev quadrature points
    GAUSS_RADAU_M_ALPHA0_BETA1 = 9         # Gauss Radau pinned at x=-1, alpha=0, beta=1
    GAUSS_RADAU_M_ALPHA0_BETA2 = 10        # Gauss Radau pinned at x=-1, alpha=0, beta=2
    GAUSS_RADAU_M_ALPHA1_BETA0 = 11        # Gauss Radau pinned at x=-1, alpha=1, beta=0
    GAUSS_RADAU_M_ALPHA2_BETA0 = 12        # Gauss Radau pinned at x=-1, alpha=2, beta=0
    GAUSS_KRONROD_LEGENDRE = 13            # 1D Gauss-Kronrod-Legendre quadrature points
    GAUSS_RADAU_KRONROD_M_LEGENDRE = 14    # 1D Gauss-Radau-Kronrod-Legendre quadrature points, pinned at x=-1
    GAUSS_RADAU_KRONROD_M_ALPHA1_BETA0 = 15 # 1D Gauss-Radau-Kronrod-Legendre pinned at x=-1, alpha=1, beta=0
    GAUSS_LOBATTO_KRONROD_LEGENDRE = 16    # 1D Lobatto Kronrod quadrature points
    POLY_EVENLY_SPACED = 17                # 1D Evenly-spaced points using Lagrange polynomial
    FOURIER_EVENLY_SPACED = 18             # 1D Evenly-spaced points using Fourier Fit
    FOURIER_SINGLE_MODE_SPACED = 19        # 1D Non Evenly-spaced points for Single Mode analysis
    BOUNDARY_LAYER_POINTS = 20             # 1D power law distribution for boundary layer points
    BOUNDARY_LAYER_POINTS_REV = 21         # 1D power law distribution for boundary layer points (reversed)
    NODAL_TRI_ELEC = 22                    # 2D Nodal Electrostatic Points on a Triangle
    NODAL_TRI_FEKETE = 23                  # 2D Nodal Fekete Points on a Triangle
    NODAL_TRI_EVENLY_SPACED = 24           # 2D Evenly-spaced points on a Triangle
    NODAL_TET_EVENLY_SPACED = 25           # 3D Evenly-spaced points on a Tetrahedron
    NODAL_TET_ELEC = 26                    # 3D Nodal Electrostatic Points on a Tetrahedron
    NODAL_PRISM_EVENLY_SPACED = 27         # 3D Evenly-spaced points on a Prism
    NODAL_PRISM_ELEC = 28                  # 3D electrostatically spaced points on a Prism
    NODAL_TRI_SPI = 29                     # 2D Nodal Symmetric Positive Internal triangle (Whitherden, Vincent)
    NODAL_TET_SPI = 30                     # 3D Nodal Symmetric Positive Internal tetrahedron (Whitherden, Vincent)
    NODAL_PRISM_SPI = 31                   # 3D Prism SPI
    NODAL_QUAD_ELEC = 32                   # 2D GLL for quad
    NODAL_HEX_ELEC = 33                    # 3D GLL for hex
    SIZE_POINTS_TYPE = 34                  # Length of enum list    

class SolverType(Enum):
    """Enum describing the available solvers in Nektar++
    """
    ADR_SOLVER = "ADR Solver"
    ACOUSTIC_SOLVER = "Acoustic Solver"
    INCOMPRESSIBLE_NAVIER_STOKES_SOLVER = "Incompressible Navier Stokes Solver"
    CARDIAC_EPS_SOLVER = "Cardiac EPS Solver"
    COMPRESSIBLE_FLOW_SOLVER = "Compressible Flow Solver"
    DIFFUSION_SOLVER = "Diffusion Solver"
    IMAGE_WARPING_SOLVER = "Image Warping Solver"
    LINEAR_ELASTIC_SOLVER = "Linear Elastic Solver"
    MMF_SOLVER = "MMF Solver"
    PULSE_WAVE_SOLVER = "Pulse Wave Solver"
    SHALLOW_WATER_SOLVER = "Shallow Water Solver"
    VORTEX_WAVE_INTERACTION_SOLVER = "Vortex Wave Interaction Solver"