#initially thought to be an alternative to Halfspace. Ignored and not functional currently, because to complicated for the time limit
import numpy as np
from .basereg import BaseRegion

class Borderspace(BaseRegion):
    def __init__(self,A,mn,mx):

        self.A=A
        self.mn=mn
        self.mx=mx

        super().__init__()

    def predict(self, samples):
        return np.all(self.mn<=np.dot(samples,self.A)<=self.mx,axis=1)
    def __str__(self):
        return f"{self.mn}<={self.A}*x<={self.mx}"

    def __repr__(self):
        return f"Borderspace({self.A},{self.mn},{self.mx})"

    def tabstr(self):
        return str(self)

    def copy(self):
        return Borderspace(self.A,self.mn,self.mx)

    def identify(self):
        return "BORDERSPACE"



