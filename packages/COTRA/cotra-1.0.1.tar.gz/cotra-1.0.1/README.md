# COntaminant TRAnsport code (COTRA)

This code is developed for academic purposes.  
It numerically solves the Adsorption-Dispersion Equation in one dimension (1D).  

## Installation
You can install the package by:  
```bash
pip install COTRA
```

## Functions

### Examples
You can find a complete example of all the features in the `showcase.py` file.

### List of functions

- `COTRA.run(Hydro_Dispersion, pore_velocity, porosity, bulk_density, Source_Time, Source_Intensity, Domain_Length, dx, Time_Span, dt, retardation, k_1, k_2)`  
  Solves the 1D Adsorption-Dispersion equation and saves the output as `.npz` files automatically.  

- `COTRA.CvS(files, *comments)`  
  Interactive plot of concentration profiles vs space at different times using a slider.  

- `COTRA.CvT(files, *comments)`  
  Interactive plot of concentration vs time at different positions using a slider.  

- `COTRA.animate(file_name)`  
  Creates an animation of the concentration profile evolving over time.  

- `COTRA.save_profile(file_name, point, domain='space')`  
  Exports the concentration profile either over time at a given space point or over space at a given time point, saving it into a CSV file.  

## Equation

The code solves the following coupled system:

$$
\frac{dC}{dt} = \frac{-v_p \frac{dC}{dx} + D \frac{d^2C}{dx^2} - S}{R}
$$

$$
\rho \frac{ds}{dt} = \dot{a} n C - \dot{d} \rho s
$$

Where:
- $C$= concentration in the fluid [g/L]  
- $s$= sorbed concentration [g/kg]  
- $v_p$= pore velocity [m/s]  
- $D$= hydrodynamic dispersion coefficient [m²/s]  
- $S$= source term  
- $R$= retardation factor  
- $n$= porosity [-]  
- $\rho$= bulk density [kg/L]  
- $\dot{a}$= adsorption rate
- $\dot{d}$= desorption rate  

The adsorption rate can be defined with two models:
- **Freundlich Model**:  
  $\dot{a} = k_1 \left( \dot{d} \frac{\rho}{n} \right) C^{\left( k_2 - 1\right)}$
- **Linear Model**:  
  $\dot{a} = k_1 \left( \dot{d} \frac{\rho}{n} \right)$

## Output
The solver automatically saves results in `.npz` format containing:
- `t_full`: full time array
- `C_full`: concentration over space and time
- `Grid_Space`: discretized spatial domain
- `Domain_Length`: total domain length
- `Source_Intensity`: intensity of the contaminant source

These files are used for further plotting, animation, and exporting data.

