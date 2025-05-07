from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, NonNegativeFloat
from typing import Union, Dict, List, Literal, Optional, Tuple

# from steam_sdk.data.DataConductor import ConstantJc, Bottura, CUDI3, Bordini, BSCCO_2212_LBNL, CUDI1, Summers, Round, \
#     Rectangular, Rutherford, Mono, Ribbon, Ic_A_NbTi
from steam_sdk.data.DataConductorFiQuS import Conductor as ConductorFiQuS


from steam_sdk.data.DataModelCommon import Circuit_Class
from steam_sdk.data.DataModelCommon import PowerSupplyClass
from steam_sdk.data.DataFiQuSCWS import CWS
from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrand
from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherford
from steam_sdk.data.DataFiQuSPancake3D import *
from steam_sdk.data.DataFiQuSMultipole import *

class CCTGeometryCWSInputs(BaseModel):
    """
        Level 3: Class for controlling if and where the conductor files and brep files are written for the CWS (conductor with step) workflow
    """
    write: bool = False             # if true only conductor and brep files are written, everything else is skipped.
    output_folder: Optional[str] = None       # this is relative path to the input file location


class CCTGeometryWinding(BaseModel):  # Geometry related windings _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    r_wms: Optional[List[float]] = None  # radius of the middle of the winding
    n_turnss: Optional[List[float]] = None  # number of turns
    ndpts: Optional[List[int]] = None  # number of divisions of turn, i.e. number of hexagonal elements for each turn
    ndpt_ins: Optional[List[int]] = None  # number of divisions of terminals ins
    ndpt_outs: Optional[List[int]] = None  # number of divisions of terminals outs
    lps: Optional[List[float]] = None  # layer pitch
    alphas: Optional[List[float]] = None  # tilt angle
    wwws: Optional[List[float]] = None  # winding wire widths (assuming rectangular)
    wwhs: Optional[List[float]] = None  # winding wire heights (assuming rectangular)


