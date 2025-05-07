import math
from time import time

import torch
from torch.utils.data import DataLoader
from sklearn.metrics import r2_score
from pytorch_lightning.callbacks import EarlyStopping
import pytorch_lightning as pl
from pytorch_lightning.utilities.model_summary import ModelSummary
import wandb
from . import model




class mlp_lpc:

    def __init__(self, config = None, num_epochs = 200, num_workers = 10, verbosity=False, wandb_project = None, min_delta = 1e-3, patience = 50):
        ''' Definition of model parameters
        -----------
        Input:
        ------
        config: dictionary
            Contains the key:value pairs for the neural network hyperparameters
        num_epochs: int
            Number of epochs, 200 by default as it is implemented the early stopping method
        verbosity: bool
            if true: prints training info
        num_workers: int
            Number of workers to split the loaders, by default 10
        wand_project: str
            Name of wandb project to visualize the training, validation and test metrics
        min_delta: float
            Loss funtion step for early stopping, by default 1e-3
        patience: int
            Number of epochs to improve the min_delta before stopping the training, by default 50
        '''
        self.config = config
        self.num_epochs = num_epochs
        self.verbosity = verbosity
        self.num_workers = num_workers
        self.wandb_project = wandb_project
        self.min_delta = min_delta
        self.patience = patience


    def train(self, X_train, X_val, Y_train, Y_val):
        '''Train and test process to calibrate the neural network and predict the I-V curves
        -----------
        Input:
        ------
        X_train: torch.tensor
            Input train subsets
        X_val: torch.tensor
            Input validation subsets
        Y_train: torch.tensor
            Output test subsets
         Output:
        -------
        - model: pytorch lightning object
            Calibrated neural network model'''
        if self.config is None:
            # Neural Network 1 hyperparameters
            self.config = {
            "layer_1": int(len(X_train[0])*2),
            "layer_2": int(len(X_train[0])*2),
            "end_layer":int(len(Y_train[0])),
            "lr": 1e-1,
            "momentum": 0.9,
            "batch_size": 128
            }
        if self.wandb_project:
            wandb.init(project=self.wandb_project, config = self.config)
        train_dataset = model.CustomDataset(data_in = X_train, data_out = Y_train)
        train_loader = DataLoader(dataset = train_dataset, batch_size = self.config["batch_size"], num_workers = self.num_workers)
        val_dataset = model.CustomDataset(data_in = X_val, data_out = Y_val)
        val_loader = DataLoader(dataset=val_dataset, batch_size = self.config["batch_size"], num_workers = self.num_workers)
        if self.verbosity == True:
            print("Dimension train dataset:", len(train_dataset))
            print("Dimension validation dataset:", len(val_dataset))
        early_stopping = EarlyStopping('val/loss',mode='min', min_delta = self.min_delta, patience = self.patience)
        start_time = time()
        self.model = model.mlp_hLPC(self.config) # Automates loops, hardware calls, model.train, model.eval and zero grad
        # print('\n\n\n', train_dataset.shape)
        # trainer = pl.Trainer(accelerator="cpu",max_epochs=self.num_epochs, log_every_n_steps = math.floor(len(X_train)/self.config["batch_size"]), callbacks=[early_stopping]) # Init Lightning trainer callbacks=[early_stopping]
        trainer = pl.Trainer(accelerator="cpu",max_epochs=self.num_epochs, log_every_n_steps = math.floor(len(X_train)/self.config["batch_size"])) # Init Lightning trainer callbacks=[early_stopping]
        trainer.fit(self.model, train_loader, val_loader)
        print(ModelSummary(self.model))

        if wandb.run is not None:
            wandb.finish()
        elapsed_time = round(time() - start_time,2)
        if self.verbosity == True:
            print('Trainer time:', elapsed_time)
            print('The defined hyperparmaters are:', self.config)


    def test(self, X_test, Y_test, scaler_output):
        with torch.no_grad():
            y_hat = self.model(X_test)

        pred = scaler_output.inverse_transform(y_hat.view(y_hat.size(0), -1))
        sim = scaler_output.inverse_transform(Y_test.view(Y_test.size(0), -1))

        # Compute per-output R²
        r2_scores = []
        for i in range(sim.shape[1]):
            r2_i = r2_score(sim[:, i], pred[:, i])
            r2_scores.append(r2_i)
            if self.verbosity:
                print(f'R² for output {i}: {r2_i:.4f}')
            if wandb.run is not None:
                wandb.log({f"test/r2_output_{i}": r2_i})

        return pred, sim, r2_scores

    def load_model(self, path):
        self.model = model.mlp_hLPC.load_from_checkpoint(path)

    def predict(self, X):
        with torch.no_grad():
            y_hat = self.model(X)
        return y_hat


