import re
import math
import matplotlib.pyplot as plt
from torcheval.metrics.functional import mean_squared_error
import numpy as np

def prediction_versus_simulation_plot(simulation, prediction, r2, xlabel = None, ylabel = None, rms = None, storepath = None, figname = None):
    '''Plot for the comparison of the simulated versus predicted data with machine learning
    --------------------
    Parameters:
    ------
    simulation: list or torch.tensor
        Simulated data
    prediction: list or torch.tensor
        Predicted data
    r2: float
        Coefficient of determination between simulated and predicted data
    xlabel: str
        Text for the xlabel
    ylabel: str
        Text fot the ylabel
    rms: list 
        Root mean square errors in the prediction of each value
    storepath: str
        Path to store the plot, by default is stored in the execution directory
    figname: str
        File name of the stored plot, by default is prediction_vs_simulation.pdf
    '''
    fig, ax = plt.subplots()
    if rms:
        rms = mean_squared_error(simulation, prediction)**0.5
        plt.errorbar(simulation, prediction, fmt='.', yerr=rms, label='RMSE')
    else:
        plt.plot(simulation, prediction,'.',color='darkorange',markersize=15,alpha=0.8)
    plt.xlabel(xlabel,fontsize=20)
    plt.ylabel(ylabel,fontsize=20)
    plt.plot(simulation, simulation,'-', color='darkgrey')
    textstr0 = rf'$R^2$={r2}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
    plt.text(x=0.1,y=0.8, s=textstr0, transform=ax.transAxes, fontsize=20,
        verticalalignment='top', bbox=props)
    plt.locator_params(axis='x', nbins=6)
    plt.locator_params(axis='y', nbins=6)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    if figname:
        plt.savefig(figname, bbox_inches='tight')

