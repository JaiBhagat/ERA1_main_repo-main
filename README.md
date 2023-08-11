# Main Repository

The main repository holds essential classes and functions utilized across multiple notebooks.

## Key Files & Directories:

### [main.py]
This file encapsulates several functions, including:
- `train`: Training the model with the training dataset.
- `test`: Evaluating the model's performance on the test dataset.
- `fit_model`: Executes the model while managing elements like optimization, scheduler, epochs count, and the L1 lambda.

### [utils.py]
This utility file consists of:
- **Class cifar_ds10**: A class for loading the CIFAR10 data.
- `tl_ts_mod`: Constructs a DataLoader for image datasets.
- `set_albumen_params`: Specifies the albumentations to be utilized.
- `load_data`: Loads data essential for Mean & Standard Deviation computation.
- `display_incorrect_pred`: Displays images that were misclassified.
- `show_sample`: Provides a glance at sample images.
- `process_dataset`: Implements transformations on the dataset.
- `plot_acc_loss`: Visualizes the accuracy and loss curves.

### models directory
- [custom_resnet.py]: This file provides a custom definition for the Resnet architecture.
