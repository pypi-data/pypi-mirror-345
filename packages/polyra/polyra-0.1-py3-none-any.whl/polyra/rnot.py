#NOT connector for a region. For the sample to lie in the resulting region, it has to not lie in the child region
import numpy as np
from .region import Region, register, from_dict

from .ror import ROR
from .rand import RAND
from .halfspace import Halfspace

class RNOT(Region):
    def __init__(self,child):

        self.child = child

        super().__init__()

    def predict(self, samples):
        return np.logical_not(self.child.predict(samples))

    def __str__(self):
        return f"!({self.child})"

    def __repr__(self):
        return f"RNOT({self.child})"

    def tabstr(self):
        return "NOT\n" + self.tabify(self.child.tabstr())

    def simplify(self):
        self.child = self.child.simplify()
        if isinstance(self.child, RNOT):
            return self.child.child.copy()
        elif isinstance(self.child,RAND):
            return ROR(*[RNOT(c).simplify() for c in self.child.children])
        elif isinstance(self.child,ROR):
            return RAND(*[RNOT(c).simplify() for c in self.child.children])
        elif self.child.is_base():
            return self.child.negate().simplify()
        return self.copy()

    def copy(self):
        return RNOT(self.child.copy())

    def identify(self):
        return "RNOT"

    def slice(self, feature, value):
        return RNOT(self.child.slice(feature, value))

    def project(self, point, axis):
        return RNOT(self.child.project(point, axis))

    def copy_apply(self, func):
        return func(RNOT(self.child.copy_apply(func)))

    def to_dict(self):
        return {"type": "RNOT", "child": self.child.to_dict()}

    @classmethod
    def _init_from_dict(self,d):
        child = from_dict(d["child"])
        return RNOT(child)

    def count_floats(self):
        return self.child.count_floats()

register(RNOT)
