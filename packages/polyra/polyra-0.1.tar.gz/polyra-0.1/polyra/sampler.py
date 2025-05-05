#pendant to lp.py for sampling instead of linear programming. Used in sample based abstraction
import numpy as np
from scipy.optimize import linprog
from .hitnrun import hitnrun

epsilon = 1e-6


counter=0
def logprog():
    global counter
    counter+=1

def count_linprog():
    global counter
    return counter

def check_intersection_s(P, Q, unlabeled):
    """Checks if two polytopes P and Q intersect using sampling."""
    return np.any(np.logical_and(P.predict(unlabeled) == 1, Q.predict(unlabeled) == 1))

def check_empty_s(P, unlabeled, return_solution=False):
    """Checks if a polytope P is empty using sampling."""
    pred=P.predict(unlabeled)
    if return_solution:
        if np.any(pred == 1):
            return False, unlabeled[pred == 1][0]
        else:
            return True, None
    return np.all(pred == 0)

def _add_constraint(P, Q):

    return (P & Q)

def _merge_many(As):
    ret=None
    for A in As:
        if ret is None:
            ret=A
        else:
            ret=ret & A
    return ret

def _useless_constraint_s(A, At, unlabeled):
    """Checks if the addition of the constraint A_t x ≤ b_t is useless considering A x ≤ b.

    Returns True if the constraint is useless, False otherwise.

    Basically checks if the constraint is dominated by the existing constraints.
    
    This means we check if not (A_t x ≤ b_t) intersects with (A x ≤ b).

    Important: Requires inverting the inequality of the constraint to be tested, so only understands single constraints: len(b)=1.
    """
    At=~At

    # Check if the new constraint is dominated by the existing constraints
    return not check_intersection_s(At, A, unlabeled)
    

def simplify_polytope_s(A, unlabeled):
    """Removes redundant constraints from the polytope defined by A x ≤ b.

    Returns the simplified polytope.

    Fourier-Motzkin elimination algorithm could be interesting. Needs to be considered. Here instead simply checks for each constraint if it is useless. If found useless, removes it.
    """

    if not A.is_and():return A

    constraints = len(A.children)
    for i in range(constraints)[::-1]:
        Aw=A.copy()
        Ai=Aw.children.pop(i)
        if _useless_constraint_s(Aw, Ai, unlabeled):
            A.children.pop(i)

    return A

def inside_polytope_s(O, I, unlabeled):
    """Checks if the polytope defined by A_I x ≤ b_I is inside the polytope defined by A_O x ≤ b_O.

    This means, that every constraint of O would be useless as a constraint of I.
    (Needs double checking!!!)

    Returns True if the polytope is inside, False otherwise.
    """
    return not np.any(np.logical_and(O.predict(unlabeled)==0, I.predict(unlabeled)==1))

def _relative_volume_s(O, I, unlabeled):
    """Checks the relative volume of the polytope defined by A_I x ≤ b_I in the polytope defined by A_O x ≤ b_O."""
    return np.mean(np.mean(I.predict(unlabeled)==1)/(np.mean(O.predict(unlabeled)==1)+epsilon))

def _relative_volume_except_s(O, I_1, I_2, unlabeled):
    """Checks the relative volume in the polytope defined by A_O x ≤ b_O except for the polytopes defined by A_1 x ≤ b_1 or A_2 x ≤ b_2."""
    Op=O.predict(unlabeled)
    I1p=I_1.predict(unlabeled)
    I2p=I_2.predict(unlabeled)
    #search for the fraction of points outside of I1 and I2 but in O as a fraction of the points in O
    poi_in_O=np.mean(Op==1)
    poi_not_in_Is_but_O=np.mean(np.logical_and(Op==1, np.logical_and(I1p==0, I2p==0)))
    if poi_in_O==0:
        return 0
    return poi_not_in_Is_but_O/(poi_in_O+epsilon)

def _iterate_constraints(A):
    if not A.is_and():
        yield A
        return
    else:
        for child in A.children:
            yield child

def merge_polytopes_s(A1, A2, unlabeled):
    """If I have two polytopes A_1 x ≤ b_1 and A_2 x ≤ b_2 connected by OR operations, can I merge them into a single polytope A x ≤ b?

    Following Idea: constraints like 1<=x<=2 and 2<=x<=3 can be merged into 1<=x<=3.

    Assuming the polytopes can be merged. Then I have two types of constraints in each polytope: Those that are useless to the other and those that are not. I want to keep only the useless ones right?

    Lets try that.

    Seems to work. Doublecheck of course.

    In any case, still requires "mergable". Currently basically just calculates an outer hull with restrictions.

    Generally for this one probably needs to check whether (p1 or p2=M) p1 in M and p2 in M to see if the restrictions kill the check. But that should be easy-ish.

    The rest depends on volume. And that is obviously hard, as it likely requires to calculate the volume of the intersection. And that is likely not easy in high dimensions.

    For low dimensional stuff, sampling will work easily. 

    Actually maybe..considering that I dont really care about 100% accuracy. If I find a way to quickly generate random samples from a polytope (M), then I just have to check whether its in p1 or p2 and dont have a volume, but a fraction of erroneous volume. That might be enough.

    For generating points: Apparently Affine Transformation Sampling is a thing. This just finds a enclosing ellipsoid which apparently has dim^3 dependency, which is not too bad. Then I can just sample from that and check whether the point is in the polytope (I think). That should be fast enough.

    """

    As=[]
    for A in _iterate_constraints(A1):
        if _useless_constraint_s(A2,A, unlabeled):
            As.append(A)
    for A in _iterate_constraints(A2):
        if _useless_constraint_s(A1,A, unlabeled):
            As.append(A)

    if len(As)==0:
        raise ValueError("Polytopes cannot be merged")

    return _merge_many(As)


def mergable_polytopes_s(A1, A2, unlabeled, maximum_error=0.001):
    """Checks if two polytopes A_1 x ≤ b_1 and A_2 x ≤ b_2 can be merged into a single polytope A x ≤ b.

    Returns the new polytope if the polytopes can be merged, None otherwise.

    Allows to increase the volume by a maximum of maximum_error.
    """

    try:
        A=merge_polytopes_s(A1, A2, unlabeled)
    except ValueError:
        return None
    A=simplify_polytope_s(A,unlabeled)
    if (not A.is_and()) or (len(A.children)==0):
        return None

    if not inside_polytope_s(A, A1, unlabeled) or not inside_polytope_s(A, A2, unlabeled):
        return None

    relv=_relative_volume_except_s(A, A1, A2, unlabeled)
    if relv>maximum_error:
        return None

    return A






