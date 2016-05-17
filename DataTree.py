# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile
from ROOT import TTree
from ROOT import TH1F
from glob import glob
from copy import deepcopy
from BranchInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class DataTree:
    def __init__(self,tree,name,cross_sections,num_events):
        self.tree_name = name
        self.tree = tree
        if name == 'data':
            self.number_events = -1
            self.cross_section = -1
            self.luminosity = 176.773
            self.scaling_factor = 1
        else:
            self.number_events = num_events
            self.cross_section = cross_sections
            self.luminosity = self.number_events/self.cross_section
            self.scaling_factor = 176.773/self.luminosity

    def GetBranchHistogram(self,branchname,nbins_histo,min_histo,max_histo):
        histogram_name = branchname+'_'+self.tree_name
        histogram = TH1F(histogram_name,histogram_name,int(nbins_histo+1),float(min_histo-float(max_histo-min_histo)/float(2*nbins_histo)),float(max_histo+float(max_histo-min_histo)/float(2*nbins_histo)))
        self.tree.Draw('{branch}>>{histo}'.format(branch=branchname, histo=histogram_name), '', 'goff')
        return deepcopy(histogram)