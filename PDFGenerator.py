# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, TH1F, TGraphErrors, TMath, TRandom3
from glob import glob
from copy import deepcopy
from DataTree import *
from BranchInfo import *

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
        signalHisto = signalHistos[branchName]
        backgroundHisto = backgroundsHistos[branchName]
        for bin in xrange(1,numBins):

            self.function.Set(self.num_points+1)
            x = signalHisto.GetBinCenter(bin)
            valueS = signalHisto.GetBinContent(bin)
            valueB = backgroundHisto.GetBinContent(bin)
            valueSB = valueS + valueB

            poisson_value = TMath.PoissonI()

    def one_bin_mc(self, signal, background):
