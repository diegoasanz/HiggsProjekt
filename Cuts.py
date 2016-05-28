# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, RooFit, RooWorkspace, RooRealVar, RooGaussian, RooPlot, kTRUE, kFALSE, TMath, TH1F
from glob import glob
from copy import deepcopy
from DataTree import *
from AnalyzeInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *


class Cuts:
    def __init__(self, analyzeInfo):
        self.analyze_info = analyzeInfo
        self.cuts_words = {'85': self.getCutWord('85'), '90': self.getCutWord('90'), '95': self.getCutWord('95')}

    def getCutWord(self, mcname):
        word = ''
        for branch in self.analyze_info.branch_names:
            if self.analyze_info.toggle_cuts[branch] == 1:
                word=self.appendToCutWord(word, branch, mcname)
        return word

    def appendToCutWord(self, word, branchname, mcname):
        if mcname == '85':
            if word == '':
                word = word + branchname + '>' + str(self.analyze_info.branch_85_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_85_highcut[branchname])
            else:
                word = word + '&&' + branchname + '>' + str(self.analyze_info.branch_85_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_85_highcut[branchname])
        if mcname == '90':
            if word == '':
                word = word + branchname + '>' + str(self.analyze_info.branch_90_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_90_highcut[branchname])
            else:
                word = word + '&&' + branchname + '>' + str(self.analyze_info.branch_90_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_90_highcut[branchname])
        if mcname == '95':
            if word == '':
                word = word + branchname + '>' + str(self.analyze_info.branch_95_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_95_highcut[branchname])
            else:
                word = word + '&&' + branchname + '>' + str(self.analyze_info.branch_95_lowcut[branchname]) + '&&' + branchname + '<' + str(self.analyze_info.branch_95_highcut[branchname])
        return word
