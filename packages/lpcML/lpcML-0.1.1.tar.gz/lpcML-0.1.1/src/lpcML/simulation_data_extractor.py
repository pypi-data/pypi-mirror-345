from pathlib import Path
import json
import pandas as pd
import re

def extract_design_parameters(filepath: Path):
    """
    Extaction of simulation parameters from .in file
    ------
    Input:
    ------
    filepath: path
        Path of the silvaco .in simulation file
    ------
    Output:
    ------
    design_params: dict
        dictionary with the simulation initial parameters
    """
    design_params = {}
    
    with open(filepath, 'r') as f:
        data = f.readlines()

    # Join the remaining lines into a single string to extract values
    data = ''.join(data)

    # Regex pattern to capture the 'set <parameter_name> = <value>' structure
    pattern = re.compile(r'set\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|\d+)')

    # Find all matches and add to the dictionary
    matches = re.findall(pattern, data)
    
    # # Only add parameters until 'temperature' (included)
    for label, value in matches:
    #     if label == "temperature":
    #         design_params[label] = float(value)
    #         break
        design_params[label] = float(value)

    return design_params

def extract_IV_curves(filepath):
    """
    Extaction of simulated IV curve of the LPCs
    ------
    Input:
    ------
    filepath: path
        Path of the datos_curva_IV.dat file
        ------
    Output:
    ------
    Dictionary with the IV curves of the LPC simulation
    """
    df = pd.read_csv(filepath, skiprows=3, delimiter=' ')
    return {
        "V [V]": df.iloc[:, 0].tolist(),
        "I [A]": df.iloc[:, 1].tolist()
    }

def extract_fom(filepath):
    """
    Extaction of figures of merit 'fom' of the LPC simulation
    ------
    Input:
    ------
    filepath: path
        Path of the results.dat file
        ------
    Output:
    ------
    magnitudes: dictionary
        label key pairs of each resulting magnitude
    """
    magnitudes = {}
    with open(filepath, 'r') as f:
        data = f.readlines()

    # Skip the first two rows
    data = data[2:]

    # Join the remaining lines into a single string to extract values
    data = ''.join(data)


    # Regex pattern to capture labels and their values
    pattern = re.compile(r'([a-zA-Z0-9_()\/\-\+]+(?:\([^\)]*\))?)\s?=\s?([+-]?\d*\.\d+e?[+-]?\d*|\d+\.?\d*)')
    
    # Find all matches and add to the dictionary
    matches = re.findall(pattern, data)
    for label, value in matches:
        magnitudes[label] = float(value)  # Store as float for numerical operations

    return magnitudes

def collect_data_to_dictionary(root_path):
    """
    Collection of all simulation data into a global dictionary
    ------
    Input:
    ------
    rootpath: path
        Path of the simulaton repository
    ------
    Output:
    ------
    collected: dictionary
        Dictionary with the all the desired data to store
    """
    root_path = Path(root_path)
    collected = []
    # Iterate through all folders
    for sim_folder in root_path.glob("*/"):  # Loop over each subfolder (simulation folder)
        data_dict = {}
        in_files = list(sim_folder.glob("*_optz.in"))
        in_file = in_files[0]
        dat_files = list(sim_folder.rglob("datos_curva_IV.dat"))
        dat_file = dat_files[0]
        result_files = list(sim_folder.glob("results.dat"))
        result_file = result_files[0]
        # collected[sim_folder]['iv_curve'] = extract_IV_curves(dat_files)
        idf = 'ID_'+str(sim_folder).split('/')[-1]
        data_dict['ID'] = idf
        data_dict['sim_parameters'] = extract_design_parameters(in_file)
        data_dict['fom'] = extract_fom(result_file)
        data_dict['IV_curve'] = extract_IV_curves(dat_file)
        collected.append(data_dict)
    return collected

def save_dict_to_json(data: dict, filename: str, indent: int = 4) -> None:
    """
    Function to store the results into a json
    ------
    Input:
    ------
    data: list
        list of dictionary with the simulation data
    filename: path
        path with the desired output file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=indent)
        print(f"Dictionary saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving dictionary to {filename}: {e}")