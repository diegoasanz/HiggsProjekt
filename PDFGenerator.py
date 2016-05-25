# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, TH1F, TGraphErrors, TMath, TRandom3
from glob import glob
from copy import deepcopy
from DataTree import *
from BranchInfo import *
from math import factorial, exp, log

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

random = TRandom3(123654)

class PDFGenerator:
    def __init__(self, branchName, signalHistos, backgroundsHistos):
        self.branch_info = BranchInfo()
        self.numBins = self.branch_info.branch_numbins[branchName]
        self.maxBin = self.branch_info.branch_max[branchName]
        self.minBin = self.branch_info.branch_min[branchName]
        self.widthBin = float((self.maxBin - self.minBin)/self.numBins)
        self.functionSB = TGraphErrors()
        self.functionB = TGraphErrors()
        self.num_points = int(0)
        self.signalHisto = signalHistos[branchName]
        self.backgroundHisto = backgroundsHistos[branchName]

    def one_bin_mc(self, signal, background, mu, observed):
        MC = (mu * signal + background) ** observed / factorial(observed) * exp(- mu * signal - background)
        return deepcopy(MC)

    def log_likelihood_ratio(self, valueOb):
        exp_bkg = 1
        exp_sig_bkg = 1
        for bin in xrange(1, self.numBins+1):
            valueS = self.signalHisto.GetBinContent(bin)
            valueB = self.backgroundHisto.GetBinContent(bin)
            valueSB = valueS + valueB
            poisson_value_B = self.one_bin_mc(valueS, valueB, 0, valueOb)
            poisson_value_SB = self.one_bin_mc(valueS, valueB, 1, valueOb)
            exp_bkg = exp_bkg * poisson_value_B  # not sure whether this is the correct way for calculating recursion?
            exp_sig_bkg = exp_sig_bkg * poisson_value_SB
            return exp_bkg, exp_sig_bkg
        q = -2 * log(exp_sig_bkg / exp_bkg)
        return deepcopy(q)

    def generate_trial(self, num_trials, mean):
        trial_list = []
        for trial in xrange(0, num_trials):
            q = self.log_likelihood_ratio(TMath.PoissonI(mean))
