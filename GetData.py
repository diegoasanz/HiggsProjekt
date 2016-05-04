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
    def __init__(self, dic, filenames, branchname):
        self.max_events = {name: dic[name].GetEntries() for name in filenames}
        self.cross_section = [3.35, 16.5, 0.0333, 15600, 102, 0.094, 2.9, 0.975, -1, 0.0667]  # [8] data cross section unknown
        self.scale = {name: cs for name, cs in zip(filenames, self.cross_section)}
        self.histograms = {name: self.get_histogram_from_tree(dic[name], branchname, self.max_events[name], name) for name in filenames}
        self.norm_histograms = {name: self.get_normalized_historgram(self.histograms[name], self.scale[name]) for name in filenames}


    def get_histogram_from_tree(self, tree, branchname, maxevents, name):
        histogram = TH1F(branchname+'_'+name, 'h1'+name, 141, -0.5, 140.5)
        branch = 0
        for i in xrange(maxevents):
            tree.GetEntry(i)
            exec('branch = tree.'+branchname)
            histogram.Fill(branch)
        return deepcopy(histogram)

    def get_normalized_historgram(self, histogram, scale):
        norm_histogram = histogram.Scale(1 / scale)
        return deepcopy(norm_histogram)