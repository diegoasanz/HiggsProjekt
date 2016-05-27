# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TH1F, TMath, RooStats, TF1
from PDFGenerator import *
from BranchInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

class qValue:
    def __init__(self, toy, histogrammu1, histogrammu2, sig_bkg_histos, sig_histos, bkg_histos, data_histos):
        self.branch_info = BranchInfo()
        self.numBins = self.branch_info.number_toys
        self.auxiliary_histo = TH1F('h1', 'h1', self.numBins, 0, self.numBins)
        self.pdf = PDFGenerator(branchName, sig_bkg_histos, bkg_histos)
        self.numBins = self.branch_info.branch_numbins[branchName]
        self.sig_value = {binN: sig_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        self.bkg_value = {binN: bkg_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        self.data_value = {binN: data_histos[higgsName][branchName]. GetBinContent for binN in xrange(self.numBins)}
        self.mc_value = {binN: self.pdf.functionSB[binN] for binN in xrange(self.numBins)}

    def poisson(self, ):
        s = self.sig_value[binN]
        b = self.bkg_value[binN]
        mc = self.mc_value[binN]
        pdf = TF1("pdf", "TMath.Poisson(u * s + b, mc)", 0, 1)
        return deepcopy(pdf)

    def likelihood(self):
        L = 1
        for binN in xrange(1, self.numBins+1, 1):
            L * self.poisson(binN)
        return L

    def max_likelihood(self, L):
        for u in xrange(0, 1, 0.001):
            if L(u+1) - L(u) == 0:
                return u