# class mlp_lpc_iv:
    
#     def __init__(self, config=None, num_epochs=200, num_workers=10, verbosity=False, wandb_project=None, min_delta=1e-3, patience=50):
#         self.config = config
#         self.num_epochs = num_epochs
#         self.verbosity = verbosity
#         self.num_workers = num_workers
#         self.wandb_project = wandb_project
#         self.min_delta = min_delta
#         self.patience = patience

#     def train(self, X_train, X_val, Y_train, Y_val):
#         if self.config is None:
#             self.config = {
#                 "layer_1": int(len(X_train[0]) * 2),
#                 "layer_2": int(len(X_train[0]) * 2),
#                 "lr": 1e-1,
#                 "momentum": 0.9,
#                 "batch_size": 128,
#                 "output_dim": Y_train.shape[-1]  # D = dimensión de cada vector
#             }

#         if self.wandb_project:
#             wandb.init(project=self.wandb_project, config=self.config)

#         train_dataset = model.CustomDataset(data_in=X_train, data_out=Y_train)
#         train_loader = DataLoader(dataset=train_dataset, batch_size=self.config["batch_size"], num_workers=self.num_workers)
#         val_dataset = model.CustomDataset(data_in=X_val, data_out=Y_val)
#         val_loader = DataLoader(dataset=val_dataset, batch_size=self.config["batch_size"], num_workers=self.num_workers)

#         if self.verbosity:
#             print("Dimension train dataset:", len(train_dataset))
#             print("Dimension validation dataset:", len(val_dataset))

#         early_stopping = EarlyStopping('val/loss', mode='min', min_delta=self.min_delta, patience=self.patience)
#         start_time = time()
#         self.model = model.mlp_hLPC(self.config)  # Usa la nueva versión de mlp_hLPC con 2 vectores de salida

#         trainer = pl.Trainer(
#             accelerator="cpu",
#             max_epochs=self.num_epochs,
#             log_every_n_steps=math.floor(len(X_train) / self.config["batch_size"]),
#             callbacks=[early_stopping]
#         )
#         trainer.fit(self.model, train_loader, val_loader)
#         print(ModelSummary(self.model))

#         if wandb.run is not None:
#             wandb.finish()

#         elapsed_time = round(time() - start_time, 2)
#         if self.verbosity:
#             print('Trainer time:', elapsed_time)
#             print('The defined hyperparameters are:', self.config)

#     def test(self, X_test, Y_test, scaler_output):
#         with torch.no_grad():
#             y_hat = self.model(X_test)  # y_hat shape: [batch_size, 2, D]

#         # Reshape to 2D if scaler expects [batch_size, features]
#         pred = scaler_output.inverse_transform(y_hat.view(y_hat.size(0), -1))
#         sim = scaler_output.inverse_transform(Y_test.view(Y_test.size(0), -1))

#         r2 = r2_score(sim, pred)

#         if self.verbosity:
#             print('The R2 for the Eff:', r2)

#         return pred, sim, r2

#     def load_model(self, path):
#         self.model = model.mlp_hLPC.load_from_checkpoint(path)

#     def predict(self, X):
#         with torch.no_grad():
#             y_hat = self.model(X)
#         return y_hat
