#OR connector for two regions. For the sample to lie in the combined region, it has to lie in any of the child regions
import numpy as np
from .region import Region, register, OR, AND, TRUE, FALSE, from_dict
from tqdm import tqdm


class ROR(Region):
    def __init__(self,*children):

        self.children = list(children)

        super().__init__()

    def predict(self, samples):
        pred=np.array([child.predict(samples) for child in self.children])
        return np.any(pred,axis=0)

    def __str__(self):
        return " | ".join("("+str(child)+")" for child in self.children)

    def __repr__(self):
        return f"ROR({' ,'.join(repr(child) for child in self.children)})"

    def tabstr(self):
        return "OR\n"+self.tabify("\n".join(child.tabstr() for child in self.children))

    def simplify(self):
        children=[child.simplify() for child in self.children]
        q=[]
        for child in children:
            if child.is_false():
                continue
            if child.is_true():
                return child
            if isinstance(child, ROR):
                q.extend(child.children)
            else:
                q.append(child)
        children=q
        if len(children)==1:
            return children[0]
        if len(children)==0:
            return FALSE()
        return ROR(*children)

    def copy(self):
        return ROR(*[child.copy() for child in self.children])

    def identify(self):
        return "ROR"

    def go_cnf(self):
        #goal: And of Ors
        #so if there is an OR of AND, transform it
        #distributive law
        #a or (b and c) = (a or b) and (a or c)
        #OR of NOT and OR of OR should not exist thanks to simplify

        children=[child.go_cnf() for child in self.children]
        ands,rest=[],[]
        for child in children:
            if child.is_and():
                ands.append(child.children)
            else:
                rest.append(child)
        for zw in rest:
            ands.append([zw])

        ret=[]
        count=np.prod([len(a) for a in ands])
        tq=range(count) 
        if count>1000:
            print("Warning: large CNF, will take considerable time. Requires "+str(count)+" clauses")
            tq=tqdm(tq,total=count)
        for i in tq:
            clause=[]
            for a in ands:
                clause.append(a[i%len(a)])
                i//=len(a)
            ret.append(ROR(*clause))
        return AND(*ret).simplify()

    def go_dnf(self):
        return ROR(*[child.go_dnf() for child in self.children])

    def is_or(self):
        return True

    def slice(self, feature, value):
        return ROR(*[child.slice(feature,value) for child in self.children])

    def project(self, point, axis):
        return ROR(*[child.project(point,axis) for child in self.children])

    def copy_apply(self, func):
        return func(ROR(*[child.copy_apply(func) for child in self.children]))

    def to_dict(self):
        return {"type":"ROR", "children":[child.to_dict() for child in self.children]}

    @classmethod
    def _init_from_dict(self,d):
        children=[from_dict(child) for child in d["children"]]
        return ROR(*children)

    def count_floats(self):
        return sum(child.count_floats() for child in self.children)

register(ROR)
