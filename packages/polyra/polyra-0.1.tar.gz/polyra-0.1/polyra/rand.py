#AND connector for two regions. For the sample to lie in the combined region, it has to lie in each of the child regions
import numpy as np
from .region import Region, register, OR, AND, TRUE, FALSE, from_dict
from tqdm import tqdm

class RAND(Region):
    def __init__(self,*children):

        self.children = list(children)

        super().__init__()

    def predict(self, samples):
        pred=np.array([child.predict(samples) for child in self.children])
        return np.all(pred,axis=0)

    def fraction(self, samples):
        pred=np.array([child.predict(samples) for child in self.children])
        return np.mean(pred,axis=0)

    def __str__(self):
        return " & ".join("("+str(child)+")" for child in self.children)

    def __repr__(self):
        return f"RAND({' ,'.join(repr(child) for child in self.children)})"

    def tabstr(self):
        return "AND\n"+self.tabify("\n".join(child.tabstr() for child in self.children))

    def count_floats(self):
        return sum([child.count_floats() for child in self.children])

    def simplify(self):
        children=[child.simplify() for child in self.children]
        q=[]
        for child in children:
            if child.is_true():
                continue
            if child.is_false():
                return child
            if isinstance(child, RAND):
                q.extend(child.children)
            else:
                q.append(child)
        children=q
        if len(children)==1:
            return children[0]
        if len(children)==0:
            return TRUE()
        return RAND(*children)

    def copy(self):
        return RAND(*[child.copy() for child in self.children])

    def identify(self):
        return "RAND"

    def go_cnf(self):
        return RAND(*[child.go_cnf() for child in self.children])

    def go_dnf(self):
        #goal: OR of ANDs
        #so if there is an AND of OR, transform it
        #distributive law
        #a and (b or c) = (a and b) or (a and c)
        #AND of NOT and AND of OR should not exist thanks to simplify

        children=[child.go_dnf() for child in self.children]
        ors,rest=[],[]
        for child in children:
            if child.is_or():
                ors.append(child.children)
            else:
                rest.append(child)
        for zw in rest:
            ors.append([zw])

        ret=[]
        count=np.prod([len(a) for a in ors])
        tq=range(count)
        if count>1000:
            print("Warning: large DNF, will take considerable time. Requires "+str(count)+" clauses")
            tq=tqdm(tq,total=count)
        for i in tq:
            clause=[]
            for a in ors:
                clause.append(a[i%len(a)])
                i//=len(a)
            ret.append(RAND(*clause))
        return OR(*ret).simplify()

    def is_and(self):
        return True

    def slice(self, feature, value):
        return RAND(*[child.slice(feature,value) for child in self.children])

    def project(self, point, axis):
        return RAND(*[child.project(point,axis) for child in self.children])

    def copy_apply(self, func):
        return func(RAND(*[child.copy_apply(func) for child in self.children]))
    
    def to_dict(self):
        return {"type": "RAND", "children": [child.to_dict() for child in self.children]}

    @classmethod
    def _init_from_dict(self,d):
        children=[from_dict(child) for child in d["children"]]
        return RAND(*children)

register(RAND)


