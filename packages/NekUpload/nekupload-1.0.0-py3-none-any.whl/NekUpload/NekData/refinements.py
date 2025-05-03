import numpy as np

class Refinements:
    def __init__(self,ref_id:int,type:str,radius:float,
                coordinate1:np.ndarray,coordinate2:np.ndarray,
                nummodes:str,numpoints:str):
        """Class initialiser

        Args:
            ref_id (int): Refinement reference ID
            type (str): STANDARD or SPHERE
            radius (float): Radius
            coordinate1 (np.ndarray): Coordinate x,y,z
            coordinate2 (np.ndarray): Coordinate x,y,z
            nummodes (str): Number of modes in refinement
            numpoints (str): Number of points in refinement
        """
        self.ref_id = ref_id
        self.type = type
        self.radius = radius
        self.coordinate1 = coordinate1
        self.coordinate2 = coordinate2
        self.nummodes = nummodes
        self.nimpoints = numpoints