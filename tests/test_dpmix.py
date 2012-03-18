'''
Created on Mar 15, 2012

@author: Andrew Cron
@author: Jacob Frelinger
'''
import sys
sys.path.append('../src')

import numpy as np
import numpy.random as npr
import pymc as pm

from dpmix import DPNormalMixture
from BEM import BEM_DPNormalMixture

import pylab


#-------------------------------------------------------------------------------
# Generate MV normal mixture

gen_mean = {
    0 : [0, 5],
    1 : [-5, 0],
    2 : [5,0]
}

gen_sd = {
    0 : [0.5, 0.5],
    1 : [.5, 1],
    2 : [1, .25]
}

gen_corr = {
    0 : 0.5,
    1 : -0.5,
    2 : 0
}

group_weights = [0.4, 0.3, 0.3]

def generate_data(n=1e5, k=2, ncomps=3, seed=1):
    npr.seed(seed)
    data_concat = []
    labels_concat = []

    for j in xrange(ncomps):
        mean = gen_mean[j]
        sd = gen_sd[j]
        corr = gen_corr[j]

        cov = np.empty((k, k))
        cov.fill(corr)
        cov[np.diag_indices(k)] = 1
        cov *= np.outer(sd, sd)

        num = int(n * group_weights[j])
        rvs = pm.rmv_normal_cov(mean, cov, size=num)

        data_concat.append(rvs)
        labels_concat.append(np.repeat(j, num))

    return (np.concatenate(labels_concat),
            np.concatenate(data_concat, axis=0))

def plot_2d_mixture(data, labels):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 10))
    colors = 'bgr'
    for j in np.unique(labels):
        x, y = data[labels == j].T
        plt.plot(x, y, '%s.' % colors[j], ms=2)

if __name__ == '__main__':
    from datetime import datetime
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--gpu", default=False)
    (options, args) = parser.parse_args()
    use_gpu = bool(options.gpu)

    N = int(1e4) # n data points per component
    K = 2 # ndim
    ncomps = 3 # n mixture components
    npr.seed(datetime.now().microsecond)
    true_labels, data = generate_data(n=N, k=K, ncomps=ncomps)
    data = data - data.mean(0)
    data = data/data.std(0)

    #import pdb
    #pdb.set_trace()
    mcmc = DPNormalMixture(data, ncomp=3, gpu=use_gpu)#, mu0=mu0)
    mcmc.sample(100,nburn=0)
    #pdb.set_trace()
    bem = BEM_DPNormalMixture(mcmc)
    bem.optimize(maxiter=200)
    #pdb.set_trace()
    ident_mcmc = DPNormalMixture(bem)
    ident_mcmc.sample(100, nburn=0, ident=False)
    #pdb.set_trace()
    print ident_mcmc.stick_weights
    mu = ident_mcmc.mu
    print mu[-1]
    print ident_mcmc.weights[-1]
    pylab.scatter(data[:,0], data[:,1], s=1, edgecolors='none')
    pylab.scatter(mu[:,:,0],mu[:,:,1], c='r')
    pylab.show()