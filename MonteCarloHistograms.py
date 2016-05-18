# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack
from GetData import *
from glob import glob
from copy import deepcopy
from DataTree import *
from BranchInfo import *
from TotalBackgrounds import *
from Utils import *

__author__ = 'Pin-Jung & Diego Alejandro'

class MonteCarloHistograms:
    def __init__(self, names, data_trees, branch_names, branches_nbins, branches_mins, branches_maxs):
        self.mc_histograms_dict = {name: {branch: data_trees[name].GetBranchHistogram(branch, branches_nbins[branch], branches_mins[branch], branches_maxs[branch]) for branch in branch_names} for name in names}
