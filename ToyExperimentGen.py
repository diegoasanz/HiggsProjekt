# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, TH1F, TGraphErrors, TMath, TRandom3, Math
from glob import glob
from copy import deepcopy
from DataTree import *
from AnalyzeInfo import *
from math import factorial, exp, log
from numpy import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class ToyExperimentGen:
    def __init__(self, analyzeInfo, histo, branchName, randomgen, num, name):
        self.random = randomgen
        self.input_histo = histo
        self.analyze_info = analyzeInfo
        self.number = num
        self.numBins = int(self.analyze_info.branch_numbins[branchName] + 1)
        self.maxBin = self.analyze_info.branch_max[branchName]+float(self.analyze_info.branch_max[branchName]-self.analyze_info.branch_min[branchName])/float(2 * self.analyze_info.branch_numbins[branchName])
        self.minBin = self.analyze_info.branch_min[branchName]-float(self.analyze_info.branch_max[branchName]-self.analyze_info.branch_min[branchName])/float(2 * self.analyze_info.branch_numbins[branchName])
        self.widthBin = float((self.maxBin - self.minBin)/self.numBins)
        self.toy = TH1F(name+'_'+str(num), name+'_'+str(num), self.numBins, self.minBin, self.maxBin)
        self.generate_toy_bins()
        # c3 = TCanvas('c3','c3',1)
        # c3.cd()
        # self.toy.Draw()
        # c3.SaveAs('toy_'+str(num)+'.png')
        # c3.Delete()
        ## self.sig_bkg = sig_bkg_histos[branchName]
        ## self.bkg = bkg_histos[branchName]
        ## self.functionSB = {binN: TGraphErrors(self.numBins, self.sig_bkg.GetBinCenter(binN), self.get_k(self.cdf_generator(self.sig_bkg)[0], random, self.cdf_generator(self.sig_bkg)[1]), self.widthBin, self.sig_bkg.SetBinErrorOption(TH1F.kPoisson)) for binN in xrange(1, self.numBins+1, 1)}
        ## self.functionB = {binN: TGraphErrors(self.numBins, self.bkg.GetBinCenter(binN), self.get_k(self.cdf_generator(self.bkg)[0], random, self.cdf_generator(self.bkg)[1]), self.widthBin, self.bkg.SetBinErrorOption(TH1F.kPoisson)) for binN in xrange(1, self.numBins+1, 1)}

    def generate_toy_bins(self):
        for bin_i in xrange(1, self.numBins+1):
            cdf = self.cdf_generator(self.input_histo, bin_i)
            value = self.get_k(cdf, self.random)
            self.toy.SetBinContent(bin_i, value)

    def cdf_generator(self, histo, binN):
        mean = histo.GetBinContent(binN)
        sdev = TMath.Sqrt(mean)
        maxK = mean + 4 * sdev  # mean + 4 * mean
        ks = linspace(0, maxK, 101)  # xrange(maxK)# [k for k in xrange(maxK)]
        cdf = {pos: [ks[pos], Math.inc_gamma_c(ks[pos]+1, mean)] for pos in xrange(len(ks))}  # dictionary wich contains the x and y info of the cdf in a list of two elements. e.g. cdf[1] -> [0, 0].
        return deepcopy(cdf)

    def get_k(self, cdf, rnd):
        y = rnd.Rndm()
        if y <= cdf[0][1]:
            return float(cdf[0][0])
        for k in xrange(1, len(cdf)):
            if y == cdf[k][1]:
                return float(cdf[k][0])
            elif y < cdf[k][1]:
                return float((cdf[k][0] + cdf[k-1][0])/2)
        return float(cdf[len(cdf)-1][0])













    # def one_bin_mc(self, signal, background, mu, observed):
    #     MC = (mu * signal + background) ** observed / factorial(observed) * exp(- mu * signal - background)
    #     return deepcopy(MC)
    #
    # def log_likelihood_ratio(self, valueOb):
    #     exp_bkg = 1
    #     exp_sig_bkg = 1
    #     for bin in xrange(1, self.numBins+1):
    #         valueS = self.signalHisto.GetBinContent(bin)
    #         valueB = self.backgroundHisto.GetBinContent(bin)
    #         valueSB = valueS + valueB
    #         poisson_value_B = self.one_bin_mc(valueS, valueB, 0, valueOb)
    #         poisson_value_SB = self.one_bin_mc(valueS, valueB, 1, valueOb)
    #         exp_bkg = exp_bkg * poisson_value_B  # not sure whether this is the correct way for calculating recursion?
    #         exp_sig_bkg = exp_sig_bkg * poisson_value_SB
    #         return exp_bkg, exp_sig_bkg
    #     q = -2 * log(exp_sig_bkg / exp_bkg)
    #     return deepcopy(q)
    #
    # def generate_trial(self, num_trials, mean):
    #     trial_list = []
    #     for trial in xrange(0, num_trials):
    #         q = self.log_likelihood_ratio(TMath.PoissonI(mean))

