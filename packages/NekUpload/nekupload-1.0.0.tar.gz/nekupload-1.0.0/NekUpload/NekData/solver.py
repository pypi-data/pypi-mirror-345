from NekUpload.NekData.data_type import SolverType

class SolverInfo:
    def __init__(self,solver: SolverType,dimension: int,equation_type: str):
        self.solver: SolverType = solver
        self.dimension: int = dimension
        self.equation_type: str = equation_type

    def get_var_num(self) -> int:
        if self.dimension == 1:
            return len(self._get_var_num_1d())
        elif self.dimension == 2:
            return len(self._get_var_num_2d())
        elif self.dimension == 3:
            return len(self._get_var_num_3d())

    def _get_var_num_1d(self) -> list[str]:
        if self.solver == SolverType.ACOUSTIC_SOLVER:
            if self.equation_type.strip().upper() == "LEE":
                return ["p","rhou","rho","rho0","c0sq","u0","gamma"]
            elif self.equation_type.strip().upper() == "APE":
                return ["p","u","rho0","c0sq","u0"]
        elif self.solver == SolverType.ADR_SOLVER:
            return ["u"]
        elif self.solver == SolverType.COMPRESSIBLE_FLOW_SOLVER:
            return ["rho","rhou","E","u","p","T","s","a","Mach","sensor"]
        elif self.solver == SolverType.INCOMPRESSIBLE_NAVIER_STOKES_SOLVER:
            return ["u","p"]
        elif self.solver == SolverType.SHALLOW_WATER_SOLVER:
            if self.equation_type.strip().upper() == "LINEARSWE":
                return ["eta","u"]
            elif self.equation_type.strip().upper() == "NONLINEARSWE":
                return ["h","hu"]

    def _get_var_num_2d(self) -> list[str]:
        var_1d: list[str] = self._get_var_num_1d()
        extra_var = []
        if self.solver == SolverType.ACOUSTIC_SOLVER:
            if self.equation_type == "LEE":
                extra_var = ["rhov","v0"]
            elif self.equation_type == "APE":
                extra_var = ["v","v0"]
        elif self.solver == SolverType.ADR_SOLVER:
            extra_var = ["v"]
        elif self.solver == SolverType.COMPRESSIBLE_FLOW_SOLVER:
            extra_var = ["rhov","v"]
        elif self.solver == SolverType.INCOMPRESSIBLE_NAVIER_STOKES_SOLVER:
            extra_var = ["v"]
        elif self.solver == SolverType.SHALLOW_WATER_SOLVER:
            if self.equation_type.strip().upper() == "LINEARSWE":
                extra_var = ["v"]
            elif self.equation_type.strip().upper() == "NONLINEARSWE":
                extra_var = ["hv"]
        return var_1d + extra_var

    def _get_var_num_3d(self) -> list[str]:
        var_2d: list[str] = self._get_var_num_2d()
        extra_var = []
        if self.solver == SolverType.ACOUSTIC_SOLVER:
            if self.equation_type == "LEE":
                extra_var = ["rhow","w0"]
            elif self.equation_type == "APE":
                extra_var = ["w","w0"]
        elif self.solver == SolverType.ADR_SOLVER:
            extra_var = ["w"]
        elif self.solver == SolverType.COMPRESSIBLE_FLOW_SOLVER:
            extra_var = ["rhow","w"]
        elif self.solver == SolverType.INCOMPRESSIBLE_NAVIER_STOKES_SOLVER:
            extra_var = ["w"]
        elif self.solver == SolverType.SHALLOW_WATER_SOLVER:
            if self.equation_type.strip().upper() == "LINEARSWE":
                extra_var = ["w"]
            elif self.equation_type.strip().upper() == "NONLINEARSWE":
                extra_var = ["hw"]
                
        return var_2d + extra_var

