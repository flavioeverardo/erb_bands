"""
Taken from https://github.com/wil-j-wil/py_bank

Based on Josh McDermott's Matlab filterbank code:
http://mcdermottlab.mit.edu/Sound_Texture_Synthesis_Toolbox_v1.7.zip

ERB implementation and Answer Set Programming (ASP) integration by Flavio Everardo
flavio.everardo@cs.uni-potsdam.de
"""

import numpy as np

class FilterBank(object):
    """
    len_signal = lenght of the singal given in samples
    sample_rate = sample rate
    total_erb_bands = number of erb bands given by the user / subbands (excluding high-&low-pass which are added for perfect reconstruction)
    erb_bands = set of erb numbers or erb bands.
    freqs_index = indexes of selected bands in Hz
    bandwidths = bandwidht wrt center frequency
    low_lim = centre frequency of first (lowest) channel
    high_lim = centre frequency of last (highest) channel
    freqs = frequency range
    nfreqs = number of frequencies
    """
    def __init__(self, len_signal, sample_rate, total_erb_bands, low_lim, high_lim):
        self.len_signal = len_signal
        self.sample_rate = sample_rate
        self.total_erb_bands = total_erb_bands
        self.erb_bands = []
        self.freq_index = []
        self.bandwidths = []
        self.low_lim = low_lim
        self.high_lim, self.freqs, self.nfreqs = self.build_frequency_limits(len_signal, sample_rate, high_lim)

    def build_frequency_limits(self, len_signal, sample_rate, high_lim):
        """
        Build frequency limits using a linear scale in Hz
        """
        if np.remainder(len_signal, 2) == 0:
            nfreqs = len_signal
            max_freq = sample_rate / 2
        else:
            nfreqs = (len_signal - 1)
            max_freq = sample_rate * (len_signal - 1) / 2 / len_signal
        freqs = np.linspace(0, max_freq, nfreqs + 1)
        if high_lim > sample_rate / 2:
            high_lim = max_freq
        return high_lim, freqs, int(nfreqs)


class EquivalentRectangularBandwidth(FilterBank):
    """
    erb_low  = lowest erb band
    erb_high = highest erb band
    erb_lims = limits between erb bands
    cutoffs  = cuts between erb bands
    """
    def __init__(self, len_signal, sample_rate, total_erb_bands, low_lim, high_lim):
        super(EquivalentRectangularBandwidth, self).__init__(len_signal, sample_rate, total_erb_bands, low_lim, high_lim)
        # Build evenly spaced cutoffs on an ERB Scale
        erb_low  = self.freq2erb(self.low_lim)
        erb_high = self.freq2erb(self.high_lim)
        erb_lims = np.linspace(erb_low, erb_high, self.total_erb_bands + 2)
        self.cutoffs = self.erb2freq(erb_lims)
        self.get_bands(self.total_erb_bands, self.nfreqs, self.freqs, self.cutoffs)
        
    def freq2erb(self, freq_Hz):
        """
        Convert Hz to ERB number
        """
        n_erb = 21.4 * np.log10(1 + 0.00437 * freq_Hz)
        return n_erb

    def erb2freq(self, n_erb):
        """
        Convert ERB number to Hz
        """
        freq_Hz = (np.power(10,(n_erb/21.4))-1)/0.00437
        return freq_Hz

    def get_bands(self, total_erb_bands, nfreqs, freqs, cutoffs):
        """
        Get the erb bands, indexes and bandwidths
        """
        for erb in range(total_erb_bands):
            lower_cutoff   = cutoffs[erb]
            higher_cutoff  = cutoffs[erb + 2]  # adjacent filters overlap by 50%
            erb_center     = (self.freq2erb(lower_cutoff) + self.freq2erb(higher_cutoff)) / 2
            freq_bandwidth = higher_cutoff - lower_cutoff
            center_freq    = self.erb2freq(erb_center)
            q_factor       = center_freq/freq_bandwidth
            index          = (np.abs(freqs-center_freq)).argmin()
            
            self.erb_bands.append(erb_center)
            self.freq_index.append(index)
            self.bandwidths.append(freq_bandwidth)
