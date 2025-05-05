#Most basic region specifier
import numpy as np
from .basereg import BaseRegion, register, TRUE, FALSE

class Halfspace(BaseRegion):
    def __init__(self,A,b):

        self.A=A
        self.b=b
        self.normalize()

        super().__init__()

    def normalize(self):
        radius=np.linalg.norm(self.A,axis=0)
        if radius==0:
            return
        self.A=self.A/radius
        self.b=self.b/radius

    def predict(self, samples):
        q=np.dot(samples,self.A)<=self.b
        while len(q.shape)>1:
            q=np.all(q,axis=1)
        return q    

    def __str__(self):
        return f"{self.A}*x<={self.b}"

    def __repr__(self):
        return f"Halfspace(A={self.A},b={self.b})"

    def tabstr(self):
        return str(self)

    def copy(self):
        return Halfspace(self.A.copy(),self.b.copy())

    def identify(self):
        return "Halfspace"

    def negate(self):
        return Halfspace(-self.A.copy(),-self.b.copy())

    def slice(self, feature, value):
        A=self.A.copy()
        b=self.b.copy()
        if len(A.shape)==1:
            b=b-A[feature]*value
            A=np.delete(A,feature)
        else:
            b=b-A[feature,:]*value
            A=np.delete(A,feature,axis=0)
        return Halfspace(A,b)

    def project(self, point, axis):
        #transforms the task into alpha space, where every sample lies on point+alpha*axis

        term1=self.b-np.dot(self.A,point)
        term2=np.dot(self.A,axis)
        if term2==0:
            return TRUE
        A=np.array([term2])
        b=np.array([term1])
        return Halfspace(A,b)




    def copy_apply(self, func):
        return func(self.copy())

    def dimensionality(self):
        return len(self.A)

    def to_polytope(self):
        return (self.A,self.b)

    def to_dict(self):
        return {
            "type": "Halfspace",
            "A": self.A.tolist(),
            "b": self.b.tolist()
        }

    @classmethod
    def _init_from_dict(self,d):
        A=np.array(d["A"])
        b=np.array(d["b"])
        return Halfspace(A,b)

    def count_floats(self):
        return int(np.prod(self.A.shape))+int(np.prod(self.b.shape))

register(Halfspace)
