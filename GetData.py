# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile
from ROOT import TTree
from ROOT import TH1F
from glob import glob
from copy import deepcopy

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class GetData:
    def __init__(self, dic, filenames, branchName):
        self.maxEvents = {name: dic[name].GetEntries() for name in filenames}
        self.histograms = { name: self.get_histogram_from_tree(dic[name],branchName,self.maxEvents[name],name) for name in filenames}

    def get_histogram_from_tree(self,tree,branchName,maxevents,name):
        histogram = TH1F(branchName+'_'+name,'h1'+name,141,-0.5,140.5)
        branch = 0
        for i in xrange(maxevents):
            tree.GetEntry(i)
            exec('branch = tree.'+branchName)
            histogram.Fill(branch)
        return deepcopy(histogram)
