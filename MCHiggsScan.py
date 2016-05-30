# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, RooFit, RooWorkspace, RooRealVar, RooGaussian, RooPlot, kTRUE, kFALSE, TMath, TH1F, TRandom3, gStyle, Double, TH2D
from glob import glob
from copy import deepcopy
from DataTree import *
from AnalyzeInfo import *
from ToyExperimentGen import *
from ProfileL import *
from numpy import *
from optparse import OptionParser
from HiggsProjekt import *
import os


__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class MCHiggsScan:
    def __init__(self, analyzeInfo, mc='85', mu=1, ntoys=1000):
        self.analyze_info = analyzeInfo
        self.mc = mc
        self.mu = mu
        self.ntoys = ntoys


    def cutsAnalysis(self, mc='85'):
        self.analyze_info.change_montecarlo_to_analyse(mc)
        self.analysis = Analysis(self.analyze_info)
        print 'efficiency: '+str(self.analysis.efficiency('mvis'))
        print 'purity: '+str(self.analysis.purity('mvis'))
        print 'significane: '+str(self.analysis.significance('mvis'))
        del self.analysis

    def allMC_q_Study(self, mu=1):
        self.MC_q_Study('85', mu)
        self.MC_q_Study('90', mu)
        self.MC_q_Study('95', mu)

    def MC_q_Study(self, mc='85', mu=1):
        self.analyze_info.change_montecarlo_to_analyse(mc)
        self.analyze_info.change_number_toys(self.ntoys)
        self.analysis = Analysis(self.analyze_info)
        self.analysis.create_q_histograms(mu, -1)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-m', '--mc', dest='mc', default='85', help='HiggsMC to analyse. e.g. 85')
    parser.add_option('-u', '--mu', dest='mu', default=1, type='float', help='mu value to analyse')
    parser.add_option('-n', '--ntoys', dest='ntoys', default=1000, type='int', help='Number of toys')
    (options, args) = parser.parse_args()
    mu = float(options.mu)
    mc = str(options.mc)
    ntoys = int(options.ntoys)
    a = AnalyzeInfo()
    z = MCHiggsScan(a, mc, mu, ntoys)
    z.MC_q_Study(z.mc, z.mu)