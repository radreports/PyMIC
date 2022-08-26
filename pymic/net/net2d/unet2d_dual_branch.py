# -*- coding: utf-8 -*-
"""
Extention of U-Net with two decoders. The network was introduced in
the following paper:
    Xiangde Luo, Minhao Hu, Wenjun Liao, Shuwei Zhai, Tao Song, Guotai Wang,
    Shaoting Zhang. ScribblScribble-Supervised Medical Image Segmentation via 
    Dual-Branch Network and Dynamically Mixed Pseudo Labels Supervision.
    MICCAI 2022. 
"""
from __future__ import print_function, division

import torch
import torch.nn as nn
from pymic.net.net2d.unet2d import *

class UNet2D_DualBranch(nn.Module):
    def __init__(self, params):
        super(UNet2D_DualBranch, self).__init__()
        self.output_mode = params.get("output_mode", "average")
        self.encoder  = Encoder(params)
        self.decoder1 = Decoder(params)    
        self.decoder2 = Decoder(params)        

    def forward(self, x):
        x_shape = list(x.shape)
        if(len(x_shape) == 5):
          [N, C, D, H, W] = x_shape
          new_shape = [N*D, C, H, W]
          x = torch.transpose(x, 1, 2)
          x = torch.reshape(x, new_shape)

        f = self.encoder(x)
        output1 = self.decoder1(f)
        output2 = self.decoder2(f)
        if(len(x_shape) == 5):
            new_shape = [N, D] + list(output1.shape)[1:]
            output1 = torch.reshape(output1, new_shape)
            output1 = torch.transpose(output1, 1, 2)
            output2 = torch.reshape(output2, new_shape)
            output2 = torch.transpose(output2, 1, 2)

        if(self.training):
          return output1, output2
        else:
          if(self.output_mode == "average"):
            return (output1 + output2)/2
          elif(self.output_mode == "first"):
            return output1
          else:
            return output2
