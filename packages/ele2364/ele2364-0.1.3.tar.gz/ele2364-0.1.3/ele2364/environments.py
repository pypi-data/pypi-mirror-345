"""ELE2364 Deep Reinforcement Learning environments

CLASSES
    Pendulum     -- OpenAI Gym Pendulum-v1 environment.
    Lander       -- OpenAI Gym Lander-v2 environment.
    FlappyBird   -- Flappy Bird environment.
"""

from math import pi
import numpy as np
import matplotlib.pyplot as plt
import gymnasium
from .flappy_bird_gym import FlappyBirdEnvSimple
from .networks import V, DQ, CQ, Mu, Pi

class Environment():
    """OpenAI Gym Environment wrapper.

       METHODS
           reset   -- Reset environment.
           step    -- Step environment.
           render  -- Visualize environment.
           close   -- Close visualization.
           
       MEMBERS
           states  -- Number of state dimensions.
           actions -- Actions, or number of action dimensions.
    """
    def reset(self):
        """Reset environment to start state.
        
           obs = env.reset() returns the start state observation.
        """
        return self.env.reset()[0]
    
    def step(self, u):
        """Step environment.
        
           obs, r, terminal, truncated, info = env.step(u) takes
           action u and returns the next state observation, reward,
           whether the episode terminated or was truncated, and
           extra information.
        """
        observation, reward, terminal, truncated, info = self.env.step(u)
        return (observation, reward, terminal, truncated, info)
    
    def render(self):
        """Render environment.
        
           env.render() renders the current state of the
           environment in a separate window.
           
           NOTE
               You must call env.close() to close the window,
               before creating a new environment; otherwise
               the kernel may hang.
        """
        return self.env.render()
    
    def close(self):
        """Closes the rendering window."""
        return self.env.close()    

class Pendulum(Environment):
    """OpenAI Gym Pendulum-v1 environment."""
    def __init__(self, render_mode=None):
        """Creates a new Pendulum environment.
        
           EXAMPLE
               >>> env = Pendulum()
               >>> print(env.states)
               3
               >>> print(env.actions)
               [-2.  0.  2.]
        """
        self.env = gymnasium.make("Pendulum-v1", render_mode=render_mode)
        self.states = self.env.observation_space.shape[0]
        self.actions = np.linspace(self.env.action_space.low[0], self.env.action_space.high[0], 3)

    def step(self, u):
        return Environment.step(self, np.atleast_1d(u))

    def normalize(self, s):
        """Normalize state to unit circle.
        
           s = env.normalize(s) normalizes `s` such that its cosine-sine
           angle representation falls on the unit circle.
           
           EXAMPLE
               >>> env = Pendulum()
               >>> print(env.normalize([1, 1, 2])
               [0.70710678 0.70710678 2.        ]
        """
        
        single = len(np.asarray(s).shape) == 1
        
        s = np.atleast_2d(s)
        ang = np.arctan2(s[:,None,1], s[:,None,0])
        s = np.hstack((np.cos(ang), np.sin(ang), s[:,None,2]))
        
        if single:
            s = s[0]
            
        return s

    def plotlinear(self, w, theta, feature=None):
        """Plot value function and policy.
        
           plot(w, feature) plots the function approximated by 
           w^T feature(x) .
           
           plot(w, theta, feature) plots the functions approximated by 
           w^T * feature(x) and theta^T * feature(x) .
        """
        ac = True
        if feature is None:
            feature = theta
            ac = False
        
        p, v = np.meshgrid(np.linspace(-pi, pi, 64), np.linspace(-8, 8, 64))
        s = np.vstack((np.cos(p.flatten()), np.sin(p.flatten()), v.flatten())).T
        f = feature(s)
        c = np.reshape(np.dot(f, w), p.shape)
        
        if ac:
            a = np.reshape(np.dot(f, theta), p.shape)
        
            fig, axs = plt.subplots(1,2)
            fig.subplots_adjust(right=1.2)

            h = axs[0].contourf(p, v, c, 256)
            fig.colorbar(h, ax=axs[0])

            h = axs[1].contourf(p, v, a, 256)
            fig.colorbar(h, ax=axs[1])

            axs[0].set_title('Critic')
            axs[1].set_title('Actor')
        else:
            fig, ax = plt.subplots(1,1)
            h = ax.contourf(p, v, c, 256)
            fig.colorbar(h, ax=ax)
            
            ax.set_title('Approximator')
    
    def plotnetwork(self, network, value_network=None):
        """Plot network.

           plot(v) plots the value function of V network `v`.
           plot(dq) plots the value function and induced policy of DQ network `dq`.
           plot(mu) plots the policy of Mu network `mu`.
           plot(mu, cq) plots the policy of Mu network `mu` and value function of
           CQ network `cq` evaluated at the policy's actions.
           plot(pi) plots the policy of Pi network `pi`.
           plot(pi, v) plots the policy of Pi network `pi` and value function of
           V network `v`.
        """
        if network.sizes[0] != 3:
            raise ValueError("Network is not compatible with Pendulum environment ({network.sizes})")
            
        pp, vv = np.meshgrid(np.linspace(-np.pi,np.pi, 64), np.linspace(-8, 8, 64))
        obs = np.hstack((np.reshape(np.cos(pp), (pp.size, 1)),
                         np.reshape(np.sin(pp), (pp.size, 1)),
                         np.reshape(       vv , (vv.size, 1))))

        aval = np.linspace(-2, 2, 3)

        if isinstance(network, V):
            vf = np.reshape(network.forward(obs), pp.shape)

            fig, ax = plt.subplots()

            h = ax.contourf(pp, vv, vf, 256)
            fig.colorbar(h, ax=ax)
            ax.set_title('Value function')
        elif isinstance(network, DQ):
            qq = network.forward(obs)
            vf = np.reshape(np.amax(qq, axis=1), pp.shape)
            pl = np.vectorize(lambda x: aval[x])(np.reshape(np.argmax(qq, axis=1), pp.shape))

            fig, axs = plt.subplots(1,2)
            #fig.subplots_adjust(right=1.5)

            h = axs[0].contourf(pp, vv, vf, 256)
            fig.colorbar(h, ax=axs[0])
            h = axs[1].contourf(pp, vv, pl, 256)
            fig.colorbar(h, ax=axs[1])

            axs[0].set_title('Value function')
            axs[1].set_title('Policy')
        elif isinstance(network, Mu) or isinstance(network, Pi):
            if isinstance(network, Pi):
                act, _ = network.forward(obs)
            else:
                act = network.forward(obs)
            pl = np.reshape(act, pp.shape)
            
            if value_network is not None:
                fig, axs = plt.subplots(1,2)
                #fig.subplots_adjust(right=1.5)
                ax = axs[1]
                
                if isinstance(value_network, V):
                    vf = np.reshape(value_network.forward(obs), pp.shape)
                else:
                    vf = np.reshape(value_network.forward(obs, act), pp.shape)
                
                h = axs[0].contourf(pp, vv, vf, 256)
                fig.colorbar(h, ax=axs[0])
                axs[0].set_title('Value function')
            else:
                fig, ax = plt.subplots()
                
            h = ax.contourf(pp, vv, pl, 256)
            fig.colorbar(h, ax=ax)
            ax.set_title('Policy')
        else:
            raise ValueError("Input should be either V, DQ, CQ, Mu or Pi, not {}".format(type(network).__name__))

