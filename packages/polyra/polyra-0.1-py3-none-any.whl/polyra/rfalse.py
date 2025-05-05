#empty region
import numpy as np
from .basereg import BaseRegion, TRUE, FALSE, register

class RFALSE(BaseRegion):
    def __init__(self):

        super().__init__()

    def predict(self, samples):
        return np.zeros(samples.shape[0],dtype=bool)

    def __str__(self):
        return f"FALSE"

    def __repr__(self):
        return f"RFALSE()"

    def tabstr(self):
        return str(self)

    def copy(self):
        return RFALSE()

    def identify(self):
        return "RFALSE"

    def negate(self):
        return TRUE()

    def slice(self, feature, value):
        return self.copy()

    def project(self, point, axis):
        return self.copy()

    def copy_apply(self, func):
        return func(self.copy())

    def dimensionality(self):
        return -1

    def is_false(self):
        return True

    def to_dict(self):
        return {"type": "RFALSE"}

    @classmethod
    def _init_from_dict(self, d):
        return RFALSE()

    def count_floats(self):
        return 0

register(RFALSE)
