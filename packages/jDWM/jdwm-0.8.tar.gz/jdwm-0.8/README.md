<a href="https://github.com/psf/black">
<img src=https://img.shields.io/badge/code%20style-black-000000.svg>
</a>

# jDWM

A Python implementation of the Dynamic Wake meandering (DWM) model.

# Documentation
Documentation is available at https://hawc2public.pages.windenergy.dtu.dk/jdwm/.
Key classes and functions are outlined below:

## jDWM.Wake.StaticWake
```python
class StaticWake(axial_induction_model="Joukowsky", viscosity_model="madsen", 
boundary_model="madsen", meandercompensator="none", **params):
```
### Parameters

**axial_induction_model : string, optional**  
Model used for defining the axial induction profile of the wake-generating turbine. Should be one of
- 'Constant': Constant axial induction over rotor. Uses Ct as an input.
- 'Joukowsky': Joukowsky rotor with tip and root loss. Uses Ct as an input. (Default)
- 'ThrustMatch': Same as Joukowsky rotor, but the rotor-averaged thrust is conserved.
- 'InductionMatch': Same as Joukowsky rotor, but the rotor-averaged axial induction is conserved.
- 'InductionMatch2': Same as InductionMatch, but uses axial induction as an input instead of Ct.
- 'UserInput': The user defines the axial induction profile.

**viscosity_model : string, optional**  
Model used for defining eddy viscosity. Should be one of
- 'IEC': Expansion as defined in IEC Standards.
- 'madsen':  Expansion as defined by Madsen et al. (Default)
- 'larsen': Expansion as defined by Larsen et al. 
- 'keck': Expansion as defined by Keck et al.

**boundary_model : string, optional**  
Pressure expansion model of the initial boundary condition. Should be one of:
- 'None': No expansion.
- 'Madsen': Expansion as defined by Madsen et al. (Default)
- 'Keck': Expansion as defined by Keck et al.
- 'IEC': Expansion as defined in IEC Standards.

**meandercompensator : string, optional**
Static meandering compensator to allow the static wake to take into account time averaged wake meandering. Should be one of:
- 'none' : No meander compensation. Suitable for dynamic simulations. (Default).
- 'Reinwardt': meander compensation as defined in an upcoming Torque paper. Suitable for static simulations.

# Requirements
jDWM requires Python 3.6+, some standard scientific modules (numpy, scipy, matplotlib).

# Installation
First clone this repository, then pip install.
```
git clone https://gitlab.windenergy.dtu.dk/jyli/jdwm.git
pip install jdwm
```

# Some cool plots
<img src="fig/003_ct.gif" width="1000">
<img src="fig/003_TI.gif" width="1000">
