
# Instructions

- To run each model, simply run the contents of that jupyter notebook. It will save everything to its respective directories.
- ResidualAttentionNet_56_Cifar10_v2_ARL.ipynb refers to Attention56_v2_ARL
- ResidualAttentionNetwork_56_Cifar10_NAL.ipynb refers to Attention56_v2_NAL
- ResidualAttentionNetwork_56_Cifar10_v1.ipynb refers to Attention56_v1
- ResidualAttentionNetwork_92_Cifar10_ARL.ipynb refers to Attention92_v2_ARL
- ResidualAttentionNetwork_92_Cifar10_NAL.ipynb refers to Attention92_v2_NALARL
- ResidualAttentionNetwork_92_Cifar10_v1_.ipynb refers to Attention92_v1

To evaluate the models, run evaluate_models.ipynb. There is a config dictionary with names, model configurations, and save paths of each model. Simply run this with all paths and models matching and it will generate results in a dictionary format


# Organization of this directory
```
Folder PATH listing for volume Windows-SSD
Volume serial number is 9477-AF6D
C:.
ª   .gitignore
ª   E4040.2021Fall.DDSA.report.dd2676.sa3976.pdf
ª   evaluate_models.ipynb
ª   ran92_v1_train_acc_history.npy
ª   ran92_v1_train_loss_history.npy
ª   ran92_v1_val_acc_history.npy
ª   ran92_v1_val_loss_history.npy
ª   README.md
ª   recover_graphs_from_checkpoints.ipynb
ª   ResidualAttentionNetwork_56_Cifar10_NAL.ipynb
ª   ResidualAttentionNetwork_56_Cifar10_v1.ipynb
ª   ResidualAttentionNetwork_92_Cifar10_ARL.ipynb
ª   ResidualAttentionNetwork_92_Cifar10_NAL.ipynb
ª   ResidualAttentionNetwork_92_Cifar10_v1_.ipynb
ª   ResidualAttentionNet_56_Cifar10_v2_ARL.ipynb
ª   test.py
ª   train_mean.npy
ª   train_std.npy
ª   tree.txt
ª   
+---models
ª   +---ran56_v1
ª   ª   +---graphs
ª   ª   ª       ran56_v1_Accuracy.png
ª   ª   ª       ran56_v1_Loss.png
ª   ª   ª       ran56_v1_modelsummary.txt
ª   ª   ª       
ª   ª   +---history
ª   ª   ª       ran56_v1_history_Tue_Dec_21_05_58_59_2021.npy
ª   ª   ª       
ª   ª   +---saved_models
ª   ª       +---ran56_v1
ª   ª           ª   keras_metadata.pb
ª   ª           ª   saved_model.pb
ª   ª           ª   
ª   ª           +---assets
ª   ª           +---variables
ª   ª                   variables.data-00000-of-00001
ª   ª                   variables.index
ª   ª                   
ª   +---ran56_v2_ARL
ª   ª   +---graphs
ª   ª   ª       ran56_v2_Accuracy.png
ª   ª   ª       ran56_v2_Loss.png
ª   ª   ª       
ª   ª   +---ran56_v2
ª   ª       ª   keras_metadata.pb
ª   ª       ª   saved_model.pb
ª   ª       ª   
ª   ª       +---variables
ª   ª               variables.data-00000-of-00001
ª   ª               variables.index
ª   ª               
ª   +---ran56_v2_nal
ª   ª   +---graphs
ª   ª   ª       ran56_v2_modelsummary.txt
ª   ª   ª       ran56_v2_nal_Accuracy.png
ª   ª   ª       ran56_v2_nal_Loss.png
ª   ª   ª       
ª   ª   +---history
ª   ª   ª       ran56_v2_history_Mon_Dec_20_00_09_47_2021.npy
ª   ª   ª       ran56_v2_history_Mon_Dec_20_00_15_41_2021.npy
ª   ª   ª       
ª   ª   +---saved_models
ª   ª       +---ran56_v2
ª   ª           ª   keras_metadata.pb
ª   ª           ª   saved_model.pb
ª   ª           ª   
ª   ª           +---assets
ª   ª           +---variables
ª   ª                   variables.data-00000-of-00001
ª   ª                   variables.index
ª   ª                   
ª   +---ran92_v1
ª   ª   +---graphs
ª   ª   ª       ran92_v1_Accuracy.png
ª   ª   ª       ran92_v1_Loss.png
ª   ª   ª       ran92_v1_modelsummary.txt
ª   ª   ª       
ª   ª   +---history
ª   ª   +---saved_models
ª   ª       +---ran92_v1_FULL_MODEL_Mon_Dec_20_18_26_00_2021
ª   ª           ª   keras_metadata.pb
ª   ª           ª   saved_model.pb
ª   ª           ª   
ª   ª           +---assets
ª   ª           +---variables
ª   ª                   variables.data-00000-of-00001
ª   ª                   variables.index
ª   ª                   
ª   +---ran92_v2_arl
ª   ª   +---graphs
ª   ª   ª       ran92_v2_arl_Accuracy.png
ª   ª   ª       ran92_v2_arl_Loss.png
ª   ª   ª       ran92_v2_arl_modelsummary.txt
ª   ª   ª       
ª   ª   +---history
ª   ª   ª       ran92_v2_history_Tue_Dec_21_22_36_50_2021.npy
ª   ª   ª       
ª   ª   +---saved_models
ª   ª       +---ran92_v2_ARL
ª   ª       ª   ª   keras_metadata.pb
ª   ª       ª   ª   saved_model.pb
ª   ª       ª   ª   
ª   ª       ª   +---assets
ª   ª       ª   +---variables
ª   ª       ª           variables.data-00000-of-00001
ª   ª       ª           variables.index
ª   ª       ª           
ª   ª       +---ran92_v2_ARL_training
ª   ª           ª   keras_metadata.pb
ª   ª           ª   saved_model.pb
ª   ª           ª   
ª   ª           +---assets
ª   ª           +---variables
ª   ª                   variables.data-00000-of-00001
ª   ª                   variables.index
ª   ª                   
ª   +---ran92_v2_nal
ª       +---graphs
ª       ª       ran92_v2_modelsummary.txt
ª       ª       ran92_v2_nal_Accuracy.png
ª       ª       ran92_v2_nal_Loss.png
ª       ª       
ª       +---history
ª       ª       ran92_v2_history_Mon_Dec_20_00_09_11_2021.npy
ª       ª       ran92_v2_history_Mon_Dec_20_00_15_30_2021.npy
ª       ª       
ª       +---saved_models
ª           +---ran92_v2
ª               ª   keras_metadata.pb
ª               ª   saved_model.pb
ª               ª   
ª               +---assets
ª               +---variables
ª                       variables.data-00000-of-00001
ª                       variables.index
ª                       
+---utils
    ª   MyRAN56_v1.py
    ª   MyRAN56_v2.py
    ª   MyRAN92_v1.py
    ª   MyRAN92_v2.py
    ª   
    +---__pycache__
            MyRAN56_v1.cpython-38.pyc
            MyRAN56_v2.cpython-38.pyc
            MyRAN92_v1.cpython-38.pyc
            MyRAN92_v2.cpython-36.pyc
            MyRAN92_v2.cpython-38.pyc
            

```