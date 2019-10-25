#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 18:01:37 2019

@author: kaniska
"""

import numpy as np

class Quantizer:
    allowed_modes = ('ufixed', 'fixed')
    allowed_overflow = ('saturate')
    allowed_rounding = {'floor': np.floor, 
                        'ceil': np.ceil, 
                        'nearest': np.round}


    
    @classmethod
    def check_arg(cls, arg, allowed_values):
        if arg not in allowed_values:
            raise ValueError(f'{arg} not supported. Only the following values are allowed {allowed_values}')
    

    def __init__(self, total_bits, frac_bits, 
                mode='ufixed', round_mode='nearest', overflow_mode='saturate'):
        self.check_arg(mode, self.allowed_modes)
        self.check_arg(round_mode, self.allowed_rounding)
        self.check_arg(overflow_mode, self.allowed_overflow)

        self.mode = mode
        self.round_mode = round_mode
        self.overflow_mode = overflow_mode
        
        self.total_bits = total_bits
        self.frac_bits = frac_bits
        self.int_bits = total_bits - frac_bits

    def quantize(self, inp):
        frac_multiplier = 2**(self.frac_bits)
        sign = np.sign(inp)

        inp_abs = np.abs(inp)
        inp_int = np.floor(inp_abs)
        inp_frac = sign*(inp_abs - inp_int)
        
        quant_func = self.allowed_rounding[self.round_mode]
        quantized_frac = quant_func( frac_multiplier * inp_frac ) / frac_multiplier

        quantized_frac_abs = np.abs(quantized_frac)
        output = sign*(inp_int+ quantized_frac_abs)

        output, overflow  = self.check_for_overflow(output)

        return output, overflow


    def check_for_overflow(self, inp):
        step_size = 1/(2**self.frac_bits)
        if self.mode == 'ufixed':
            max_val = 2**(self.int_bits) - step_size
            min_val = 0
        elif self.mode == 'fixed':
            max_val = 2**(self.int_bits -1) - step_size
            min_val = -2**(self.int_bits - 1)

        overflow = False
        output = inp
        if self.overflow_mode == 'saturate':
            if inp > max_val:
                overflow = True
                output = max_val 
            elif inp < min_val:
                overflow = True 
                output = min_val

        return output, overflow



if __name__ == '__main__':
        quantizer = Quantizer(12, 8, 'fixed')
        quant_pi, overflow = quantizer.quantize(-np.pi)
        print( quant_pi, overflow ) 