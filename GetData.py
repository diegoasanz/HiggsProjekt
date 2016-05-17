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
        self.cross_section = [3.35, 16.5, 0.0333, 15600, 102, 0.094, 2.9, 0.975, 1, 0.0667]  # [8] data has no cross section
        self.num_evts = [29500, 294500, 3971, 5940000, 200000, 3972, 81786, 196000, 1, 3973]  # [8] data just need to be normalized
        self.lum = {name: lum for name, lum in zip(filenames, (self.num_evts[i] / self.cross_section[i] for i in range (0, 10)))}  # normalized by integrated luminosity
        self.scale = {name: 176.773/self.lum[name] for name in filenames}
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
        print scale
        histogram.Scale(scale)
        norm_histogram=histogram
        return deepcopy(norm_histogram)