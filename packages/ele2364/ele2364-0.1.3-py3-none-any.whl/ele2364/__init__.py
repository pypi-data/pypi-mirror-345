"""ELE2364 Deep Reinforcement Learning helper functions.

MODULES
    environments -- OpenAI gym environments.
    networks     -- PyTorch networks.

CLASSES
    Memory       -- Replay Memory.

FUNCTIONS
    rbfprojector -- Gaussian RBF projector factory.
"""

from math import pi
import numpy as np
import scipy.stats

def __gaussrbf(s, p, v, sigma):
    """Gaussian radial basis function activation.
    
       f = gaussrbf(s, p, v, sigma) returns the activation for the
       radial basis functions specified by (`p`, `v`, `sigma`) calculated at
       `s`. `p` is a list of position centers, `v` is a list of velocity centers,
       and `sigma` is the basis function width. The return value f is a vector
       with activations.
       
       `s` is a vector containing the state, or may be a matrix in which each
       row specifies a state. In that case, `f` is a matrix where each row
       contains the activation for a row in `s`.
    """

    s = np.atleast_2d(s)
    pd = np.arctan2(s[:, None, 1], s[:, None, 0]) - p.flatten()
    pd = abs((pd-pi)%(2*pi)-pi)

    dist = np.sqrt(pd**2 + ((s[:, None, 2] - v.flatten())/(8/pi))**2)
    return np.squeeze(scipy.stats.norm.pdf(dist, 0, sigma))

def rbfprojector(nbasis, sigma):
    """Returns function that projects states onto Gaussian radial basis function features.
    
       feature = rbfprojector(nbasis, sigma) returns a function
           f = feature(s)
       that projects a state `s` onto a Gaussian RBF feature vector `f`. `nbasis` is the number
       of basis functions per dimension, while `sigma` is their width.
       
       If `s` is a matrix where each row is a state, `f` is a matrix where each row
       contains the feature vector for a row of `s`.
       
       EXAMPLE
           >>> feature = rbfprojector(3, 2)
           >>> print(feature([0, 0, 0]))
           [0.01691614 0.05808858 0.05808858 0.19947114 0.01691614 0.05808858]
    """

    p, v = np.meshgrid(np.linspace(-pi, pi-(2*pi)/(nbasis-1), nbasis-1), np.linspace(-8, 8, nbasis))
    return lambda x: __gaussrbf(x, p, v, sigma)

class Memory:
    """Replay memory
       
       METHODS
           add    -- Add transition to memory.
           sample -- Sample minibatch from memory.
    """
    def __init__(self, state_dims, action_dims, size=1000000):
        """Creates a new replay memory.
        
           Memory(state_dims, action_dims) creates a new replay memory for storing
           transitions with `state_dims` observation dimensions and `action_dims`
           action dimensions. It can store 1000000 transitions.
           
           Memory(state_dims, action_dims, size) additionally specifies how many
           transitions can be stored.
        """

        self.s = np.ndarray([size, state_dims])
        self.a = np.ndarray([size, action_dims])
        self.r = np.ndarray([size, 1])
        self.sp = np.ndarray([size, state_dims])
        self.terminal = np.ndarray([size, 1])
        self.v = np.ndarray([size, 1])
        self.logp = np.ndarray([size, 1])
        self.adv = np.ndarray([size, 1])
        self.rtg = np.ndarray([size, 1])
        self.i = 0
        self.n = 0
        self.size = size
    
    def __len__(self):
        """Returns the number of transitions currently stored in the memory."""

        return self.n
    
    def add(self, s, a, r, sp, terminal, v=0, logp=0):
        """Adds a transition to the replay memory.
        
           Memory.add(s, a, r, sp, terminal) adds a new transition to the
           replay memory starting in state `s`, taking action `a`,
           receiving reward `r` and ending up in state `sp`. `terminal`
           specifies whether the episode finished at terminal absorbing
           state `sp`.

           Memory.add(s, a, r, sp, terminal, v, logp) additionally records
           the value of state s and log-probability of taking action a.
        """

        self.s[self.i, :] = s
        self.a[self.i, :] = a
        self.r[self.i, :] = r
        self.sp[self.i, :] = sp
        self.terminal[self.i, :] = terminal
        self.v[self.i, :] = v
        self.logp[self.i, :] = logp
        
        self.i = (self.i + 1) % self.size
        if self.n < self.size:
            self.n += 1
    
    def sample(self, size):
        """Get random minibatch from memory.
        
        s, a, r, sp, done = Memory.sample(batch) samples a random
        minibatch of `size` transitions from the replay memory. All
        returned variables are vectors of length `size`.
        """

        idx = np.random.randint(0, self.n, size)

        return self.s[idx], self.a[idx], self.r[idx], self.sp[idx], self.terminal[idx]
        
    def reset(self):
        """Reset memory."""

        self.i = 0
        self.n = 0
