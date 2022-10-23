# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 08:02:01 2021

@author: dd102
"""

#%%

import tensorflow as tf
import pickle, sys, time
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Input, BatchNormalization, Activation, Conv2D, Add, Multiply
from tensorflow.keras.layers import MaxPool2D, UpSampling2D, AveragePooling2D, Flatten, Dense
from tensorflow.keras import Model



#%%

class ResidualUnit():
    def __init__(self, title, filters, activation='relu', use_bias=False, downSample=False):
        if type(filters) == list and len(filters) == 3: # Need 3 filter values for each of 3 bn->relu->conv2d layeres
            self.filters = filters
        else:
            raise Exception("ResidualUnit Error! Please input a list of 3 integers as the unit filters.")
        # stride length, 1 for Attention Module res units, 2 for res units outside of Attention modules
        self.downSample = downSample
        if self.downSample:    
            self.stride = 2
        else:
            self.stride = 1
        self.activation = activation # ReLU default activation type
        self.use_bias = use_bias # Whether to use bias in Conv2D layers, False for now
        self.title = title
        self.layer_names = list()
        for i in range(11):
            self.layer_names.append('ResUnit_L{}_'.format(i+1) + self.title)
        for i in range(len(self.layer_names)):
            print(self.layer_names[i])
            
        self.bn_1 = BatchNormalization(name = self.layer_names[-11]) # 1st batch normalization layer
        self.activ_1 = Activation(self.activation, name = self.layer_names[-10]) # 1st PRE-ACTIVATION relu layer
        self.conv_1 = Conv2D(name = self.layer_names[-9], filters = self.filters[0], kernel_size=(1,1), strides=(1,1), padding='same', use_bias = self.use_bias) # 1st Conv2D layer
        
        self.bn_2 = BatchNormalization(name = self.layer_names[-8]) # 2nd batch normalization layer
        self.activ_2 = Activation(self.activation, name = self.layer_names[-7]) # 2nd PRE-ACTIVATION relu layer
        self.conv_2 = Conv2D(name = self.layer_names[-6], filters = self.filters[1], kernel_size=(3,3), strides=self.stride, padding='same', use_bias = self.use_bias) # 2nd Conv2D layer

        self.bn_3 = BatchNormalization(name = self.layer_names[-5]) # 3rd batch normalization layer
        self.activ_3 = Activation(self.activation, name = self.layer_names[-4]) # 3rd PRE-ACTIVATION relu layer
        self.conv_3 = Conv2D(name = self.layer_names[-3], filters = self.filters[2], kernel_size=(1,1), strides=(1,1), padding='same', use_bias = self.use_bias) # 3rd Conv2D layer   
        
        # Skip convolutional layer that goes to output
        self.conv_Identity = Conv2D(name = self.layer_names[-2], filters = self.filters[2], kernel_size=(1,1), strides=self.stride, padding='same', use_bias = self.use_bias)
        self.Add_layer = Add(name = self.layer_names[-1]) # Layer for element-wise addition
        
    def forward(self, X):
        self.X_Input = X
        
        # Forward pass through 1st bn->relu->conv segment
        y1 = self.bn_1(self.X_Input) # Batch normalize
        y1 = self.activ_1(y1) # Pre-activation
        self.y_Identity = y1
        y1 = self.conv_1(y1) # Conv Output
        # Forward pass through 2nd bn->relu->conv segment
        y2 = self.bn_2(y1)
        y2 = self.activ_2(y2)
        y2 = self.conv_2(y2)
        # Forward pass through 3rd bn->relu->conv segment
        y3 = self.bn_3(y2)
        y3 = self.activ_3(y3)
        y3 = self.conv_3(y3)
        
        # Skip Conv2D layer operation for Residual operation
        # Verify that the input filter size and conv output size is the same as the output filter size and conv size
        if y3.shape != self.y_Identity.shape or self.strides != 1:
            self.conv_Identity.filters = y3.shape[-1]
            y_Identity_Out = self.conv_Identity(self.y_Identity)
        else:
            y_Identity_Out = self.y_Identity
        # Add the skip connection output
        y_Out = self.Add_layer([y3, y_Identity_Out])
        
        return y_Out # Return results


#%%

class SpecialConvUnit_AttnMod_Mask(): # Special Convolutional Output for Attention Module Mask Branch
    def __init__(self, filters, activation='relu', use_bias=False, attn_mod='1-1'):
        if type(filters) == list and len(filters) == 3:
            self.filters = filters
        else:
            raise Exception("SpecialConvUnit Error! Please input a list of 3 integers as the unit filters (last is used).")
        self.attn_mod=attn_mod
        self.activation = activation # Conv pre-activation
        self.use_bias = use_bias # Default False
        self.count = 0

        self.layer_names = list()

        for i in range(7):
            self.layer_names.append('SpcConv_Mask_L{}_Attn_S{}'.format(i+1, self.attn_mod))
        # 1st Conv segment
        self.bn_1 = BatchNormalization(name=self.layer_names[-7]) # Normalize data
        self.ReLU_1 = Activation(self.activation, name=self.layer_names[-6]) # Pre Activation
        # Conv2D output
        self.conv_1 = Conv2D(name=self.layer_names[-5], filters=self.filters[-1], kernel_size=(1,1),  
                             strides=(1,1), padding='same', use_bias = self.use_bias)
        # 2nd Conv segment
        self.bn_2 = BatchNormalization(name=self.layer_names[-4]) # Normalize data
        self.ReLU_2 = Activation(self.activation, name=self.layer_names[-3])  # Pre Activation
        # Conv2D output
        self.conv_2 = Conv2D(name=self.layer_names[-2], filters=self.filters[-1], kernel_size=(1,1),  
                             strides=(1,1), padding='same', use_bias = self.use_bias)
        # Final sigmoid output
        self.count += 1
        self.Sigmoid_Out = Activation('sigmoid', name=self.layer_names[-1])
        
    def forward(self, X):
        self.X_Input = X
        
        y1 = self.bn_1(self.X_Input)
        y1 = self.ReLU_1(y1)
        y1 = self.conv_1(y1)
        
        y2 = self.bn_2(y1)
        y2 = self.ReLU_2(y2)
        y2 = self.ReLU_2(y2)
        
        y_Out = self.Sigmoid_Out(y2)
        
        return y_Out




#%%

class AttentionModule_Stage_01():
    def __init__(self, filters, substage=1, p=1, t=2, r=1, learning_type='ARL', use_bias=False):
        if type(filters) == list and len(filters) == 3:
            self.filters = filters
        else:
            raise Exception("AttentionModule Error! Please input a list of 3 integers as the unit filters.")
        self.substage = substage
        self.p = p
        self.t = t
        self.r = r
        self.learning_type_choices = ['ARL','NAL'] # Attention Module must use either "Naive Attention Learning" or "Attention Residual Learning"
        # If naive (NAL), just multiply trunk and soft mask outputs; if not naive (ARL), multiply trunk and soft mask and add back trunk for output
        if learning_type in self.learning_type_choices:
            self.learning_type = learning_type
        else:
            raise Exception("Entered learning type is invalid!  Please input either 'ARL' or 'NAL'.")

        self.use_bias = use_bias # Choose whether to use bias in Conv2D layers
        self.layer_names = list()
        
        # Input Residual Unit (res unit), p res units
        self.Res_Input = defaultdict()
        for i in range(self.p):
            title = 'Input-p-{}-{}_AttnS1-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Input[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        
        # Trunk Branch Res Unit Layer, t trunk res units
        self.Res_Trunk_t=defaultdict()
        for i in range(self.t):
            title = 'Trunk-t-{}-{}_AttnS1-{}'.format(self.t, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Trunk_t[i]= ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        
        # Soft Attention Mask Branch Layers
        title = 'MaxPool_DownSamp-{}_Mask_AttnS1-{}'.format(1, self.substage)
        self.layer_names.append(title)
        self.MaxPool_Down_SM_1 = MaxPool2D(name = title, 
                                           pool_size=(3,3), strides=2, padding="same") # 1st maxpool downsampling operation
        
        title = 'SkipConn-Outer_Mask_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Res_SkipConn_Outer_SM = ResidualUnit(title, self.filters, use_bias = self.use_bias) # 1st (only) Skip connection res unit 
       
        # 1st mask res unit for downsampling segment; Run r times
        self.Res_SM_Down_1r_1 = defaultdict()
        for i in range(self.r):
            title = 'DownSamp-r-{}-{}_Mask_AttnS1-{}'.format(self.r, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Down_1r_1[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias)
        
        # 1st (only) Skip connection res unit 
        title = 'SkipConn-Inner_Mask_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Res_SkipConn_Inner_SM = ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        # 2nd mask maxpool downsampling operation
        title = 'MaxPool_DownSamp-{}_Mask_AttnS1-{}'.format(2, self.substage)
        self.layer_names.append(title)
        self.MaxPool_Down_SM_2 = MaxPool2D(name = title, pool_size=(3,3), strides=2, padding="same") 
        
        # Mask branch middle res units, 2*r res units
        self.Res_SM_Middle_2r = defaultdict()
        for i in range(int(2*self.r)):
            title = 'Mid-2r-{}-{}_Mask_AttnS1-{}'.format(int(2*self.r), i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Middle_2r[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) # Mask branch middle res units, call 2*r times
        
        # 1st mask upsampling operation
        title = 'UpSamp2D-{}_Mask_AttnS1-{}'.format(1,self.substage)
        self.layer_names.append(title)
        self.UpSampling_Up_SM_1 = UpSampling2D(name=title, size=(2,2)) 
        
        # Elementwise Addition layer to add output of downsampling segment res unit to output of 1st UpSampling layer
        title = 'Add_L1_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_1 = Add(name=title) 
        
        
        # 1st mask res unit for upsampling segment; Run r times
        self.Res_SM_Up_1r_2 = defaultdict()
        for i in range(self.r):
            title = 'UpSamp-r-{}-{}_Mask_AttnS1-{}'.format(self.r, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Up_1r_2[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias)
        
        # 2nd mask upsampling operation
        title = 'UpSamp2D-{}_Mask_AttnS1-{}'.format(2,self.substage)
        self.layer_names.append(title)
        self.UpSampling_SM_Up_2 = UpSampling2D(name=title, size=(2,2)) 
        
        # Elementwise Addition layer to add output of Skip connection to previous Addition layer
        title = 'Add_L2_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_2 = Add(name=title) 
        
        # Special convolutional layer for Mask branch output
        title = '2-{}'.format(self.substage)
        self.layer_names.append(title)
        self.specialConvOut = SpecialConvUnit_AttnMod_Mask(filters = self.filters, 
                                                           use_bias=self.use_bias,
                                                           attn_mod=title) 
        title = 'Mult_L1_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Mult_layer = Multiply(name=title) # Elementwise Multiplication layer to get product of Trunk branch and Special Convolutional Layer
        
        title = 'Add_L3_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_3 = Add(name=title) # Elementwise Addition layer to add Trunk layer to previous Multiply layer
        
        # Last output res unit segment, run p times
        self.Res_Output = defaultdict()
        for i in range(self.p):
            title = 'Output-p-{}-{}_AttnS1-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Output[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 

    def forward(self, X):
        self.X_Input = X # Input to Attention layer
        # Input Forward Pass: Iterate over p={1} initial Residual Units (res units shorthand)
        for i in range(self.p):
            if i==0:
                Y_Res_Input_1 = self.Res_Input[i].forward(self.X_Input)
            else:
                Y_Res_Input_1 = self.Res_Input[i].forward(Y_Res_Input_1)
        
        
        
        # Soft Attention Mask Forward Pass
        Y_SM_1 = self.MaxPool_Down_SM_1(Y_Res_Input_1) # 1st MaxPool for downsampling segment
        
        Y_Skip_SM_Outer = self.Res_SkipConn_Outer_SM.forward(Y_SM_1)
        
        for i in range(self.r): # Run r times
            if i==0:
                Y_SM_2 = self.Res_SM_Down_1r_1[i].forward(Y_SM_1) # Pass to skip connection and next max pool layer
            else:
                Y_SM_2 = self.Res_SM_Down_1r_1[i].forward(Y_SM_2)
        
        Y_Skip_SM_Inner = self.Res_SkipConn_Inner_SM.forward(Y_SM_2)
        
        Y_SM_3 = self.MaxPool_Down_SM_2(Y_SM_2) # 2nd MaxPool for downsampling segment
        
        # Mask Middle Res Units
        for i in range(int(2*self.r)):
            if i==0:
                Y_SM_4 = self.Res_SM_Middle_2r[i].forward(Y_SM_3)
            else:
                Y_SM_4 = self.Res_SM_Middle_2r[i].forward(Y_SM_4)
        
        Y_SM_5 = self.UpSampling_Up_SM_1(Y_SM_4) # 1st UpSampling output for upsampling segment
        
        Y_SM_6_SkipAdd_1 = self.Add_layer_1([Y_Skip_SM_Inner, Y_SM_5]) # Add output of 1st downsampling res unit to previous output
        
        for i in range(self.r):
          if i==0:
              Y_SM_7 = self.Res_SM_Up_1r_2[i].forward(Y_SM_6_SkipAdd_1) # Output of 1st upsampling res unit
          else:
              Y_SM_7 = self.Res_SM_Up_1r_2[i].forward(Y_SM_7)
        
        Y_SM_8_SkipAdd_2 = self.Add_layer_2([Y_Skip_SM_Outer, Y_SM_7]) # Add skip connection output to previous output

        Y_SM_9 = self.UpSampling_SM_Up_2(Y_SM_8_SkipAdd_2) # 2nd UpSampling output for upsampling segment
        
        # Trunk branch- t iterations
        for i in range(self.t):
            if i==0:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Res_Input_1) # Trunk output
            else:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Trunk_1) # Trunk output
        
        
        
        Y_SM_10_SpecConv = self.specialConvOut.forward(Y_SM_9) # Output of special convolution unit
        
        Y_Combined_1 = self.Mult_layer([Y_SM_10_SpecConv, Y_Trunk_1]) # Prodcut of Trunk branch and Special Convolution Layer
        
        # If 'ARL', add trunk output to product of trunk output and special convolution output
        if self.learning_type == self.learning_type_choices[0]:
            Y_Combined_2 = self.Add_layer_3([Y_Combined_1, Y_Trunk_1])
        # If 'NAL', just keep product of trunk output and special convolution layer
        elif self.learning_type == self.learning_type_choices[-1]:
            Y_Combined_2 = Y_Combined_1
        
        for i in range(self.p): # Get p output res units
            if i==0:
                Y_Out = self.Res_Output[i].forward(Y_Combined_2) # Pass mask and trunk output
            else:
                Y_Out = self.Res_Output[i].forward(Y_Out) # Pass last output res unit result
        
        return Y_Out # Return Final Output


#%%

class AttentionModule_Stage_02():
    def __init__(self, filters, substage=1, p=1, t=2, r=1, learning_type='ARL', use_bias=False):
        if type(filters) == list and len(filters) == 3:
            self.filters = filters
        else:
            raise Exception("AttentionModule Error! Please input a list of 3 integers as the unit filters.")
        self.substage = substage
        self.p = p
        self.t = t
        self.r = r
        self.learning_type_choices = ['ARL','NAL'] # Attention Module must use either "Naive Attention Learning" or "Attention Residual Learning"
        # If naive (NAL), just multiply trunk and soft mask outputs; if not naive (ARL), multiply trunk and soft mask and add back trunk for output
        if learning_type in self.learning_type_choices:
            self.learning_type = learning_type
        else:
            raise Exception("Entered learning type is invalid!  Please input either 'ARL' or 'NAL'.")

        self.use_bias = use_bias # Choose whether to use bias in Conv2D layers
        self.layer_names = list()
        # Input Residual Unit (res unit), p res units
        self.Res_Input = defaultdict()
        for i in range(self.p):
            title = 'Input-p-{}-{}_AttnS2-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Input[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        
        # Trunk Branch Res Unit Layer, t trunk res units
        self.Res_Trunk_t=defaultdict()
        for i in range(self.t):
            title = 'Trunk-t-{}-{}_AttnS2-{}'.format(self.t, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Trunk_t[i]= ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        
        # Soft Attention Mask Branch Layers
        title = 'MaxPool_DownSamp-{}_Mask_AttnS2-{}'.format(1, self.substage)
        self.layer_names.append(title)
        self.MaxPool_Down_SM_1 = MaxPool2D(name = title, 
                                           pool_size=(3,3), strides=2, padding="same") # 1st maxpool downsampling operation
        
        # # 1st Skip connection res unit 
        # title = 'SkipConn-Outer_Mask_AttnS1-{}'.format(self.substage)
        # self.layer_names.append(title)
        # self.Res_SkipConn_Outer_SM = ResidualUnit(title, self.filters, use_bias = self.use_bias) # 1st (only) Skip connection res unit 
       
        # 1st mask res unit for downsampling segment; Run r times
        self.Res_SM_Down_1r_1 = defaultdict()
        for i in range(self.r):
            title = 'DownSamp-r-{}-{}_Mask_AttnS2-{}'.format(self.r, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Down_1r_1[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias)
        
        # 2nd Skip connection res unit 
        title = 'SkipConn-Inner_Mask_AttnS2-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Res_SkipConn_Inner_SM = ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        # 2nd mask maxpool downsampling operation
        title = 'MaxPool_DownSamp-{}_Mask_AttnS2-{}'.format(2, self.substage)
        self.layer_names.append(title)
        self.MaxPool_Down_SM_2 = MaxPool2D(name = title, pool_size=(3,3), strides=2, padding="same") 
        
        # Mask branch middle res units, 2*r res units
        self.Res_SM_Middle_2r = defaultdict()
        for i in range(int(2*self.r)):
            title = 'Mid-2r-{}-{}_Mask_AttnS2-{}'.format(int(2*self.r), i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Middle_2r[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) # Mask branch middle res units, call 2*r times
        
        # 1st mask upsampling operation
        title = 'UpSamp2D-{}_Mask_AttnS2-{}'.format(1,self.substage)
        self.layer_names.append(title)
        self.UpSampling_Up_SM_1 = UpSampling2D(name=title, size=(2,2)) 
        
        # Elementwise Addition layer to add output of downsampling segment res unit to output of 1st UpSampling layer
        title = 'Add_L1_AttnS2-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_1 = Add(name=title) 
        
        
        # 1st mask res unit for upsampling segment; Run r times
        self.Res_SM_Up_1r_2 = defaultdict()
        for i in range(self.r):
            title = 'UpSamp-r-{}-{}_Mask_AttnS2-{}'.format(self.r, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Up_1r_2[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias)
        
        # 2nd mask upsampling operation
        title = 'UpSamp2D-{}_Mask_AttnS2-{}'.format(2,self.substage)
        self.layer_names.append(title)
        self.UpSampling_SM_Up_2 = UpSampling2D(name=title, size=(2,2)) 
        
        # # Elementwise Addition layer to add output of Skip connection to previous Addition layer
        # title = 'Add_L2_AttnS1-{}'.format(self.substage)
        # self.layer_names.append(title)
        # self.Add_layer_2 = Add(name=title) 
        
        # Special convolutional layer for Mask branch output
        title = '1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.specialConvOut = SpecialConvUnit_AttnMod_Mask(filters = self.filters, 
                                                           use_bias=self.use_bias,
                                                           attn_mod=title) 
        title = 'Mult_L1_AttnS2-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Mult_layer = Multiply(name=title) # Elementwise Multiplication layer to get product of Trunk branch and Special Convolutional Layer
        
        title = 'Add_L2_AttnS2-{}'.format(self.substage) # title = 'Add_L3_AttnS1-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_3 = Add(name=title) # Elementwise Addition layer to add Trunk layer to previous Multiply layer
        
        # Last output res unit segment, run p times
        self.Res_Output = defaultdict()
        for i in range(self.p):
            title = 'Output-p-{}-{}_AttnS2-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Output[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 

    def forward(self, X):
        self.X_Input = X # Input to Attention layer
        # Input Forward Pass: Iterate over p={1} initial Residual Units (res units shorthand)
        for i in range(self.p):
            if i==0:
                Y_Res_Input_1 = self.Res_Input[i].forward(self.X_Input)
            else:
                Y_Res_Input_1 = self.Res_Input[i].forward(Y_Res_Input_1)
        
        
        
        # Soft Attention Mask Forward Pass
        Y_SM_1 = self.MaxPool_Down_SM_1(Y_Res_Input_1) # 1st MaxPool for downsampling segment
        
        # Y_Skip_SM_Outer = self.Res_SkipConn_Outer_SM(Y_SM_1)
        
        for i in range(self.r): # Run r times
            if i==0:
                Y_SM_2 = self.Res_SM_Down_1r_1[i].forward(Y_SM_1) # Pass to skip connection and next max pool layer
            else:
                Y_SM_2 = self.Res_SM_Down_1r_1[i].forward(Y_SM_2)
        
        Y_Skip_SM_Inner = self.Res_SkipConn_Inner_SM.forward(Y_SM_2)
        
        Y_SM_3 = self.MaxPool_Down_SM_2(Y_SM_2) # 2nd MaxPool for downsampling segment
        
        # Mask Middle Res Units
        for i in range(int(2*self.r)):
            if i==0:
                Y_SM_4 = self.Res_SM_Middle_2r[i].forward(Y_SM_3)
            else:
                Y_SM_4 = self.Res_SM_Middle_2r[i].forward(Y_SM_4)
        
        Y_SM_5 = self.UpSampling_Up_SM_1(Y_SM_4) # 1st UpSampling output for upsampling segment
        
        Y_SM_6_SkipAdd_1 = self.Add_layer_1([Y_Skip_SM_Inner, Y_SM_5]) # Add output of 1st downsampling res unit to previous output
        
        for i in range(self.r):
          if i==0:
              Y_SM_7 = self.Res_SM_Up_1r_2[i].forward(Y_SM_6_SkipAdd_1) # Output of 1st upsampling res unit
          else:
              Y_SM_7 = self.Res_SM_Up_1r_2[i].forward(Y_SM_7)
        
        # Y_SM_8_SkipAdd_2 = self.Add_layer_2([Y_Skip_SM_Outer, Y_SM_7]) # Add skip connection output to previous output

        Y_SM_8 = self.UpSampling_SM_Up_2(Y_SM_7) # 2nd UpSampling output for upsampling segment
        
        # Trunk branch- t iterations
        for i in range(self.t):
            if i==0:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Res_Input_1) # Trunk output
            else:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Trunk_1) # Trunk output
        
        
        
        Y_SM_9_SpecConv = self.specialConvOut.forward(Y_SM_8) # Output of special convolution unit
        
        Y_Combined_1 = self.Mult_layer([Y_SM_9_SpecConv, Y_Trunk_1]) # Prodcut of Trunk branch and Special Convolution Layer
        
        # If 'ARL', add trunk output to product of trunk output and special convolution output
        if self.learning_type == self.learning_type_choices[0]:
            Y_Combined_2 = self.Add_layer_3([Y_Combined_1, Y_Trunk_1])
        # If 'NAL', just keep product of trunk output and special convolution layer
        elif self.learning_type == self.learning_type_choices[-1]:
            Y_Combined_2 = Y_Combined_1
        
        for i in range(self.p): # Get p output res units
            if i==0:
                Y_Out = self.Res_Output[i].forward(Y_Combined_2) # Pass mask and trunk output
            else:
                Y_Out = self.Res_Output[i].forward(Y_Out) # Pass last output res unit result
        
        return Y_Out # Return Final Output



#%%

class AttentionModule_Stage_03():
    def __init__(self, filters, substage=1, p=1, t=2, r=1, learning_type='ARL', use_bias=False):
        if type(filters) == list and len(filters) == 3:
            self.filters = filters
        else:
            raise Exception("AttentionModule Error! Please input a list of 3 integers as the unit filters.")
        self.substage = substage
        self.p = p
        self.t = t
        self.r = r
        self.learning_type_choices = ['ARL','NAL'] # Attention Module must use either "Naive Attention Learning" or "Attention Residual Learning"
        # If naive (NAL), just multiply trunk and soft mask outputs; if not naive (ARL), multiply trunk and soft mask and add back trunk for output
        if learning_type in self.learning_type_choices:
            self.learning_type = learning_type
        else:
            raise Exception("Entered learning type is invalid!  Please input either 'ARL' or 'NAL'.")

        self.use_bias = use_bias # Choose whether to use bias in Conv2D layers
        self.layer_names = list()

        # Input Residual Unit (res unit), p res units
        self.Res_Input = defaultdict()
        for i in range(self.p):
            title = 'Input-p-{}-{}_AttnS3-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Input[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        # Trunk Branch Res Unit Layer, t trunk res units
        self.Res_Trunk_t = defaultdict()
        for i in range(self.t):
            title = 'Trunk-t-{}-{}_AttnS3-{}'.format(self.t, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Trunk_t[i]= ResidualUnit(title, self.filters, use_bias = self.use_bias) 
        
        # Soft Attention Mask Branch Layers
        
        # 1st downsampling- max pool layer
        title = 'MaxPool_DownSamp-{}_Mask_AttnS3-{}'.format(1, self.substage)
        self.layer_names.append(title)
        self.MaxPool_Down_SM_1 = MaxPool2D(name = title, 
                                           pool_size=(3,3), strides=2, padding="same") # 1st maxpool downsampling operation
        # Mask branch middle res units, 2*r res units
        self.Res_SM_Middle_2r = defaultdict()
        for i in range(int(2*self.r)):
            title = 'UpSamp-r-{}-{}_Mask_AttnS3-{}'.format(self.r, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_SM_Middle_2r[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) # Mask branch middle res units, call 2*r times
        
        # 1st mask upsampling operation
        title = 'UpSamp2D-{}_Mask_AttnS3-{}'.format(1,self.substage)
        self.layer_names.append(title)
        self.UpSampling_Up_SM_1 = UpSampling2D(name=title, size=(2,2)) 
        
        title = '3-{}'.format(self.substage)
        self.layer_names.append(title)
        self.specialConvOut = SpecialConvUnit_AttnMod_Mask(filters = self.filters, use_bias=self.use_bias, attn_mod=title) # Special convolutional layer for Mask branch output
        
        title = 'Mult_L1_AttnS3-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Mult_layer = Multiply(name=title) # Elementwise Multiplication layer to get product of Trunk branch and Special Convolutional Layer
        
        title = 'Add_L1_AttnS3-{}'.format(self.substage)
        self.layer_names.append(title)
        self.Add_layer_1 = Add(name=title) # Elementwise Addition layer to add Trunk branch output to previous UpSampling output
       
        # Last output res unit segment, run p times
        self.Res_Output = defaultdict()
        for i in range(self.p):
            title = 'Output-p-{}-{}_AttnS3-{}'.format(self.p, i+1, self.substage)
            self.layer_names.append(title)
            self.Res_Output[i] = ResidualUnit(title, self.filters, use_bias = self.use_bias) 

    def forward(self, X):
        self.X_Input = X # Input to Attention layer
        # Input Forward Pass: Iterate over p={1} initial Residual Units (res units shorthand)
        for i in range(self.p):
            if i==0:
                Y_Res_Input_1 = self.Res_Input[i].forward(self.X_Input)
            else:
                Y_Res_Input_1 = self.Res_Input[i].forward(Y_Res_Input_1)
        
        # Soft Attention Mask Forward Pass
        Y_SM_1 = self.MaxPool_Down_SM_1(Y_Res_Input_1) # 1st MaxPool for downsampling segment
        
        # Mask Middle Res Units
        for i in range(int(2*self.r)):
            if i==0:
                Y_SM_2 = self.Res_SM_Middle_2r[i].forward(Y_SM_1)
            else:
                Y_SM_2 = self.Res_SM_Middle_2r[i].forward(Y_SM_2)
        
        Y_SM_3 = self.UpSampling_Up_SM_1(Y_SM_2) # 1st UpSampling output for upsampling segment
        
        # Trunk branch
        for i in range(self.t):
            if i==0:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Res_Input_1) # Trunk output
            else:
                Y_Trunk_1 = self.Res_Trunk_t[i].forward(Y_Trunk_1) # Trunk output

        Y_SM_4_SpecConv = self.specialConvOut.forward(Y_SM_3) # Output of special convolution unit

        Y_Combined_1 = self.Mult_layer([Y_SM_4_SpecConv, Y_Trunk_1]) # Product of Trunk branch and Special Convolution Layer
        
        # If 'ARL', add trunk output to product of trunk output and special convolution output
        if self.learning_type == self.learning_type_choices[0]:
            Y_Combined_2 = self.Add_layer_1([Y_Combined_1, Y_Trunk_1])
        # If 'NAL', just keep product of trunk output and special convolution layer
        elif self.learning_type == self.learning_type_choices[-1]:
            Y_Combined_2 = Y_Combined_1
        # Output Forward Pass: Iterate over p={1} initial Residual Units (res units shorthand)
        for i in range(self.p): 
            if i==0:
                Y_Out = self.Res_Output[i].forward(Y_Combined_2) # Pass mask and trunk output
            else:
                Y_Out = self.Res_Output[i].forward(Y_Out) # Pass last output res unit result
        
        return Y_Out # Return Final Output



#%%

class ResidualAttentionModel_56():
    def __init__(self, input_shape, output_classes, filter_base=[128//2,256//2,512//2,1024//2], 
                 activation='relu', p=1, t=2, r=1, learning_type='ARL', use_bias=False):
        self.input_shape = input_shape
        self.output_classes = output_classes
        if type(filter_base) == list and len(filter_base) == 4:
            self.filter_dict = {'1':[filter_base[0]//4, filter_base[0]//4, filter_base[0]],
                                '2':[filter_base[1]//4, filter_base[1]//4, filter_base[1]],
                                '3':[filter_base[2]//4, filter_base[2]//4, filter_base[2]],
                                'Out':[filter_base[3]//4, filter_base[3]//4, filter_base[3]]}
        else:
            raise Exception("RAN Filter List Error! Please input a list of 4 integers as the unit filter base.")
        self.activation = activation
        self.p = p
        self.t = t
        self.r = r
        self.learning_type_choices = ['ARL','NAL'] # Attention Module must use either "Naive Attention Learning" or "Attention Residual Learning"
        # If naive (NAL), just multiply trunk and soft mask outputs; if not naive (ARL), multiply trunk and soft mask and add back trunk for output
        if learning_type in self.learning_type_choices:
            self.learning_type = learning_type
        else:
            raise Exception("Entered learning type is invalid!  Please input either 'ARL' or 'NAL'.")

        self.use_bias = use_bias # Choose whether to use bias in Conv2D layers
        
        self.Model_Input = Input(name='Model_Input', shape = self.input_shape)
        
        self.Conv_Input = Conv2D(name='Conv1_In', filters=32, kernel_size=(3,3), padding='same', use_bias=self.use_bias)
        self.BN_Input = BatchNormalization(name='BN_In')
        self.ReLU_Input = Activation('relu', name='ReLU_In')
        
        self.Res_NotAttnMod_1 = ResidualUnit(title='NotAttnModule_1_NoDS', filters=self.filter_dict['1'], activation = self.activation,
                                             use_bias = self.use_bias, downSample=False)
        
        self.AttnMod_1 = AttentionModule_Stage_01(filters=self.filter_dict['1'], substage=1,
                                                  p=self.p, t=self.t, r=self.r, 
                                                  learning_type=self.learning_type, use_bias=self.use_bias)
        
        self.Res_NotAttnMod_2 = ResidualUnit(title='NotAttnModule_2_DS', filters=self.filter_dict['2'],
                                             activation = self.activation,
                                             use_bias = self.use_bias, downSample=True)
        
        self.AttnMod_2 = AttentionModule_Stage_02(filters=self.filter_dict['2'],  substage=1,
                                                  p=self.p, t=self.t, r=self.r, 
                                                  learning_type=self.learning_type, use_bias=self.use_bias)
        
        self.Res_NotAttnMod_3 = ResidualUnit(title='NotAttnModule_3_DS', filters=self.filter_dict['3'], activation = self.activation,
                                             use_bias = self.use_bias, downSample=True)
        
        self.AttnMod_3 = AttentionModule_Stage_03(filters=self.filter_dict['3'], substage=1,
                                                  p=self.p, t=self.t, r=self.r, 
                                                  learning_type=self.learning_type, use_bias=self.use_bias)
        
        self.Res_NotAttnMod_4 = ResidualUnit(title='NotAttnModule_4_NoDS', filters=self.filter_dict['Out'], activation = self.activation,
                                             use_bias = self.use_bias, downSample=False)
        self.Res_NotAttnMod_5 = ResidualUnit(title='NotAttnModule_5_NoDS', filters=self.filter_dict['Out'], activation = self.activation,
                                             use_bias = self.use_bias, downSample=False)
        self.Res_NotAttnMod_6 = ResidualUnit(title='NotAttnModule_6_NoDS', filters=self.filter_dict['Out'], activation = self.activation,
                                             use_bias = self.use_bias, downSample=False)
        self.BN_Out = BatchNormalization(name='BN_Out')
        self.ReLU_Out = Activation('relu', name='ReLU_Out')
        self.AvgPool_Out = AveragePooling2D(name='AvgPool_Out')
        
        self.Flatten_Out = Flatten(name='Flatten_Out')
        
        self.Dense_Out = Dense(name='Final_Out', units = self.output_classes, activation='softmax')
        
    def return_Model(self):
        
        X_Input = self.Model_Input
        
        Y_Conv_Input = self.Conv_Input(X_Input)
        
        Y_BN_Input = self.BN_Input(Y_Conv_Input)
        
        Y_ReLU_Input = self.ReLU_Input(Y_BN_Input)
        
        Y_Res_NA_1 = self.Res_NotAttnMod_1.forward(Y_ReLU_Input)
        
        Y_AttnMod_1 = self.AttnMod_1.forward(Y_Res_NA_1)
        
        Y_Res_NA_2 = self.Res_NotAttnMod_2.forward(Y_AttnMod_1)
        
        Y_AttnMod_2 = self.AttnMod_2.forward(Y_Res_NA_2)
        
        Y_Res_NA_3 = self.Res_NotAttnMod_3.forward(Y_AttnMod_2)
        
        Y_AttnMod_3 = self.AttnMod_3.forward(Y_Res_NA_3)
        
        Y_Res_NA_4 = self.Res_NotAttnMod_4.forward(Y_AttnMod_3)
        
        Y_Res_NA_5 = self.Res_NotAttnMod_5.forward(Y_Res_NA_4)
        
        Y_Res_NA_6 = self.Res_NotAttnMod_6.forward(Y_Res_NA_5)
        
        Y_BN_Out = self.BN_Out(Y_Res_NA_6)
        Y_ReLU_Out = self.ReLU_Out(Y_BN_Out)
        
        self.AvgPool_Out.pool_size = (Y_ReLU_Out.shape[-3], Y_ReLU_Out.shape[-2])
        Y_AvgPoolOut = self.AvgPool_Out(Y_ReLU_Out)
        
        Y_Flatten_Out = self.Flatten_Out(Y_AvgPoolOut)
        
        Y_Dense_Out = self.Dense_Out(Y_Flatten_Out)

        model = Model(inputs = X_Input, outputs = Y_Dense_Out)        
        
        return model


