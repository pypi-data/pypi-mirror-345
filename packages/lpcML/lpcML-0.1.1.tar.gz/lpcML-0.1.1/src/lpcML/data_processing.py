from pickle import dump, load
import os
import numpy as np

import json
import pandas as pd 
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import  StandardScaler, MinMaxScaler

def columns_with_variation(df, tol=1e-15):
    '''
    Print columns in df with variation
    -------
    Input:
    ------
    df: pd.DataFrame
    '''
    col_std = []
    for col in df.select_dtypes(include=['float']).columns:
        if df[col].std() > tol:
            col_std.append(col)
    print('La lista de columnas en el df con std > 0:\n',col_std)

def import_lpc_data_from_csv(path, delimiter=','):
    '''
    Imports data into a pandas dataFrame from csv
    -------
    Input:
    ------
    path: path
        path where the data is stored
    delimiter: str
        delimiter between columns of csv
    Output:
    -------
    data: pandas dataframe 
        dataframe with data
    '''
    data = pd.read_csv(path, delimiter=delimiter)
    return data

def import_lpc_data_from_json(path_json):
    '''
    Imports data into a pandas dataFrame from json file
    -------
    Input:
    ------
    path: path
        path where the data is stored
    Output:
    -------
    data: pandas dataframe 
        dataframe with data
    '''
    with open(path_json, "r") as f: 
        data = json.load(f)
    # Flatten the nested structure
    flat_data = []
    for entry in data:
        flat_entry = {"ID": entry["ID"]}
        flat_entry.update(entry["sim_parameters"])
        flat_entry.update(entry["fom"])
        flat_entry.update(entry["IV_curve"])
        flat_data.append(flat_entry)
    df = pd.DataFrame(flat_data)
    df = df.sort_values(by="ID").reset_index(drop=True)
    return df


def data_to_input_output_tensors(data, input_param=None, output_param=None, verbosity=False):
    '''Preprocessing function that creates the input and output tensors
    ---------
    Input:
    -----
    data: pd.Dataframe
        hLPC optimization data
    input_param: list
        list of input parameters used to train the neural network, ['C1_up2_thick','C1_up2_dop','C1_down1_thick','C1_down1_dop','wavelength'] by default
    output_param: list
        list of output parameter(s) used to train the neural network, ['Eff'] by default
    verbosity: bool
        Print information about the final scaled tensors
    Output:
    ------
    X_list: torch.tensor
        Input tensor
    Y_list: torch.tensor
        Output tensor
    '''
    if not input_param:
        print('List of input parameters to feed the neural network not defined')
        input_param = ['C1_up2_thick','C1_up2_dop','C1_down1_thick','C1_down1_dop','wavelength']
    if not output_param:
        print('List of output parameter(s) to feed the neural network not defined')
        output_param = ['Eff']
    df_inputs = pd.DataFrame(data, columns=input_param)
    df_outputs = pd.DataFrame(data, columns=output_param)
    X_list, Y_list = df_inputs.to_numpy(), df_outputs.to_numpy()
    if verbosity:
        print("Total dimension (rank)\n","\tInput:", torch.tensor(X_list, dtype=torch.float32).ndim,"\tOutput:",torch.tensor(Y_list, dtype=torch.float32).ndim)
        print("Total size (shape)\n","\tInput:", torch.tensor(X_list, dtype=torch.float32).shape,"\tOutput:",torch.tensor(Y_list, dtype=torch.float32).shape)
        print("Total data type (dtype)\n","\tInput:", torch.tensor(X_list, dtype=torch.float32).dtype,"\tOutput:",torch.tensor(Y_list, dtype=torch.float32).dtype)
    return torch.tensor(X_list, dtype=torch.float32), torch.tensor(Y_list, dtype=torch.float32)


# def data_to_input_ouputIV_tensor(data, input_param, verbosity=False):
# TODO


def split_data(X, Y, test_split = 0.2, verbosity=False):
    '''Split data into train, validation and test subsets
    ---------
    Input:
    ------
    X: torch.tensor
        Input tensor
    Y: torch.tensor
        Output tensor
    test_split: float
        Percentage of subsets distribution, 20% test by default
    
    Output:
    -------
    X_train, Y_train: torch.tensor
        Input, Output train subsets
    X_val, Y_val: torch.tensor
        Input, Output validation subsets
    X_test, Y_test: torch.tensor
        Input, Output test subsets
    '''
    X, X_test, Y, Y_test = train_test_split(X, Y, test_size=test_split) 
    X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=test_split)
    if verbosity:
        print("Train size\n","\tInput:", X_train.shape,"\tOutput:",Y_train.shape)
        print("Validation size\n","\tInput:", X_val.shape,"\tOutput:",Y_val.shape)
        print("Test size\n","\tInput:", X_test.shape,"\tOutput:",Y_test.shape)
    return X_train, X_val, X_test, Y_train, Y_val, Y_test


def scale_input(X_train, X_val, X_test, scaler='standard'):
    '''Preprocessing function that normalize the input and output of the neural network and store the scalers
    ---------
    Input:
    -----
    data: pd.Dataframe
        hLPC optimization data
    scaler: str
        Choose the scaler to apply to the data, two options: StandardScaler 'standard' (default) and MinMaxScaler 'minmax'

    Output:
    ------
    X_train: torch.tensor
        Input train tensor
    X_val: torch.tensor
        Input validation tensor
    X_test: torch.tensor
        Input test tensor
    scaler_inputs: object
        Scaler object for inputs, standard by default
    '''
    if scaler == 'standard':
        scaler_inputs = StandardScaler()
    elif scaler == 'minmax':
        scaler_inputs = MinMaxScaler()
    X_train_scaled = scaler_inputs.fit_transform(X_train)
    X_val_scaled = scaler_inputs.transform(X_val)
    X_test_scaled = scaler_inputs.transform(X_test)
    directory =  'scaler_objects/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    dump(scaler_inputs, open(directory+'scaler_inputs.pkl', 'wb'))
    return torch.tensor(X_train_scaled, dtype=torch.float32), torch.tensor(X_val_scaled, dtype=torch.float32), torch.tensor(X_test_scaled, dtype=torch.float32), scaler_inputs

def scale_output(Y_train, Y_val, Y_test, scaler='standard'):
    '''Preprocessing function that normalize the input and output of the neural network and store the scalers
    ---------
    Input:
    -----
    data: pd.Dataframe
        hLPC optimization data
    scaler: str
        Choose the scaler to apply to the data, two options: StandardScaler 'standard' (default) and MinMaxScaler 'minmax'
    Output:
    ------
    Y_train: torch.tensor
        Output tensor
    Y_val: torch.tensor
        Output tensor
    Y_test: torch.tensor
        Output tensor
    scaler_outputs: object
        Scaler object for outputs, standard by default
    '''
    if scaler == 'standard':
        scaler_output = StandardScaler()
    elif scaler == 'minmax':
        scaler_output = MinMaxScaler()
    Y_train_scaled = scaler_output.fit_transform(Y_train)
    Y_val_scaled = scaler_output.transform(Y_val)
    Y_test_scaled = scaler_output.transform(Y_test)
    directory =  'scaler_objects/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    dump(scaler_output, open(directory+'scaler_output.pkl', 'wb'))
    return torch.tensor(Y_train_scaled, dtype=torch.float32), torch.tensor(Y_val_scaled, dtype=torch.float32), torch.tensor(Y_test_scaled, dtype=torch.float32), scaler_output

def scale_load(path):
    return load(open(path, 'rb'))