# ELE2364 (reinforcement learning) support package

Package to support the deep reinforcement learning exercises of the
ELE2364 (reinforcement learning) course at PUC-Rio.

Copyright (c) 2024 Wouter Caarls
Parts copyright (c) 2020 Gabriel Nogueira (Talendar)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Introduction

This package provides the environments and approximators used in the
ELE2364 (reinforcement learning) course at PUC-Rio. 

To install, run

´´´
pip install ele2364
´´´

# Environments

The environments provided in `ele2364.environments` are:

- Pendulum (Pendulum-v1 from Gymnasium)
- Lander (LunarLander-v2 from Gymnasium)
- FlappyBird (FlappyBird-v0 by Gabriel Nogueira (Talendar))

# Networks

The networks provided in `ele2364.networks` are:

- V (state-value network)
- DQ (state-action value network with discrete actions)
- CQ (state-action value network with continuous actions)
- Mu (deterministic policy network)
- Pi (stochastic policy network)