class Lander(Environment):
    """OpenAI Gym LunarLander-v2 environment."""
    def __init__(self):
        """Creates a new Lander environment.
                
           EXAMPLE
               >>> env = Lander()
               >>> print(env.states)
               8
               >>> print(env.actions)
               [0 1 2 3]
        """
        self.env = gymnasium.make("LunarLander-v2")
        self.states = self.env.observation_space.shape[0]
        self.actions = np.arange(self.env.action_space.n)

class FlappyBird(Environment):
    """FlappyBird-v0 environment."""
    def __init__(self):
        """Creates a new FlappyBird environment.
        
           EXAMPLE
               >>> env = FlappyBird()
               >>> print(env.states)
               3
               >>> print(env.actions)
               [0, 1]
        """
        self.env = gymnasium.make("FlappyBird-v0", render_mode='human')
        self.states = self.env.observation_space.shape[0]
        self.actions = [0, 1]

    def step(self, u):
        return Environment.step(self, np.atleast_1d(u))

    def plotnetwork(self, network):
        """Plot network.

           plot(dq) plots the value function and induced policy of DQ network `dq`
           at bird velocity 0.
        """
        if network.sizes[0] != 3 or network.sizes[-1] != 2:
            raise ValueError("Network is not compatible with FlappyBird environment")

        xx, yy = np.meshgrid(np.linspace(0, 2, 64), np.linspace(-0.5, 0.5, 64))
        vv = np.zeros((64, 64))
        obs = np.hstack((np.reshape(xx , (xx.size, 1)),
                         np.reshape(yy , (yy.size, 1)),
                         np.reshape(vv , (vv.size, 1))
                       ))

        aval = [0, 1] 

        qq = network(obs)
        vf = np.reshape(np.amax(qq, axis=1), xx.shape)
        pl = np.vectorize(lambda x: aval[x])(np.reshape(np.argmax(qq, axis=1), xx.shape))

        fig, axs = plt.subplots(1,2)
        fig.subplots_adjust(right=1)

        h = axs[0].contourf(xx, yy, vf, 256)
        fig.colorbar(h, ax=axs[0])
        h = axs[1].contourf(xx, yy, pl, 256)
        fig.colorbar(h, ax=axs[1])

        axs[0].set_title('Value function')
        axs[1].set_title('Policy')
