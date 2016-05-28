# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TH1F, TMath, RooStats, TF1
from PDFGenerator import *
from BranchInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

class ProfileL:
    def __init__(self):
        self.branch_info = BranchInfo()

    def fit_mu(self, toy, background, signal):
        b = {i: background.GetBinContent(i) for i in xrange(1, background.GetNBinsX()+1)}
        s = {i: signal.GetBinContent(i) for i in xrange(1, background.GetNBinsX()+1)}

        def myFunc(u, i):
            return u * s[i] + b[i]
        
        pdf = TF1("pdf", "myFunc(u)", 0, 1)
        toy.Fit(pdf)


    def qValue(self, toy, histogram_num, histogram_den, sig_bkg_histos, sig_histos, bkg_histos, data_histos):
        numBins = self.branch_info.number_toys
        auxiliary_histo = TH1F('h1', 'h1', numBins, 0, numBins)
        auxiliary_histo.SetBinErrorOption(TH1F.kPoisson)
        for bin in xrange(1, numBins+1):
            toy_bin_cont = toy.GetBinContent(bin)
            h_num_bin_cont = histogram_num.GetBinContent(bin)
            h_den_bin_cont = histogram_den.GetBinContent(bin)
            auxiliary_histo.SetBinContent(bin, log(TMath.Poisson(toy_bin_cont, h_num_bin_cont) - log(TMath.Poisson(toy_bin_cont, h_den_bin_cont))))
        return ((-2) * auxiliary_histo.Integral())
        # self.pdf = PDFGenerator(branchName, sig_bkg_histos, bkg_histos)
        # self.numBins = self.branch_info.branch_numbins[branchName]
        # self.sig_value = {binN: sig_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        # self.bkg_value = {binN: bkg_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        # self.data_value = {binN: data_histos[higgsName][branchName]. GetBinContent for binN in xrange(self.numBins)}
        # self.mc_value = {binN: self.pdf.functionSB[binN] for binN in xrange(self.numBins)}

    # def poisson(self, ):
    #     s = self.sig_value[binN]
    #     b = self.bkg_value[binN]
    #     mc = self.mc_value[binN]
    #     pdf = TF1("pdf", "TMath.Poisson(u * s + b, mc)", 0, 1)
    #     return deepcopy(pdf)
    #
    # def likelihood(self):
    #     L = 1
    #     for binN in xrange(1, self.numBins+1, 1):
    #         L * self.poisson(binN)
    #     return L
    #
    # def max_likelihood(self, L):
    #     for u in xrange(0, 1, 0.001):
    #         if L(u+1) - L(u) == 0:
    #             return u
