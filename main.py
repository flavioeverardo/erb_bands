#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base code implemented by Ajin Tom to read wav files and calculate the average spectrum.
Taken from https://github.com/ajintom/auto-spatial/blob/master/final/my_algo-Ajin%E2%80%99s%20MacBook%20Pro.ipynb

ERB implementation and modification to use with Answer Set Programming (ASP) by Flavio Everardo
flavio.everardo@cs.uni-potsdam.de
"""

## Imports
import sys
import argparse
import textwrap
import os
import numpy as np
import matplotlib.pyplot as plt
from librosa import load, stft, magphase
import erb as erb


""" 
Parse Arguments 
"""
def parse_params():
    parser = argparse.ArgumentParser(prog='aspeq.py',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
ERB bands representation of an audio (wav) file
Default command-line: python main.py --samples=32768 --erb=40  --file=snare.wav
                                     '''),

                                     epilog=textwrap.dedent('''\
Get help/report bugs via : flavio.everardo@cs.uni-potsdam.de
                                     '''),)

    ## Input related to uniform solving and sampling
    basic_args = parser.add_argument_group("Basic Options")

    parser.add_argument("--samples", type=int, default=32768,
                        help="FFT size or number of samples (1000-32768). Default: 32768.")
    parser.add_argument("--erb", type=int, default=40,
                        help="Number of ERB bands (10-100). Default: 40.")
    parser.add_argument("--file", type=str, default="snare.wav",
                        help="WAV Filename")
    return parser.parse_args()


"""
Checks consistency wrt. related command line args.
"""
def check_input(arguments):
    
    ## Check for errors
    if arguments.samples < 1000 or arguments.samples > 32768:
        raise ValueError("""Number of samples requested is out of bounds""")
    if arguments.erb < 10 or arguments.erb > 100:
        raise ValueError("""Number of erb bands requested is out of bounds""")
    if arguments.file == "":
        raise ValueError("""File cannot be emtpy""")
    
    

""" 
Main function
Get ERB bands, build instances, ground, solve and parse answer sets to mix
"""
def main():

    ## Parse input data
    args = parse_params()
    ## Check for input errors
    check_input(args)

    # Input data
    # Trach Name without extension
    track_name = os.path.splitext(args.file)[0]

    ## STFT parameters
    sr = 44100.0       # Sample Rate
    N  = args.samples  # FFT size or Number of Samples
    M  = N             # Window size 
    H  = int(M/64)     # Hop size
    W  = np.hanning(M) # Window Type
    B  = args.erb      # ERB Bands
    low_lim = 20       # centre freq. of lowest filter
    high_lim = sr / 2  # centre freq. of highest filter

    ## Load WAV File
    track,sr = load(track_name+'.wav', sr = sr, mono = 'True')
    ## Perform Short Term Fourier Transform
    stft_ = stft(y = track, n_fft = N,win_length=M, hop_length=H, window = 'hann')
    ## Magnitudes (excluding phase)
    magnitude, _ = magphase(stft_)
    magnitude = magnitude / np.sum(W) #normalising STFT output
    ## Spectrum Average
    spec_avg = np.average(magnitude,axis=1) 
    spec_avg = spec_avg/np.max(spec_avg)
    len_signal = spec_avg.shape[0] # filter bank length

    # Equivalent Rectangular Bandwidth
    # Create an instance of the ERB filter bank class
    erb_bank = erb.EquivalentRectangularBandwidth(len_signal, sr, B, low_lim, high_lim)

    # Get frequencies indexes
    freqs_index = erb_bank.freq_index
    # Get range of frequencies
    freqs = erb_bank.freqs.tolist()
    # Get frequency bandwidths
    bandwidths = erb_bank.bandwidths

    # Get ERB Bands and convert them to integer
    erb_bands = erb_bank.erb_bands
    erb_bands = list(map(int, erb_bands))

    # Get amplitudes wrt the ERB/Center Freq
    erb_amp = [0]
    for i in range(len(freqs_index)):
        erb_amp.append(spec_avg[freqs_index[i]])

    ## Normalize ERBs amplitude
    max_erb_amp = max(erb_amp)
    erb_amp = erb_amp/max_erb_amp

    ## Get Filters
    filters = erb_bank.filters

    ## Plot
    plt.figure(figsize=(12,7))
    plt.subplot(311)
    plt.grid(True)
    plt.plot(freqs,filters[:, 1:-1])
    plt.title("%s Auditory filters"%B)
    plt.xlabel('Frequencies (Hz)')
    plt.ylabel('Linear Amp [0-1]')

    plt.subplot(312)
    plt.grid(True)
    plt.plot(freqs,spec_avg)
    plt.title(track_name+" Spectrum")
    plt.xlabel('Frequency')
    plt.xlim(xmin=20)
    plt.ylabel('Linear Amp [0-1]')
    plt.xscale('log')

    plt.subplot(313)
    plt.grid(True)
    plt.plot(erb_amp)
    plt.title(track_name+" ERB Scale")
    plt.xlabel('ERB Numbers (1-%s)'%B)
    plt.ylabel('Linear Amp [0-1]')

    plt.tight_layout()

    plt.savefig('%s.png'%track_name)
    plt.show()

    
if __name__ == '__main__':
    sys.exit(main())					      
