import numpy as np

def save_profile(file_name, point, domain='space'):
    data = np.load(file_name)
    t_full, C_full, Grid_Space = data["t_full"], data["C_full"], data["Grid_Space"]

    if domain == 'space':
        index = np.argmin(np.abs(Grid_Space - point))
        concentration = C_full[index, :]
        np.savetxt("Numerical_Evaluation.csv", np.column_stack((t_full, concentration)), delimiter=",")
        
    elif domain == 'time':
        index = np.argmin(np.abs(t_full - point))
        concentration = C_full[:, index]       
        np.savetxt("Numerical_Evaluation.csv", np.column_stack((Grid_Space, concentration)), delimiter=",")
        
    else:
        raise ValueError("Domain must be 'space' or 'time'")

