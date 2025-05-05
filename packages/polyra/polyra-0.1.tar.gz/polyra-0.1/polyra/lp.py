#linear programming functions, for an alternative to sample based abstraction. Not as powerful as sample based abstraction, but scales better to high dim
import numpy as np
try:
    from scipy.optimize import linprog
except ImportError:
    def linprog(*args, **kwargs):
        raise ImportError("scipy.optimize.linprog is not available. Please install scipy to use this function.")
from .hitnrun import hitnrun

epsilon = 1e-6


counter=0
def logprog():
    global counter
    counter+=1

def count_linprog():
    global counter
    return counter

def check_intersection(A_P, b_P, A_Q, b_Q):
    """Checks if two polytopes P and Q intersect using linear programming.
    
    P is defined as {x | A_P x ≤ b_P}
    Q is defined as {x | A_Q x ≤ b_Q}
    
    Returns True if they intersect, False otherwise.
    """
    # Stack constraints: A x ≤ b
    A = np.vstack([A_P, A_Q])
    b = np.hstack([b_P, b_Q])

    d = A.shape[1]  # Dimension of x
    c = np.zeros(d)  # Arbitrary objective function (we only check feasibility)

    logprog()
    # Solve feasibility problem
    res = linprog(c, A_ub=A, b_ub=b, method="highs", bounds=[(-np.inf, np.inf)] * d)

    return res.success  # True if feasible (intersection exists), False otherwise

def check_empty(A, b, return_solution=False):
    """Checks if there is any solution to a given polytope using linear programming.

    The polytope is defined as {x | A x ≤ b}

    Returns True if the polytope is empty, False otherwise.

    If return_solution is True, returns the solution x that makes the polytope empty.
    """
    d = A.shape[1]  # Dimension of x
    c = np.zeros(d)  # Arbitrary objective function (we only check feasibility)

    logprog()
    # Solve feasibility problem
    res = linprog(c, A_ub=A, b_ub=b, method="highs", bounds=[(-np.inf, np.inf)] * d)

    if return_solution:
        return not res.success, res.x
    return not res.success  # True if infeasible, False otherwise

def _add_constraint(A, b, A_new, b_new):
    """Adds a new constraint A_new x ≤ b_new to the polytope defined by A x ≤ b.

    Returns the new polytope defined by A_new x ≤ b_new ∩ A x ≤ b.
    """
    A = np.vstack([A, A_new])
    b = np.hstack([b, b_new])

    return A, b

def _merge_constraints(As, bs):
    """Merges multiple constraints into a single polytope.

    Returns the polytope defined by the constraints.
    """
    A = np.vstack(As)
    b = np.hstack(bs)

    return A, b

def _useless_constraint(A, b, A_t, b_t):
    """Checks if the addition of the constraint A_t x ≤ b_t is useless considering A x ≤ b.

    Returns True if the constraint is useless, False otherwise.

    Basically checks if the constraint is dominated by the existing constraints.
    
    This means we check if not (A_t x ≤ b_t) intersects with (A x ≤ b).

    Important: Requires inverting the inequality of the constraint to be tested, so only understands single constraints: len(b)=1.
    """
    # Invert inequality
    A_t = -A_t
    b_t = -b_t-epsilon

    # Check if the new constraint is dominated by the existing constraints
    return not check_intersection(A_t, b_t, A, b)
    

def simplify_polytope(A, b):
    """Removes redundant constraints from the polytope defined by A x ≤ b.

    Returns the simplified polytope.

    Fourier-Motzkin elimination algorithm could be interesting. Needs to be considered. Here instead simply checks for each constraint if it is useless. If found useless, removes it.
    """

    constraints = A.shape[0]
    for i in range(constraints)[::-1]:
        A_without= np.delete(A, i, axis=0)
        b_without = np.delete(b, i)
        A_i = A[i:i+1]
        b_i = b[i:i+1]
        if _useless_constraint(A_without, b_without, A_i, b_i):
            A = np.delete(A, i, axis=0)
            b = np.delete(b, i)

    return A, b

def _iterate_constraints(A, b):
    """Iterates over all constraints of the polytope defined by A x ≤ b.

    Returns the constraints one by one.
    """
    if len(A.shape)==1:
        yield A,b
        return
    for i in range(A.shape[0]):
        yield A[i:i+1], b[i]

