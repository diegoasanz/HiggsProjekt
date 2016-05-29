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
from HiggsProjekt import *
import os


__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *