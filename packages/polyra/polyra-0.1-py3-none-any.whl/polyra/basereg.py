#baseclass to make it simpler to create new types of regions, instead of just Halfspace
from .region import Region, TRUE, FALSE, register


class BaseRegion(Region):
    def __init__(self):
        super().__init__()

    def is_base(self):
        return True

    def is_composite(self):
        return False

    def negate(self):
        raise NotImplementedError("BaseRegion.negate() must by implemented by subclass {}".format(self.__class__.__name__))

    def dimensionality(self):
        raise NotImplementedError("BaseRegion.dimensionality() must by implemented by subclass {}".format(self.__class__.__name__))

    def to_polytope(self):
        raise NotImplementedError("BaseRegion.to_polytope() must by implemented by subclass {}".format(self.__class__.__name__))
