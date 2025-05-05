#Base class for the learning of regions.
import numpy as np

from .region import Region, from_dict

from .halfspace import Halfspace
from .borderspace import Borderspace

from .rand import RAND
from .ror import ROR
from .rnot import RNOT

from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, to_rgba, BoundaryNorm
import json

class Polyra():

    def __init__(self,Adim=2,Bdim=2,subsample=0.0, quantile=0.0,extend=0.0,minpoi=1, epsilon=1e-8, **kwargs):
        """
        Polyra is a class for learning regions in a arbitrary-dimensional space. A few parameters control how the regions are learned.
        Adim=2: Conditions of the "If" polytope. If this value is equal to the dimension of the data+1, it is guaranteed that every shape can be learned. Generally: A higher Adim means smaller and more detailed regions.
        Bdim=2: Conditions of the "Then" polytope. This value does not affect the quality much, but is a speed-up.
        subsample=0.0: Allows for subsampling the data. Every submodel only sees 1-subsample of available datapoints.
        quantile=0.0: If this value is equal to 0, the model will learn the maximum and minimum of a distribution. If it is greater than 0, the model will learn the quantile of the distribution.
        extend=0.0: If this value is greater than 0, the model will extend the learned region by a extend*100%.
        minpoi=1: Minimum number of points required in the learned "If" polytopes. The higher this value becomes, the more convex the learned shape.
        epsilon=1e-8: Numerical safety constant.
        """
        self.learned=False
        self.dim=None

        self.Adim=Adim
        self.Bdim=Bdim
        self.subsample=subsample
        self.quantile=quantile
        self.extend=extend
        self.minpoi=minpoi
        self.epsilon=epsilon

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        dic={"Adim":self.Adim,"Bdim":self.Bdim,"subsample":self.subsample,"quantile":self.quantile,"extend":self.extend,"minpoi":self.minpoi,"epsilon":self.epsilon}
        if self.dim is not None:
            dic["dim"]=self.dim
        dic["learned"]=self.learned
        if self.learned:
            dic["model"]=self.model.to_dict()
        return dic

    @classmethod
    def _init_from_dict(self,d):
        p=Polyra(**d)
        if hasattr(p,"model"):
            p.model=Region.from_dict(d["model"])
        return p

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(self, filename):
        with open(filename, 'r') as f:
            d=json.loads(f.read())
            if "learned" in d:
                return Polyra._init_from_dict(d)
            else:
                return from_dict(d)

    def _learn_one(self, data) -> Region:
        n=data.shape[0]

        M=np.random.normal(0,1,(self.dim,self.Adim))
        #(dim,Adim)
        O=np.random.normal(0,1,(self.dim,self.Bdim))
        #(dim,Bdim)

        #data: (n,dim)
        p=np.dot(data,M)
        #(n,dim)*(dim,Adim) -> (n,Adim)
        b=np.zeros((self.Adim,))
        b[0]=np.random.uniform(np.min(p[:,0],axis=0),np.max(p[:,0],axis=0))

        masks=np.ones((n,),dtype=bool)

        if self.subsample>0:
            #set subsample fraction of masks to false
            #deterministic amount
            masks[np.random.choice(n,int(n*self.subsample),replace=False)]=False
            #random amount
            #masks=np.logical_and(masks,np.random.rand(n)<self.subsample)

        masks=np.logical_and(masks,p[:,0]<b[0])
        if not np.any(masks):return None
        for i in range(1,self.Adim):
            mn,mx=np.min(p[:,i][masks],axis=0),np.max(p[:,i][masks],axis=0)
            b[i]=np.random.uniform(mn,mx)
            masks=np.logical_and(masks,p[:,i]<b[i])
            if not np.any(masks):return None

        op=np.dot(data,O)
        #(n,dim)*(dim,Bdim) -> (n,Bdim)

        count=np.sum(masks)
        if count<self.minpoi:
            return None

        if self.quantile>0:
            arrmn=np.quantile(op[masks],self.quantile,axis=0)
            arrmx=np.quantile(op[masks],1-self.quantile,axis=0)
        else:
            arrmn=np.min(op[masks],axis=0)-self.epsilon
            arrmx=np.max(op[masks],axis=0)+self.epsilon

        if self.extend!=0.0:
            delta=(arrmx-arrmn)*self.extend/2
            arrmn-=delta
            arrmx+=delta

        inp=[]
        for i in range(self.Adim):
            inp.append(Halfspace(M[:,i],b[i]))
        inp=RAND(*inp)

        outp=[]
        for i in range(self.Bdim):
            outp.append(Halfspace(O[:,i],arrmx[i]))
            outp.append(Halfspace(-O[:,i],-arrmn[i]))
        outp=RAND(*outp)

        return ROR(RNOT(inp),outp).simplify()


    def learn(self,data, count=1000, do_tqdm=True):

        assert len(data.shape)==2, "Data must be a 2D array, got shape {}".format(data.shape)

        dim=int(data.shape[1])
        if not self.dim is None:
            assert self.dim==dim, "Data dimension must be {}, got {}".format(self.dim,dim)
        else:
            self.dim=dim

        q=None
        if do_tqdm:
            q=tqdm(range(count), desc='Learning')

        ret=[]
        while len(ret)<count:
            zw=self._learn_one(data)
            if zw is not None:
                ret.append(zw)
                if not q is None:
                    q.update(1)

        self.model=RAND(*ret)

        self.learned=True

        return self.model

    def add_box(self, mn, mx, dim):
        if hasattr(mn,"__len__"):
            mn=np.array(mn)
            assert len(mn)==dim, "Minimum box coordinates must have dimension {}, got {}".format(dim,len(mn))
        else:
            mn=np.full((dim,),mn)
        if hasattr(mx,"__len__"):
            mx=np.array(mx)
            assert len(mx)==dim, "Maximum box coordinates must have dimension {}, got {}".format(dim,len(mx))
        else:
            mx=np.full((dim,),mx)

        eye=np.eye(dim)

        conditions=[]
        for i in range(dim):
            conditions.append(Halfspace(eye[i],mx[i]))
            conditions.append(Halfspace(-eye[i],-mn[i]))

        if self.model is None:
            self.model=RAND(*conditions)
            self.learned=True #kinda at least, you are able to make predictions
        else:
            self.model=RAND(self.model,*conditions)

        return self.model

    def predict(self, data):
        assert self.learned, "Predicting samples requires first training the polyra model"
        return self.model.predict(data)

    def fraction(self, data):
        assert self.learned, "Calculating fraction requires first training the polyra model"
        return self.model.fraction(data)

    def even_draw(self,*args,mn=0.0,mx=1.0,per_dim=100,c=None,method="img",boolean=True,**kwargs):
        if c is None:
            if boolean:
                c="red"
            else:
                c="hot"
        if hasattr(mn,"__len__"):
            mn=np.array(mn)
            assert len(mn)==2, "Minimum box coordinates must have dimension {}, got {}".format(2,len(mn))
        else:
            mn=np.full((2,),mn)
        if hasattr(mx,"__len__"):
            mx=np.array(mx)
            assert len(mx)==2, "Maximum box coordinates must have dimension {}, got {}".format(2,len(mx))
        else:
            mx=np.full((2,),mx)
        if hasattr(per_dim,"__len__"):
            per_dim=np.array(per_dim)
            assert len(per_dim)==2, "Minimum box coordinates must have dimension {}, got {}".format(2,len(per_dim))
        else:
            per_dim=np.full((2,),per_dim)
        xs=[np.linspace(mn[0],mx[0],per_dim[0]),np.linspace(mn[1],mx[1],per_dim[1])]
        x=np.meshgrid(xs[0],xs[1])
        x=np.stack(x,axis=-1).reshape((-1,2))
        if boolean:
            y=self.predict(x)
        else:
            y=self.fraction(x)
        if method=="cut":
            x=x[y==1.0]
            plt.scatter(x[:,0],x[:,1],*args,c=c,**kwargs)
        elif method=="img":
            yr=y.reshape((per_dim[0],per_dim[1]))
            norm=None
            if boolean:
                cmap=ListedColormap([to_rgba("white",alpha=0),to_rgba(c,alpha=1)])
            elif type(c) is tuple:
                cmap=ListedColormap([to_rgba("white",alpha=0),to_rgba(c[0],alpha=1)])
                norm=BoundaryNorm([0,c[1],1],ncolors=cmap.N)
            else:
                cmap=c
                print("setting cmap to",c)
            plt.imshow(yr,extent=(mn[0],mx[0],mn[1],mx[1]),cmap=cmap,norm=norm,origin="lower",**kwargs)
        else:
            plt.scatter(x[:,0],x[:,1],*args,c=y,**kwargs)
        return x
    draw=even_draw


