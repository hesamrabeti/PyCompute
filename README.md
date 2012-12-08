PyCompute
=========
A project for small-scale distributed computing in Python.

PyCompute is designed to be a flexible and light-weight framework for performing distributed computation across a small set of computers. It uses a centralized task scheduling architecture to perform calculations.

An example of a use-case would be several computers in a house or a small business connected through a network.

Currently, PyCompute does not have any fault-tolerance implemented. As such, some human intervention will be required in case of hardware or software failure.

PyCompute executes Python code blindy in a non-virtualized cPython environment, as such, appropriate pre-cautions should be taken to guarantee that the code being executed is from a trusted source.

