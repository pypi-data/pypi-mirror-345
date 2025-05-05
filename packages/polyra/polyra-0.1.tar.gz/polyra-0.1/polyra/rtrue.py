#trivially true region
import numpy as np
from .basereg import BaseRegion, TRUE, FALSE, register

class RTRUE(BaseRegion):
    def __init__(self):

        super().__init__()

    def predict(self, samples):
        return np.ones(samples.shape[0],dtype=bool)

    def __str__(self):
        return f"TRUE"

    def __repr__(self):
        return f"RTRUE()"

    def tabstr(self):
        return str(self)

    def copy(self):
        return RTRUE()

    def identify(self):
        return "RTRUE"

    def negate(self):
        return FALSE()

    def slice(self, feature, value):
        return self.copy()

    def project(self, point, axis):
        return self.copy()

    def copy_apply(self, func):
        return func(self.copy())

    def dimensionality(self):
        return -1

    def is_true(self):
        return True

    def to_dict(self):
        return {"type": "RTRUE"}

    @classmethod
    def _init_from_dict(self,d):
        return RTRUE()

    def count_floats(self):
        return 0

register(RTRUE)