def ml_input_versus_output_plot(X_train, X_val, X_test, Y_train, Y_val, Y_test, input_params_name, output_params_name, figname=None):
    '''Plot the simulated data that is used as input for the machine learning vs the output
    --------------------
    Parameters:
    ------
    data: pd.Dataframe
        hLPC optimization data
    input_params_name: list
        List of text for the input parameters
    output_params_name: list
        List of text for the output parameter
    figname: str
        File name of the stored plot
    '''
    FONT = 16
    LFONT = 14
    num_inputs = len(input_params_name)
    ncols = 3
    nrows = math.ceil(num_inputs / ncols)

    fig, axs = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axs = np.array(axs).reshape(-1)  # flatten axs in case it's 2D

    for i in range(num_inputs):
        ax = axs[i]
        ax.scatter(X_train[:, i], Y_train, color='blue', label='Train')
        ax.scatter(X_val[:, i], Y_val, color='red', label='Validation')
        ax.scatter(X_test[:, i], Y_test, color='green', label='Test')

        ax.set_xlabel(input_params_name[i], fontsize=FONT)
        if i % ncols == 0:  # First column
            ax.set_ylabel(output_params_name[0], fontsize=FONT)
        if 'dop' in input_params_name[i].lower():
            ax.set_xscale('log')
        ax.tick_params(axis="x", labelsize=LFONT)
        ax.tick_params(axis="y", labelsize=LFONT)

        # Optional: add log scale for specific inputs
        if "log" in input_params_name[i].lower():
            ax.set_xscale('log')

        ax.legend(fontsize=LFONT)

    # Turn off unused subplots
    for j in range(num_inputs, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    if figname is not None:
        plt.savefig(figname, bbox_inches='tight')
    else:
        plt.show()

# def ml_input_versus_output_plot(X_train, X_val, X_test, Y_train, Y_val, Y_test, input_params_name, output_params_name, figname = None):
#     '''Plot the simulated data that is used as input for the machine learning vs the output
#     --------------------
#     Parameters:
#     ------
#     data: pd.Dataframe
#         hLPC optimization data
#     input_params_name: list
#         List of text for the input parameters
#     output_params_name: list
#         List of text for the output parameter
#     figname: str
#         File name of the stored plot
#     '''

#     FONT = 16
#     LFONT = 14
#     fig, axs = plt.subplots(2, 2, figsize=(15, 10))
#     plt.subplots_adjust(hspace=0.25, wspace=0.05)
#     axs[0, 0].scatter(X_train[:,0], Y_train, color='blue', label='Train')
#     axs[0, 0].scatter(X_val[:,0], Y_val, color='red', label='Validation')
#     axs[0, 0].scatter(X_test[:,0], Y_test, color='green', label='Test')
#     axs[0, 0].set_xlabel(input_params_name[0], fontsize = FONT)
#     axs[0, 0].set_ylabel(output_params_name[0], fontsize = FONT)
#     axs[0, 0].tick_params(axis="x", labelsize = LFONT)
#     axs[0, 0].tick_params(axis="y", labelsize = LFONT)
#     # axs[0, 0].legend()
#     axs[1, 0].scatter(X_train[:,1], Y_train, color='blue', label='Train')
#     axs[1, 0].scatter(X_val[:,1], Y_val, color='red', label='Validation')
#     axs[1, 0].scatter(X_test[:,1], Y_test, color='green', label='Test')
#     axs[1, 0].set_xscale('log')
#     axs[1, 0].set_xlabel(input_params_name[1], fontsize = FONT)
#     axs[1, 0].set_ylabel(output_params_name[0], fontsize = FONT)
#     axs[1, 0].tick_params(axis="x", labelsize = LFONT)
#     axs[1, 0].tick_params(axis="y", labelsize = LFONT)
#     axs[1, 0].legend(fontsize = LFONT)
#     axs[0, 1].scatter(X_train[:,2], Y_train, color='blue', label='Train')
#     axs[0, 1].scatter(X_val[:,2], Y_val, color='red', label='Validation')
#     axs[0, 1].scatter(X_test[:,2], Y_test, color='green', label='Test')
#     axs[0, 1].set_xlabel(input_params_name[2], fontsize = FONT)
#     axs[0, 1].tick_params(axis="x", labelsize = LFONT)
#     axs[0, 1].tick_params(labelleft=False)
#     #axs[0, 1].legend()
#     axs[1, 1].scatter(X_train[:,3], Y_train, color='blue', label='Train')
#     axs[1, 1].scatter(X_val[:,3], Y_val, color='red', label='Validation')
#     axs[1, 1].scatter(X_test[:,3], Y_test, color='green', label='Test')
#     axs[1, 1].set_xscale('log')
#     axs[1, 1].set_xlabel(input_params_name[3], fontsize = FONT)
#     axs[1, 1].tick_params(axis="x", labelsize = LFONT)
#     axs[1, 1].tick_params(labelleft=False)
#     #axs[1, 1].legend()
#     if figname is not None:
#         plt.savefig(figname, bbox_inches='tight')

def prediction_versus_simulation_plot_colored(simulation, prediction, X_test, r2, xlabel = None, ylabel = None, input_params = None, input_params_name = None, figname = None):
    '''Plot for the comparison of the simulated versus predicted data with machine learning, subplots for each input parameter
    --------------------
    Parameters:
    ------
    simulation: list or torch.tensor
        Simulated data
    prediction: list or torch.tensor
        Predicted data
    X_test: torch.tensor
        Input test tensor
    r2: float
        Coefficient of determination between simulated and predicted data
    xlabel: str
        Text for the xlabel
    ylabel: str
        Text fot the ylabel
    input_params: list 
        List of identifiers for the input parameters
    input_params_name: list
        List of input parameter names with units
    figname: str
        File name of the stored plot
    '''

    for i in range(len(input_params)):
        fig, ax = plt.subplots()
        plt.xlabel(xlabel,fontsize=20)
        plt.ylabel(ylabel,fontsize=20)

        plt.plot(simulation, simulation,'-', color='darkgrey')

        plt.title(f'Dependent of {input_params_name[i]}', fontsize=20)

        x_diffent = sorted(set(X_test[:,i].tolist()))
        color_list = ['blue','green','red','purple','orange','brown','pink','gray','olive','cyan']
        for f_x_i,_ in enumerate(x_diffent):
            filter = X_test[:,i] == x_diffent[f_x_i]

            simulation_filter = simulation[filter]
            prediction_filter = prediction[filter]

            if 'cm' in input_params_name[i]:
                plt.plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=re.sub(r'e\+?([-\d]+)', r'$\\times$10$^{{\1}}$', f'{x_diffent[f_x_i]:.0e} cm$^{{-3}}$'))
            else:
                plt.plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=f'{1000*x_diffent[f_x_i]:3.0f} nm')


        legend = plt.legend(fontsize=10, title=f'R$^2$={r2}')
        legend.get_title().set_fontweight('bold')  # Set the title font to bold
        plt.locator_params(axis='x', nbins=6)
        plt.locator_params(axis='y', nbins=6)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        if figname is not None:
            figname2 = figname + str(i) + '.png'
            plt.savefig(figname2, bbox_inches='tight')


