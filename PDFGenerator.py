# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, TH1F, TGraphErrors, TMath, TRandom3
from glob import glob
from copy import deepcopy
from DataTree import *
from BranchInfo import *
from math import factorial, exp

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

    def likelihood(self):
        self.poisson_B = 1
        self.poisson_SB = 1
        for bin in xrange(1, self.numBins+1):
            self.function.Set(self.num_points+1)
            x = self.signalHisto.GetBinCenter(bin)
            valueS = self.signalHisto.GetBinContent(bin)
            valueB = self.backgroundHisto.GetBinContent(bin)
            valueSB = valueS + valueB
            poisson_value_B = self.one_bin_mc(valueS, valueB, 0, valueSB)
            poisson_value_SB = self.one_bin_mc(valueS, valueB, 1, valueSB)

            poisson_B = poisson_B * poisson_value_B
            poisson_SB = poisson_SB * poisson_value_SB
            return poisson_B, poisson_SB
        return

            # poisson_value = TMath.PoissonI()

    def one_bin_mc(self, signal, background, mu, n):
        MC = (mu * signal + background) ** n / factorial(n) * exp(- mu * signal - background)
        return deepcopy(MC)