class CCTGeometryFQPCs(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = []  # name to use in gmsh and getdp
    fndpls: Optional[List[int]] = None  # fqpl number of divisions per length
    fwws: Optional[List[float]] = None  # fqpl wire widths (assuming rectangular) for theta = 0 this is x dimension
    fwhs: Optional[List[float]] = None  # fqpl wire heights (assuming rectangular) for theta = 0 this is y dimension
    r_ins: Optional[List[float]] = None  # radiuses for inner diameter for fqpl (radial (or x direction for theta=0) for placing the fqpl
    r_bs: Optional[List[float]] = None  # radiuses for bending the fqpl by 180 degrees
    n_sbs: Optional[List[int]] = None  # number of 'bending segmetns' for the 180 degrees turn
    thetas: Optional[List[float]] = None  # rotation in deg from x+ axis towards y+ axis about z axis.
    z_starts: Optional[List[str]] = None  # which air boundary to start at. These is string with either: z_min or z_max key from the Air region.
    z_ends: Optional[List[float]] = None  # z coordinate of loop end


class CCTGeometryFormer(BaseModel):  # Geometry related formers _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    r_ins: Optional[List[float]] = None  # inner radius
    r_outs: Optional[List[float]] = None  # outer radius
    z_mins: Optional[List[float]] = None  # extend of former  in negative z direction
    z_maxs: Optional[List[float]] = None  # extend of former in positive z direction
    rotates: Optional[List[float]] = None  # rotation of the former around its axis in degrees


class CCTGeometryAir(BaseModel):  # Geometry related air_region _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    name: Optional[str] = None  # name to use in gmsh and getdp
    sh_type: Optional[str] = None  # cylinder or cuboid are possible
    ar: Optional[float] = None  # if box type is cuboid a is taken as a dimension, if cylinder then r is taken
    z_min: Optional[float] = None  # extend of air region in negative z direction
    z_max: Optional[float] = None  # extend of air region in positive z direction


class CCTGeometry(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    CWS_inputs: CCTGeometryCWSInputs = CCTGeometryCWSInputs()
    windings: CCTGeometryWinding = CCTGeometryWinding()
    fqpcs: CCTGeometryFQPCs = CCTGeometryFQPCs()
    formers: CCTGeometryFormer = CCTGeometryFormer()
    air: CCTGeometryAir = CCTGeometryAir()


class CCTMesh(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    MaxAspectWindings: Optional[float] = None  # used in transfinite mesh_generators settings to define mesh_generators size along two longer lines of hex elements of windings
    ThresholdSizeMin: Optional[float] = None  # sets field control of Threshold SizeMin
    ThresholdSizeMax: Optional[float] = None  # sets field control of Threshold SizeMax
    ThresholdDistMin: Optional[float] = None  # sets field control of Threshold DistMin
    ThresholdDistMax: Optional[float] = None  # sets field control of Threshold DistMax


class CCTSolveWinding(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: Optional[List[float]] = None  # current in the wire
    sigmas: Optional[List[float]] = None  # electrical conductivity
    mu_rs: Optional[List[float]] = None  # relative permeability


class CCTSolveFormer(BaseModel):  # Solution time used formers _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigmas: Optional[List[float]] = None  # electrical conductivity
    mu_rs: Optional[List[float]] = None  # relative permeability


class CCTSolveFQPCs(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = []  # current in the wire
    sigmas: List[float] = []  # electrical conductivity
    mu_rs: List[float] = []  # relative permeability


class CCTSolveAir(BaseModel):  # Solution time used air _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigma: Optional[float] = None  # electrical conductivity
    mu_r: Optional[float] = None  # relative permeability


class CCTSolve(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    windings: CCTSolveWinding = CCTSolveWinding()  # windings solution time _inputs
    formers: CCTSolveFormer = CCTSolveFormer()  # former solution time _inputs
    fqpcs: CCTSolveFQPCs = CCTSolveFQPCs()  # fqpls solution time _inputs
    air: CCTSolveAir = CCTSolveAir()  # air solution time _inputs
    pro_template: Optional[str] = None  # file name of .pro template file
    variables: Optional[List[str]] = None  # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by GetDP, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions to post-process by GetDP, like .pos


class CCTPostproc(BaseModel):
    """
        Level 2: Class for  FiQuS CCT
    """
    windings_wwns: Optional[List[int]] = None  # wires in width direction numbers
    windings_whns: Optional[List[int]] = None  # wires in height direction numbers
    additional_outputs: Optional[List[str]] = None  # Name of software specific input files to prepare, like :LEDET3D
    winding_order: Optional[List[int]] = None
    fqpcs_export_trim_tol: Optional[List[float]] = None  # this multiplier times winding extend gives 'z' coordinate above(below) which hexes are exported for LEDET, length of this list must match number of fqpls
    variables: Optional[List[str]] = None  # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by python Gmsh API, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions o post-process by python Gmsh API, like .pos


class CCT(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    type: Literal['CCT_straight']
    geometry: CCTGeometry = CCTGeometry()
    mesh: CCTMesh = CCTMesh()
    solve: CCTSolve = CCTSolve()
    postproc: CCTPostproc = CCTPostproc()

class RunFiQuS(BaseModel):
    """
    Class for FiQuS run
    """

    type: Optional[Literal[
        "start_from_yaml",
        "mesh_only",
        "geometry_only",
        "geometry_and_mesh",
        "pre_process_only",
        "mesh_and_solve_with_post_process_python",
        "solve_with_post_process_python",
        "solve_only",
        "post_process_getdp_only",
        "post_process_python_only",
        "post_process",
        "batch_post_process_python",
    ]] = Field(
        default="start_from_yaml",
        title="Run Type of FiQuS",
        description="FiQuS allows you to run the model in different ways. The run type can be specified here. For example, you can just create the geometry and mesh or just solve the model with previous mesh, etc.",
    )
    geometry: Optional[Union[str, int]] = Field(
        default=None,
        title="Geometry Folder Key",
        description="This key will be appended to the geometry folder.",
    )
    mesh: Optional[Union[str, int]] = Field(
        default=None,
        title="Mesh Folder Key",
        description="This key will be appended to the mesh folder.",
    )
    solution: Optional[Union[str, int]] = Field(
        default=None,
        title="Solution Folder Key",
        description="This key will be appended to the solution folder.",
    )
    launch_gui: Optional[bool] = Field(
        default=False,
        title="Launch GUI",
        description="If True, the GUI will be launched after the run.",
    )
    overwrite: Optional[bool] = Field(
        default=False,
        title="Overwrite",
        description="If True, the existing folders will be overwritten, otherwise new folders will be created.",
    )
    comments: str = Field(
        default="",
        title="Comments",
        description="Comments for the run. These comments will be saved in the run_log.csv file.",
    )
    verbosity_Gmsh: int = Field(
        default=5,
        title="verbosity_Gmsh",
        description="Level of information printed on the terminal and the message console (0: silent except for fatal errors, 1: +errors, 2: +warnings, 3: +direct, 4: +information, 5: +status, 99: +debug)",
    )
    verbosity_GetDP: int = Field(
        default=5,
        title="verbosity_GetDP",
        description="Level of information printed on the terminal and the message console. Higher number prints more, good options are 5 or 6.",
    )
    verbosity_FiQuS: bool = Field(
        default=True,
        title="verbosity_FiQuS",
        description="Level of information printed on the terminal and the message console by FiQuS. Only True of False for now.",
    )


class General(BaseModel):
    """
        Class for FiQuS general
    """
    magnet_name: Optional[str] = None


class EnergyExtraction(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    t_trigger: Optional[float] = None
    R_EE: Optional[float] = None
    power_R_EE: Optional[float] = None
    L: Optional[float] = None
    C: Optional[float] = None


class QuenchHeaters(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    N_strips: Optional[int] = None
    t_trigger: Optional[List[float]] = None
    U0: Optional[List[float]] = None
    C: Optional[List[float]] = None
    R_warm: Optional[List[float]] = None
    w: Optional[List[float]] = None
    h: Optional[List[float]] = None
    h_ins: List[List[float]] = []
    type_ins: List[List[str]] = []
    h_ground_ins: List[List[float]] = []
    type_ground_ins: List[List[str]] = []
    l: Optional[List[float]] = None
    l_copper: Optional[List[float]] = None
    l_stainless_steel: Optional[List[float]] = None
    ids: Optional[List[int]] = None
    turns: Optional[List[int]] = None
    turns_sides: Optional[List[str]] = None


class Cliq(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    t_trigger: Optional[float] = None
    current_direction: Optional[List[int]] = None
    sym_factor: Optional[int] = None
    N_units: Optional[int] = None
    U0: Optional[float] = None
    C: Optional[float] = None
    R: Optional[float] = None
    L: Optional[float] = None
    I0: Optional[float] = None

class ESC(BaseModel):
    """
        Level 2: Class for the ESC parameters
    """
    t_trigger: Optional[List[float]] = None
    U0: Optional[List[float]] = None
    C: Optional[List[float]] = None
    R_unit: Optional[List[float]] = None
    R_leads: Optional[List[float]] = None
    Ud_Diode: Optional[List[float]] = None

class QuenchProtection(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    energy_extraction:  EnergyExtraction = EnergyExtraction()
    quench_heaters: QuenchHeaters = QuenchHeaters()
    cliq: Cliq = Cliq()
    esc: ESC = ESC()

class QuenchDetection(BaseModel):
    """
    Level 2: Class for FiQuS
    """

    voltage_thresholds: Optional[List[float]] = Field(
        default=None,
        title="List of quench detection voltage thresholds",
        description="Voltage thresholds for quench detection. The quench detection will be triggered when the voltage exceeds these thresholds continuously for a time larger than the discrimination time.",
    )

    discrimination_times: Optional[List[float]] = Field(
        default=None,
        title="List of quench detection discrimination times",
        description="Discrimination times for quench detection. The quench detection will be triggered when the voltage exceeds the thresholds continuously for a time larger than these discrimination times.",
    )

    voltage_tap_pairs: Optional[List[List[int]]] = Field(
        default=None,
        title="List of quench detection voltage tap pairs",
        description="Voltage tap pairs for quench detection. The voltage difference between these pairs will be used for quench detection.",
    )

class DataFiQuS(BaseModel):
    """
        This is data structure of FiQuS Input file
    """
    general: General = General()
    run: RunFiQuS = RunFiQuS()
    magnet: Union[CCT, CWS, Multipole, Pancake3D, CACStrand, CACRutherford] = {'type': 'multipole'}
    circuit: Circuit_Class = Circuit_Class()
    power_supply: PowerSupplyClass = PowerSupplyClass()
    quench_protection: QuenchProtection = QuenchProtection()
    quench_detection: QuenchDetection = QuenchDetection()
    conductors: Dict[str, ConductorFiQuS] = {}
