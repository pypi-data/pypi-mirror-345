#basic region class. Contains type inspecific functions. The difference to polyra is, that polyra handles the learning and constructs a region
from tqdm import tqdm
import numpy as np
import json

from .lp import simplify_polytope, check_empty, mergable_polytopes
from .sampler import simplify_polytope_s, check_empty_s, mergable_polytopes_s


class Region():
    def __init__(self):
        pass

    def predict(self,samples):
        raise NotImplementedError("Region.predict() must be implemented by subclass {}.".format(self.__class__.__name__))

    def fraction(self,samples):
        """similar to predict, but instead of returning boolean values, returns fractions for "and" regions """
        return self.predict(samples)

    def __str__(self):
        raise NotImplementedError("Region.__str__() must be implemented by subclass {}.".format(self.__class__.__name__))

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def tabify(q):
        return "\n".join(["    "+line for line in q.split("\n")])
    def tabstr(self):
        raise NotImplementedError("Region.tabstr() must be implemented by subclass {}.".format(self.__class__.__name__))

    def simplify(self):
        return self.copy()

    def copy(self):
        raise NotImplementedError("Region.copy() must be implemented by subclass {}.".format(self.__class__.__name__))

    def identify(self):
        raise NotImplementedError("Region.identify() must be implemented by subclass {}.".format(self.__class__.__name__))


    def is_base(self):
        """opposite of is_composite"""
        return False

    def is_composite(self):
        """opposite of is_base, is this region constructed from multiple regions"""
        return True

    def go_dnf(self):
        """transform a region construct in a shape that is of structure OR (AND)"""
        return self.copy()

    def go_cnf(self):
        """transform a region construct in a shape that is of structure AND (OR)"""
        return self.copy()

    def is_and(self):
        """is this region a conjunction of other regions"""
        return False

    def is_or(self):
        """is this region a disjunction of other regions"""
        return False

    def is_true(self):
        """is this region always true"""
        return False

    def is_false(self):
        """is this region always false"""
        return False

    def slice(self, feature, value):
        """slice the region along the given feature at the given value. This is used to create a new region that is a lower dimensional subset of the original region"""
        raise NotImplementedError("Region.slice() must be implemented by subclass {}.".format(self.__class__.__name__))

    def project(self, point, axis):
        """similar to slice, but works with non-axis aligned directions (axis) and an example (point) instead of an axis value"""
        raise NotImplementedError("Region.project() must be implemented by subclass {}.".format(self.__class__.__name__))

    def copy_apply(self, func):
        """copies the current structure, but applies the function "func" at each level. Good for making tree like changes"""
        raise NotImplementedError("Region.copy_apply() must be implemented by subclass {}.".format(self.__class__.__name__))

    def to_dict(self):
        """convert the region construct into a dictionary that can be used to reconstruct the construct"""
        raise NotImplementedError("Region.to_dict() must be implemented by subclass {}.".format(self.__class__.__name__))

    @classmethod
    def _init_from_dict(self, d):
        """initializes a region with the given dictionary. This is used to reconstruct the region from a dictionary"""
        raise NotImplementedError("Region._init_from_dict() must be implemented by subclass {}.".format(self.__class__.__name__))

    def count_floats(self):
        """counts the number of floating point values used to describe the polyra swarm"""
        raise NotImplementedError("Region.count_floats() must be implemented by subclass {}.".format(self.__class__.__name__))

    def _oned_or(self):
        """when given one dimensional data, this function will try to simplify the OR clauses. It will remove all but the two most extreme halfspaces, if they are not contradictory"""
        def func(obj):
            if not obj.is_or():return obj
            minn=None
            maxx=None
            for child in obj.children:
                if not child.is_base():return obj
                if not child.identify()=="Halfspace":return obj
                if not child.dimensionality()==1:return obj
                if child.A[0]<0:
                    if minn is None or child.b>minn.b:
                        minn=child
                else:
                    if maxx is None or child.b>maxx.b:
                        maxx=child
            conditions=[]
            if not minn is None:
                conditions.append(minn)
            if not maxx is None:
                conditions.append(maxx)
            if len(conditions)==2:
                if maxx.b>-minn.b:
                    return TRUE()
            ret= OR(*conditions).simplify()
            return ret

        return self.copy_apply(func)

    def _oned_and(self):
        """when given one dimensional data, this function will try to simplify the AND clauses. It will remove all but the two most extreme halfspaces, if they are not contradictory"""
        def func(obj):
            if not obj.is_and():return obj
            minn=None
            maxx=None
            for child in obj.children:
                if not child.is_base():return obj
                if not child.identify()=="Halfspace":return obj
                if not child.dimensionality()==1:return obj
                if child.A[0]<0:
                    if minn is None or child.b<minn.b:
                        minn=child
                else:
                    if maxx is None or child.b<maxx.b:
                        maxx=child
            conditions=[]
            if not minn is None:
                conditions.append(minn)
            if not maxx is None:
                conditions.append(maxx)
            if len(conditions)==2:
                if maxx.b<-minn.b:
                    return FALSE()
            ret= AND(*conditions).simplify()
            return ret

        return self.copy_apply(func)

    def _andor(self,do_tqdm=False):
        """given one dimensional data, this function will transform an construct in cnf format into one in dnf format, while avoiding the exponential explosion of terms by simplifying the construct iteratively for each additional term in the cnf format."""
        def func(obj):
            if not obj.is_and():return obj
            for child in obj.children:
                if not (child.is_or() or child.is_base()):return obj
            curr=None
            children=obj.children
            if do_tqdm:
                children=tqdm(children,desc="Rangefinding")
            for child in children:
                if curr is None:
                    curr=child
                    continue
                curr=AND(curr,child).go_dnf().simplify()
                #print(curr.tabstr())
                #print("applying and")
                curr=curr._oned_and()
                #print(curr.tabstr())
                #exit()

            return curr

        return self.copy_apply(func)

    def rangefinder(self,do_tqdm=False):
        """assumes that the dimensionality is 1, uses this to drastically simplify the region further"""

        self=self.simplify().go_cnf().simplify()
        self=self._oned_or().simplify()
        self=self._andor(do_tqdm=do_tqdm).simplify()
        return self

    def _range_random(self,rnd, count=1):
        """assumes the object is in (OR) AND form (dnf)
        For each OR clause, if there is one, calculate the length of the area
        randomly select one clause weighted by the area
        select a random point in that clause"""
        
        if self.is_false() or self.is_true():
            return None

        ors=[]
        if self.is_or():
            ors=self.children
        else:
            ors=[self]

        areas=[]
        for orr in ors:
            if orr.is_base():
                raise Exception("Found unbound area in range_random. Please add a border condition")
            else:
                if not orr.is_and():
                    print(orr.tabstr())
                assert orr.is_and(), "Found non-AND in range_random,{},{},{}".format(orr,orr.is_and(), orr.identify())
                rang=[None,None]
                for child in orr.children:
                    assert child.is_base()
                    if child.A[0]<0:
                        rang[0]=-child.b
                    else:
                        rang[1]=child.b
                areas.append(rang[1]-rang[0])
        sumarea=sum(areas)
        areas=[zw/sumarea for zw in areas]
        areas=np.array(areas).flatten()

        if count==1:
            which=rnd.choice(len(ors),p=[zw for zw in areas])
            orr=ors[which]
            rang=[None,None]
            for child in orr.children:
                if child.A[0]<0:
                    rang[0]=-child.b
                else:
                    rang[1]=child.b
            return rnd.uniform(rang[0],rang[1])
        else:
            whichs=rnd.choice(len(ors),p=[zw for zw in areas],size=count) 
            ret=[]
            for which in whichs:
                orr=ors[which]
                rang=[None,None]
                for child in orr.children:
                    if child.A[0]<0:
                        rang[0]=-child.b
                    else:
                        rang[1]=child.b
                ret.append(rnd.uniform(rang[0],rang[1]))
            return np.array(ret)

    def motio(self, pos, rnd):
        """tries to move a point pos into each axis to find a normal point. Weaker version of hit_and_run generation"""
        todo=[i for i in range(len(pos))]
        rnd.shuffle(todo)
        for i in todo:
            curr=self
            for j in range(len(pos))[::-1]:
                if i==j:continue
                curr=curr.slice(j,pos[j])
            curr=curr.rangefinder()
            newp=curr._range_random(rnd)
            if newp is None:continue
            pos[i]=newp
        return pos

    def _one_hit_and_run(self, pos, rnd, count=1):
        """given a point "pos" in the region, move it to another random point in the region"""
        dimension=len(pos)
        direction=rnd.randn(dimension)
        direction /= np.linalg.norm(direction)

        #switch to alpha space
        p=self.project(pos, direction)
        p=p.rangefinder()

        alpha=p._range_random(rnd, count)
        assert alpha is not None, "alpha is None. This should not happen when the initial point lies in the region"
        if count==1:
            poi=pos+alpha*direction
            return poi
        else:
            pois=[pos+alp*direction for alp in alpha]
            return np.array(pois)

    def hit_and_run(self, pos, steps=-1, pointsper=1, warmup=1, rnd=None, do_tqdm=True):
        """generates random samples of the shape, following the hit_and_run algorithm. If steps is -1, it will run indefinitely, else it will run for "steps" steps. If pointsper is larger than 1, it will generate pointsper samples in each step. Requires "pos" to be contained in the shapee, to guarantee that the algorithm will not fail. Technically might be possible to extend this, as we only require there to be a random variation of "pos" in a given random direction to be in the shape. Still this is not considered here. rnd represents the random object. If set to None, will use np.random. Warmup removes the first few samples, as they might be biased. With the standart parameter (warmup=1) it will only remove the initial position. if do_tqdm is set to True, it will show a progress bar, assuming that steps is not -1"""
        if rnd is None:
            rnd=np.random

        curr=np.copy(pos)
        assert np.all(self.predict(curr)), "Initial position is not in the shape. Can not use hit and run"
        tt=None
        if steps!=-1 and do_tqdm:
            tt=tqdm(total=steps,desc="Hit and run generation")
        while steps!=0:
            if steps>0:
                steps-=1
            if warmup>0:
                warmup-=1
            else:
                yield curr
            curr=self._one_hit_and_run(curr, rnd, count=pointsper)
            if not tt is None:
                tt.update(1)
            if pointsper>1:
                for i in range(len(curr)-1):
                    yield curr[i]
                curr=curr[-1]




    def _and_to_polytope(self):
        """converts an AND like construct into a classical polytope"""
        assert self.is_and() or self.is_base()
        As,bs=[],[]
        if self.is_base():
            A,b=self.to_polytope()
            As.append(A)
            bs.append(b)
        else:
            for child in self.children:
                A,b=child.to_polytope()
                As.append(A)
                bs.append(b)
        return np.array(As),np.array(bs)

    def _redundant_ands(self):
        """part of the lp abstraction"""
        def func(obj):
            if not obj.is_and():return obj
            for child in obj.children:
                if not child.is_base():return obj
            A,b=obj._and_to_polytope()
            if check_empty(A,b):
                return FALSE()
            A,b=simplify_polytope(A,b)
            return polytope_to_and(A,b)

        return self.copy_apply(func)

    def _puzzle_ands(self,maximum_error=0.001):
        """part of the lp abstraction"""
        def func(obj):
            if not obj.is_or():return obj
            for child in obj.children:
                if not (child.is_base() or child.is_and()):return obj

            As,bs=[],[]
            for child in obj.children:
                A,b=child._and_to_polytope()
                As.append(A)
                bs.append(b)

            Af,bf=[],[]
            while len(As)>0:
                A,b=As.pop(),bs.pop()
                broken=False
                for i in range(len(As))[::-1]:
                    merge=mergable_polytopes(A,b,As[i],bs[i],maximum_error=maximum_error)
                    if merge is None:continue
                    As.pop(i)
                    bs.pop(i)
                    A,b=merge
                    broken=True
                    break
                if broken:
                    As.append(A)
                    bs.append(b)
                    print("!!!!merged",len(As),len(Af),len(As)+len(Af))
                else:
                    Af.append(A)
                    bf.append(b)

            children=[]
            for A,b in zip(Af,bf):
                children.append(polytope_to_and(A,b))
            return OR(*children)



        return self.copy_apply(func)

    def _abstract_dnf(self,maximum_error=0.001,do_tqdm=False):
        """experiment on lp abstraction"""
        def func(obj):
            if not obj.is_and():return obj
            for child in obj.children:
                if not (child.is_or() or child.is_base()):return obj
            curr=None
            children=obj.children
            if do_tqdm:
                children=tqdm(children,desc="Abstracting")
            for child in children:
                if curr is None:
                    curr=child
                    continue
                curr=AND(curr,child).go_dnf().simplify()
                curr=curr._redundant_ands().simplify()
                #here could include _sample_redundant_ors() to work well
                curr=curr._puzzle_ands(maximum_error=maximum_error).simplify()

            return curr

        return self.copy_apply(func)

    def _sample_redundant_ands(self, normal, unlabeled):
        """part of the sample abstraction"""
        #probably a hybrid way would be best. But lets ignore this for now.
        def func(obj):
            if not obj.is_and():return obj
            for child in obj.children:
                if not child.is_base():return obj
            if check_empty_s(obj, unlabeled):
                return FALSE()
            obj=simplify_polytope_s(obj, unlabeled)
            return obj

        return self.copy_apply(func)

    def _sample_redudant_ors(self, normal, unlabeled):
        """part of the sample abstraction. searches for children of ors that are redundant. Meaning that including them does not alter the prediction of the model
        does not require the tree call because called directly on the or object"""
        if not self.is_or():return self
        #assert np.all(self.predict(normal)), "found situation where model is not correct on normal"#could be done differently to allow quantiles abstraction
        #kinda useless check. If not all are normal, just does nothing. Removed here for minor speedup
        children=self.children
        for i in range(len(children))[::-1]:
            without=OR(*[children[j] for j in range(len(children)) if j!=i])
            if not np.all(without.predict(normal)):
                continue
            children.pop(i)
        return OR(*children)

    def _sample_puzzle_ands(self, normal, unlabeled, maximum_error=0.001):
        """part of the sample abstraction"""
        def func(obj):
            if not obj.is_or():return obj
            for child in obj.children:
                if not (child.is_base() or child.is_and()):return obj

            Cs=[zw.copy() for zw in obj.children]

            Cf=[]

            while len(Cs)>0:
                C=Cs.pop()
                broken=False
                for i in range(len(Cs))[::-1]:
                    merge=mergable_polytopes_s(C,Cs[i],unlabeled,maximum_error=maximum_error)
                    if merge is None:continue
                    Cs.pop(i)
                    C=merge
                    broken=True
                    break
                if broken:
                    Cs.append(C)
                else:
                    Cf.append(C)

            return OR(*Cf)


        return self.copy_apply(func)

    def sample_abstraction(self, normal, unlabeled, maximum_error=0.001, do_tqdm=False):#todo:)
        """Abstraction code based on sampling. The alternative (_abstract_dnf) uses a similar setup but linear programing instead of sampling. It should thus scale better to high dim cases."""
        def func(obj):
            if not obj.is_and():return obj
            for child in obj.children:
                if not (child.is_or() or child.is_base()):return obj
            curr=None
            children=obj.children
            if do_tqdm:
                children=tqdm(children,desc="Abstracting")
            for child in children:
                if curr is None:
                    curr=child
                    continue
                curr=AND(curr,child).go_dnf().simplify()
                curr=curr._sample_redundant_ands(normal, unlabeled).simplify()
                curr=curr._sample_redudant_ors(normal, unlabeled).simplify()
                curr=curr._sample_puzzle_ands(normal, unlabeled, maximum_error=maximum_error).simplify()

            return curr

        return self.copy_apply(func)

    def __and__(self,other):
        return AND(self,other).simplify()

    def __or__(self,other):
        return OR(self,other).simplify()

    def __invert__(self):
        return NOT(self).simplify()

    @classmethod
    def from_dict(self, d):
        return from_dict(d)

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(self.to_dict(), indent=2))

    @classmethod 
    def load(self, filename):
        with open(filename, "r") as f:
            d=json.loads(f.read())
        return from_dict(d)


def polytope_to_and(A,b):
    children=[]
    for i in range(A.shape[0]):
        children.append(HALFSPACE(A[i],b[i]))
    return AND(*children)







classes={}
def register(cls):
    classes[cls.__name__]=cls
    return cls

def from_dict(d):
    typ=d["type"]
    if not typ in classes:
        raise Exception("Unknown type {} in from_dict".format(typ))
    return classes[typ]._init_from_dict(d)

def OR(*args):
    return classes["ROR"](*args)

def AND(*args):
    return classes["RAND"](*args)

def NOT(*args):
    return classes["RNOT"](*args)

def TRUE(*args):
    return classes["RTRUE"](*args)

def FALSE(*args):
    return classes["RFALSE"](*args)

def HALFSPACE(*args):
    return classes["Halfspace"](*args)




