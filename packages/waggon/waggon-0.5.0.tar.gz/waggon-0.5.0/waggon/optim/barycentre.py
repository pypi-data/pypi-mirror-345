import gc
import numpy as np
from .surrogate import SurrogateOptimiser


class BarycentreSurrogateOptimiser(SurrogateOptimiser):
    def __init__(self, func, surr, acqf, **kwargs):
        super(BarycentreSurrogateOptimiser, self).__init__(func, surr, acqf, **kwargs)
    
    def get_lip(self, X, y):
        idx = np.array(np.meshgrid(np.arange(X.shape[0]), np.arange(X.shape[0]))).T.reshape(-1, 2)
        idx = idx[idx[:, 0] != idx[:, 1]]
        L = np.max(np.linalg.norm(y[idx[:, 0]] - y[idx[:, 1]], axis=-1) / np.linalg.norm(X[idx[:, 0]] - X[idx[:, 1]], axis=-1))
        return L

    def predict(self, X, y):

        self.surr.fit(X, y)
        self.acqf.L = self.get_lip(X, y)
        self.acqf.surr = []
        for epoch in range(self.surr.save_epoch, self.surr.n_epochs):
            self.acqf.surr.append(self.surr.load_model(epoch=epoch, return_model=True))
        
        x0 = None
        if self.num_opt_start == 'fmin':
            x0 = X[np.argmin(y)]
        
        next_x = self.numerical_search(x0=x0)

        del self.acqf.surr
        gc.collect()
        
        if next_x in X:
            next_x += np.random.normal(0, self.jitter, 1)
        
        return np.array([next_x])


class EnsembleBarycentreSurrogateOptimiser(SurrogateOptimiser):
    def __init__(self, func, surr, acqf, **kwargs):
        super(EnsembleBarycentreSurrogateOptimiser, self).__init__(func, surr, acqf, **kwargs)
        
        for surr in self.surr:
            surr.verbose   = self.verbose
        self.acqf.verbose   = self.verbose
    
    def get_lip(self, X, y):
        idx = np.array(np.meshgrid(np.arange(X.shape[0]), np.arange(X.shape[0]))).T.reshape(-1, 2)
        idx = idx[idx[:, 0] != idx[:, 1]]
        L = np.max(np.linalg.norm(y[idx[:, 0]] - y[idx[:, 1]], axis=-1) / np.linalg.norm(X[idx[:, 0]] - X[idx[:, 1]], axis=-1))
        return L

    def predict(self, X, y):
        
        surrs = []
        
        for surr in self.surr:
            surr.fit(X, y)
            surrs.append(surr)
        
        self.acqf.surr = surrs
        self.acqf.L = self.get_lip(X, y)
        
        x0 = None
        if self.num_opt_start == 'fmin':
            x0 = X[np.argmin(y)]
        
        next_x = self.numerical_search(x0=x0)
        
        del self.acqf.surr
        gc.collect()

        return np.array([next_x])