def inside_polytope(A_O, b_O, A_I, b_I):
    """Checks if the polytope defined by A_I x ≤ b_I is inside the polytope defined by A_O x ≤ b_O.

    This means, that every constraint of O would be useless as a constraint of I.
    (Needs double checking!!!)

    Returns True if the polytope is inside, False otherwise.
    """
    for A, b in _iterate_constraints(A_O, b_O):
        if not _useless_constraint(A_I, b_I, A, b):
            return False
    return True

def _relative_volume(A_O, b_O, A_I, b_I):
    """Checks the relative volume of the polytope defined by A_I x ≤ b_I in the polytope defined by A_O x ≤ b_O."""
    #start with a point that is in the outer polytope
    empty, x0 = check_empty(A_O, b_O, return_solution=True)
    if empty:
        raise ValueError("Outer polytope is empty")

    points=hitnrun(A_O, b_O, x0)

    #check how many points are in the inner polytope
    check=np.mean(np.all(points@A_I.T<=b_I, axis=1))

    return check

def _relative_volume_except(A_O, b_O, A_1, b_1, A_2, b_2):
    """Checks the relative volume in the polytope defined by A_O x ≤ b_O except for the polytopes defined by A_1 x ≤ b_1 or A_2 x ≤ b_2."""
    #start with a point that is in the outer polytope
    empty, x0 = check_empty(A_O, b_O, return_solution=True)
    if empty:
        raise ValueError("Outer polytope is empty")

    points=hitnrun(A_O, b_O, x0)

    in1=np.all(points@A_1.T<=b_1, axis=1)
    in2=np.all(points@A_2.T<=b_2, axis=1)

    #search for the fraction of points that are both not in the first and second polytope
    check=np.mean(np.logical_and(np.logical_not(in1),np.logical_not(in2)))

    return check

def _gen_points(A, b):
    """generates a set of points from the polytope defined by A x ≤ b."""
    empty, x0 = check_empty(A, b, return_solution=True)
    if empty:
        raise ValueError("Polytope is empty")

    points=hitnrun(A, b, x0)

    return points


def merge_polytopes(A_1, b_1, A_2, b_2):
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

    As,bs=[],[]
    for A,b in _iterate_constraints(A_1, b_1):
        if _useless_constraint(A_2, b_2, A, b):
            As.append(A)
            bs.append(b)
    for A,b in _iterate_constraints(A_2, b_2):
        if _useless_constraint(A_1, b_1, A, b):
            As.append(A)
            bs.append(b)

    if len(As)==0:
        raise ValueError("Polytopes cannot be merged")

    return _merge_constraints(As, bs)


def mergable_polytopes(A_1, b_1, A_2, b_2, maximum_error=0.001):
    """Checks if two polytopes A_1 x ≤ b_1 and A_2 x ≤ b_2 can be merged into a single polytope A x ≤ b.

    Returns the new polytope if the polytopes can be merged, None otherwise.

    Allows to increase the volume by a maximum of maximum_error.
    """

    try:
        A,b=merge_polytopes(A_1, b_1, A_2, b_2)
    except ValueError:
        return None
    A,b=simplify_polytope(A,b)
    if len(A)==0: #first case: Fails to merge the polytopes, so return False
        return None

    #Then check if the two polytopes are inside the merged polytope
    if not inside_polytope(A, b, A_1, b_1) or not inside_polytope(A, b, A_2, b_2):
        return None

    #Then check the relative volume of the merged polytope in the two polytopes
    relv=_relative_volume_except(A, b, A_1, b_1, A_2, b_2)
    if relv>maximum_error:
        return None

    return A,b

mhash=set()
def hash_mergable(A_1, b_1, A_2, b_2,maximum_error=0.001):
    """version of mergable that simply uses a hash to store unmergables"""
    h=str([A_1, b_1, A_2, b_2])
    h2=str([A_2, b_2, A_1, b_1])
    h=min(h,h2)
    if h in mhash:
        return None
    m=mergable_polytopes(A_1, b_1, A_2, b_2, maximum_error)
    if m is None:
        mhash.add(h)
    return m