def prediction_versus_simulation_subplot_colored(simulation, prediction, X_test, r2, xlabel=None, ylabel=None, input_params=None, input_params_name=None, figname=None):
    FONT = 16
    LFONT = 14
    color_list = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive', 'cyan']

    n_inputs = X_test.shape[1]
    ncols = 3
    nrows = math.ceil(n_inputs / ncols)

    fig, axs = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows))
    axs = np.array(axs).reshape(-1)

    for i in range(n_inputs):
        ax = axs[i]
        ax.plot(simulation[:, 0].tolist(), simulation[:, 0].tolist(), '-', color='darkgrey')

        x_diffent = sorted(set(X_test[:, i].tolist()))
        for f_x_i, _ in enumerate(x_diffent):
            mask = X_test[:, i] == x_diffent[f_x_i]
            sim_filter = simulation[mask]
            pred_filter = prediction[mask]

            label = f'{1000*x_diffent[f_x_i]:.0f} nm' if 'nm' in input_params_name[i].lower() else \
                    re.sub(r'e\+?([-\d]+)', r'×10$^{\1}$', f'{x_diffent[f_x_i]:.0e}')

            ax.plot(sim_filter, pred_filter, '.', color=color_list[f_x_i % len(color_list)], markersize=15, alpha=0.8, label=label)

        ax.set_title(f'{input_params_name[i]}', fontsize=LFONT)
        ax.locator_params(axis='x', nbins=6)
        ax.locator_params(axis='y', nbins=6)

        if i % ncols == 0:
            ax.set_ylabel(ylabel, fontsize=FONT)
        else:
            ax.tick_params(labelleft=False)

        if i // ncols == nrows - 1:
            ax.set_xlabel(xlabel, fontsize=FONT)
        else:
            ax.tick_params(labelbottom=False)

        ax.tick_params(axis="x", labelsize=LFONT)
        ax.tick_params(axis="y", labelsize=LFONT)

        legend = ax.legend(fontsize=10, ncols=2, title=input_params_name[i])
        legend.get_title().set_fontweight('bold')

    # Desactivar ejes sobrantes
    for j in range(n_inputs, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    if figname:
        plt.savefig(figname, bbox_inches='tight')
    else:
        plt.show()

# def prediction_versus_simulation_subplot_colored(simulation, prediction, X_test, r2, xlabel = None, ylabel = None, input_params = None, input_params_name = None, figname = None):
#     '''Plot for the comparison of the simulated versus predicted data with machine learning, subplots for each input parameter
#     --------------------
#     Parameters:
#     ------
#     simulation: list or torch.tensor
#         Simulated data
#     prediction: list or torch.tensor
#         Predicted data
#     X_test: torch.tensor
#         Input test tensor
#     r2: float
#         Coefficient of determination between simulated and predicted data
#     xlabel: str
#         Text for the xlabel
#     ylabel: str
#         Text fot the ylabel
#     input_params: list 
#         List of identifiers for the input parameters
#     input_params_name: list
#         List of input parameter names with units
#     figname: str
#         File name of the stored plot
#     '''

#     FONT = 16
#     LFONT = 14
#     color_list = ['blue','green','red','purple','orange','brown','pink','gray','olive','cyan']

#     fig, axs = plt.subplots(2, 2, figsize=(15, 10))
#     fig.subplots_adjust(hspace=0)
#     fig.subplots_adjust(wspace=0)

#     # top left
#     axs[0, 0].plot(simulation[:,0].tolist(), simulation[:,0].tolist(),'-', color='darkgrey')
#     axs[0, 0].tick_params(labelbottom=False)

#     i = 0
#     x_diffent = sorted(set(X_test[:,i].tolist()))
#     for f_x_i,_ in enumerate(x_diffent):
#         filter = X_test[:,i] == x_diffent[f_x_i]

#         simulation_filter = simulation[filter]
#         prediction_filter = prediction[filter]

#         axs[0, 0].plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=f'{1000*x_diffent[f_x_i]:3.0f} nm')

#     # axs[0, 0].legend(fontsize=10, title=f'R$^2$={r2}', title_fontproperties={'weight':'bold'})
#     legend = axs[0, 0].legend(fontsize=10, title=f'{input_params_name[i]}', ncols=2)
#     legend.get_title().set_fontweight('bold')
#     axs[0, 0].locator_params(axis='x', nbins=6)
#     axs[0, 0].locator_params(axis='y', nbins=6)
#     # axs[0, 0].set_xlabel(xlabel, fontsize = FONT)
#     axs[0, 0].set_ylabel(ylabel, fontsize = FONT)
#     # axs[0, 0].tick_params(axis="x", labelsize = LFONT)
#     axs[0, 0].tick_params(axis="y", labelsize = LFONT)

#     # bottom left
#     axs[1, 0].plot(simulation[:,0].tolist(), simulation[:,0].tolist(),'-', color='darkgrey')

#     i = 1
#     x_diffent = sorted(set(X_test[:,i].tolist()))
#     for f_x_i,_ in enumerate(x_diffent):
#         filter = X_test[:,i] == x_diffent[f_x_i]

#         simulation_filter = simulation[filter]
#         prediction_filter = prediction[filter]

#         axs[1, 0].plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=re.sub(r'e\+?([-\d]+)', r'$\\times$10$^{{\1}}$', f'{x_diffent[f_x_i]:.0e} cm$^{{-3}}$'))

#     # axs[1, 0].legend(fontsize=10, title=f'R$^2$={r2}', title_fontproperties={'weight':'bold'})
#     legend = axs[1, 0].legend(fontsize=10, title=f'{input_params_name[i]}', ncols=2)
#     legend.get_title().set_fontweight('bold')
#     axs[1, 0].locator_params(axis='x', nbins=6)
#     axs[1, 0].locator_params(axis='y', nbins=6)
#     axs[1, 0].set_xlabel(xlabel, fontsize = FONT)
#     axs[1, 0].set_ylabel(ylabel, fontsize = FONT)
#     axs[1, 0].tick_params(axis="x", labelsize = LFONT)
#     axs[1, 0].tick_params(axis="y", labelsize = LFONT)

#     # top right
#     axs[0, 1].plot(simulation[:,0].tolist(), simulation[:,0].tolist(),'-', color='darkgrey')
#     axs[0, 1].tick_params(labelleft=False)

#     i = 2
#     x_diffent = sorted(set(X_test[:,i].tolist()))
#     for f_x_i,_ in enumerate(x_diffent):
#         filter = X_test[:,i] == x_diffent[f_x_i]

#         simulation_filter = simulation[filter]
#         prediction_filter = prediction[filter]

#         axs[0, 1].plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=f'{1000*x_diffent[f_x_i]:3.0f} nm')

#     # axs[0, 1].legend(fontsize=10, title=f'R$^2$={r2}', title_fontproperties={'weight':'bold'})
#     legend = axs[0, 1].legend(fontsize=10, title=f'{input_params_name[i]}', ncols=2)
#     legend.get_title().set_fontweight('bold')    
#     axs[0, 1].locator_params(axis='x', nbins=6)
#     axs[0, 1].locator_params(axis='y', nbins=6)
#     # axs[0, 1].set_xlabel(xlabel, fontsize = FONT)
#     # axs[0, 1].set_ylabel(ylabel, fontsize = FONT)
#     # axs[0, 1].tick_params(axis="x", labelsize = LFONT)
#     # axs[0, 1].tick_params(axis="y", labelsize = LFONT)

#     # bottom right
#     axs[1, 1].plot(simulation[:,0].tolist(), simulation[:,0].tolist(),'-', color='darkgrey')
#     axs[1, 1].tick_params(labelleft=False)

#     i = 3
#     x_diffent = sorted(set(X_test[:,i].tolist()))
#     for f_x_i,_ in enumerate(x_diffent):
#         filter = X_test[:,i] == x_diffent[f_x_i]

#         simulation_filter = simulation[filter]
#         prediction_filter = prediction[filter]

#         axs[1, 1].plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=re.sub(r'e\+?([-\d]+)', r'$\\times$10$^{{\1}}$', f'{x_diffent[f_x_i]:.0e} cm$^{{-3}}$'))

#     # axs[1, 1].legend(fontsize=10, title=f'R$^2$={r2}', title_fontproperties={'weight':'bold'})
#     legend = axs[1, 1].legend(fontsize=10, title=f'{input_params_name[i]}', ncols=2)
#     legend.get_title().set_fontweight('bold')
#     axs[1, 1].locator_params(axis='x', nbins=6)
#     axs[1, 1].locator_params(axis='y', nbins=6)
#     axs[1, 1].set_xlabel(xlabel, fontsize = FONT)
#     # axs[1, 1].set_ylabel(ylabel, fontsize = FONT)
#     axs[1, 1].tick_params(axis="x", labelsize = LFONT)
#     # axs[1, 1].tick_params(axis="y", labelsize = LFONT)
#     if figname:
#         plt.savefig(figname, bbox_inches='tight')

    
# # import re

# # simulation = simulated_values
# # prediction = predicted_values
# # r2 = round(r2_test,3)


# # for i in range(len(INPUT_PARAMS)):
# #     out_filename_2 = '/home/daniel/research/0_CDE/images/precision/2e4/Voc/SimPred_ML_hLPC_GaN_300K_1W_MIERDA_DE_ENRIQUE_' + str(i) + '.png'

# #     xlabel = OUTPUT_PARAMS_NAME2[0]
# #     ylabel = OUTPUT_PARAMS_NAME2[1]
# #     figname = out_filename_2

# #     fig, ax = plt.subplots()
# #     # plt.plot(simulation, prediction,'.',color='darkorange',markersize=15,alpha=0.8)
# #     plt.xlabel(xlabel,fontsize=20)
# #     plt.ylabel(ylabel,fontsize=20)

# #     plt.plot(simulation, simulation,'-', color='darkgrey')

# #     plt.title(f'Dependent of {INPUT_PARAMS_NAME[i]}', fontsize=20)

# #     x_diffent = sorted(set(X_test[:,i].tolist()))
# #     color_list = ['blue','green','red','purple','orange','brown','pink','gray','olive','cyan']
# #     for f_x_i,_ in enumerate(x_diffent):
# #         filter = X_test[:,i] == x_diffent[f_x_i]

# #         simulation_filter = simulation[filter]
# #         prediction_filter = prediction[filter]

# #         if 'cm' in INPUT_PARAMS_NAME[i]:
# #             plt.plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=re.sub(r'e\+?([-\d]+)', r'$\\times$10$^{{\1}}$', f'{x_diffent[f_x_i]:.0e} cm$^{{-3}}$'))
# #         else:
# #             plt.plot(simulation_filter, prediction_filter,'.',color=color_list[f_x_i],markersize=15,alpha=0.8, label=f'{1000*x_diffent[f_x_i]:3.0f} nm')



# #     plt.legend(fontsize=10, title=f'R$^2$={r2}', title_fontproperties={'weight':'bold'})
# #     # textstr0 = rf'$R^2$={r2}'
# #     # props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
# #     # plt.text(s=textstr0, transform=ax.transAxes, fontsize=20, bbox=props)
# #     plt.locator_params(axis='x', nbins=6)
# #     plt.locator_params(axis='y', nbins=6)
# #     plt.xticks(fontsize=20)
# #     plt.yticks(fontsize=20)
# #     plt.savefig(figname, bbox_inches='tight')
# #     plt.close()