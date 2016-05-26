# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TH1F, TMath, RooStats
from PDFGenerator import *
from BranchInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

class qValue:
    def __init__(self, higgsName, branchName, sig_bkg_histos, sig_histos, bkg_histos, data_histos):
        self.branch_info = BranchInfo()
        self.pdf = PDFGenerator(branchName, sig_bkg_histos, bkg_histos)
        self.numBins = self.branch_info.branch_numbins[branchName]
        self.sig_value = {binN: sig_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        self.bkg_value = {binN: bkg_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        self.data_value = {binN: data_histos[higgsName][branchName]. GetBinContent for binN in xrange(self.numBins)}
        self.mc_value = {binN: self.pdf.functionSB[binN] for binN in xrange(self.numBins)}

    def poisson(self, binN):
        s = self.sig_value[binN]
        b = self.bkg_value[binN]
        mc = self.mc_value[binN]
        pdf = TMath.Poisson(u * s + b, mc)
        return deepcopy(pdf)

    def likelihood(self):
        L = 1
        for binN in xrange(1, self.numBins+1, 1):
            L * self.poisson(binN)
        return L

    def max_likelihood(self, L):
        likelihood = []
        for u in xrange(0,1,0.001):
            likelihood.append()
