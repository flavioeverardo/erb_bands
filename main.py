#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base code implemented by Ajin Tom to read wav files and calculate the average spectrum.
Taken from https://github.com/ajintom/auto-spatial/blob/master/final/my_algo-Ajin%E2%80%99s%20MacBook%20Pro.ipynb

ERB implementation and modification to use with Answer Set Programming (ASP) by Flavio Everardo
flavio.everardo@cs.uni-potsdam.de
"""

## Imports
import numpy as np
import matplotlib.pyplot as plt
from librosa import load, stft, magphase
import erb as erb

# Input data
# Trach Name without extension
track_name = "snare"

## STFT parameters
sr = 44100.0       # Sample Rate
N  = 32768         # FFT size or Number of Samples
M  = N             # Window size 
H  = M/64          # Hop size
W  = np.hanning(M) # Window Type
B  = 50            # ERB Bands
low_lim = 20       # centre freq. of lowest filter
high_lim = sr / 2  # centre freq. of highest filter

## Load WAV File
track,sr = load(track_name+'.wav', sr = sr, mono = 'True')
## Perform Short Term Fourier Transform
stft = stft(y = track, n_fft = N,win_length=M, hop_length=H, window = 'hann')
## Magnitudes (excluding phase)
magnitude, _ = magphase(stft)
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

## Plot
plt.figure(figsize=(9,6))
plt.subplot(211)
plt.grid(True)
plt.plot(freqs,spec_avg)
plt.title(track_name+" Spectrum")
plt.xlabel('Frequency')
plt.xlim(xmin=20)
plt.ylabel('Linear Amp [0-1]')
plt.xscale('log')

plt.subplot(212)
plt.grid(True)
plt.plot(erb_amp)
plt.title(track_name+" ERB Scale")
plt.xlabel('ERB Numbers (1-%s)'%B)
plt.ylabel('Linear Amp [0-1]')

plt.tight_layout()

plt.savefig('%s.png'%track_name)
plt.show()
