import torch, os, sys
torch.manual_seed(0) 
from trialbench.dataset import *

import warnings
warnings.filterwarnings("ignore")

def load_data(task, phase, ):
    '''
    Input:
        task: str, name of the dataset
        phase: str, phase of the clinical trial (e.g., "Phase 1", "Phase 2", "Phase 3", "Phase 4")
    Output: [train_loader, valid_loader, test_loader, num_classes, tabular_input_dim
        dataloaders:  tuple, containing train_loader, valid_loader, test_loader
        tabular_input_dim: int, number of features
    '''
    if task == 'mortality_rate':
        return mortality_rate(phase)
    elif task == 'serious_adverse_rate':
        return serious_adverse_rate(phase)
    elif task == 'patient_dropout_rate':
        return patient_dropout_rate(phase)
    elif task == 'duration':
        return duration(phase)
    elif task == 'outcome':
        return outcome(phase)
    elif task == 'failure_reason':
        return failure_reason(phase) 
    elif task == 'serious_adverse_rate_yn':
        return serious_adverse_rate_yn(phase)
    elif task == 'patient_dropout_rate_yn':
        return patient_dropout_rate_yn(phase)
    elif task == 'mortality_rate_yn':
        return mortality_rate_yn(phase)
    elif task == 'dose':
        return dose(phase)
    elif task == 'dose_cls':
        return dose_cls(phase)

def load_model():
    pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <task> <phase>")
        sys.exit(1)

    task = sys.argv[1]
    phase = sys.argv[2]

    train_loader, valid_loader, test_loader, num_classes, tabular_input_dim = load_data(task, phase)
    print(f"train_loader: {len(train_loader)}")
    print(f"num_classes: {num_classes}, tabular_input_dim: {tabular_input_dim}")
