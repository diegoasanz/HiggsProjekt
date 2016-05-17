# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, TTree, TH1F
from glob import glob
from copy import deepcopy
from DataTree import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class TotalBackgrounds:
    def __init__(self, names, data_trees, branches_names, branches_nbins, branches_mins, branches_maxs):
        self.total_background_histograms_dict = {}
        for name in branches_names:
            self.accumulateHistogram(self.total_background_histograms_dict, names, data_trees, name, branches_nbins[name], branches_mins[name], branches_maxs[name])

    def accumulateHistogram(self, dictionary, names, data_trees, branch_name, branch_nbin, branch_min, branch_max):
        nbins = int(branch_nbin+1)
        hmin = branch_min - float(branch_max - branch_min) / float(2 * branch_nbin)
        hmax = branch_max + float(branch_max - branch_min) / float(2 * branch_nbin)
        h1 = TH1F(branch_name + '_background', branch_name + '_background', nbins, hmin, hmax)
        # h1.sumw2() # if weighted distribution
        for name in names:
            h1.Add(data_trees[name].GetBranchHistogram(branch_name, branch_nbin, branch_min,branch_max), data_trees[name].scaling_factor)
        dictionary[branch_name] = h1
