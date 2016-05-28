# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, AddressOf, TTree, TH1F, RooFit, RooWorkspace, RooRealVar, RooGaussian, RooPlot, kFALSE, kTRUE
from glob import glob
from copy import deepcopy
from AnalyzeInfo import *
from array import array
from Cuts import *
from ToyExperimentGen import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *


class DataTree:
    def __init__(self, analyzeInfo, tree, name, cross_sections, num_events, random):
        self.tree_name = name
        self.tree = tree
        self.rand = random
        self.entries = self.tree.GetEntries()
        if name == 'data':
            self.number_events = -1
            self.cross_section = -1
            self.luminosity = 176.773
            self.scaling_factor = 1
        else:
            self.number_events = num_events
            self.cross_section = cross_sections
            self.luminosity = float(self.number_events / self.cross_section)
            self.scaling_factor = float(176.773 / self.luminosity)
        #self.CreateBranchInvariantMass() # Create branch of invariant mass
        self.branches_info = analyzeInfo
        self.cuts = Cuts(self.branches_info)
        self.cuts_words = self.cuts.cuts_words
        self.branches_histograms = {branch: self.GetBranchHistogram(branch, self.branches_info.branch_numbins[branch],
                                                                    self.branches_info.branch_min[branch],
                                                                    self.branches_info.branch_max[branch])
                                    for branch in self.branches_info.branch_names}
        self.branches_histogram_no_norm = deepcopy(self.branches_histograms)
        for branch in self.branches_info.branch_names:
            self.branches_histogram_no_norm[branch].Scale(float(1)/self.scaling_factor)
        if name != 'data':
            if name == '85' or name == '90' or name == '95':
                self.toys = self.generate_toy_experiments('signal_'+name, self.branches_info.test_statistics_branch,
                                                          self.branches_info.number_toys)
            else:
                self.toys = self.generate_toy_experiments('background_'+name, self.branches_info.test_statistics_branch,
                                                          self.branches_info.number_toys)

    def __del__(self):
        print 'Deleting', self

    def GetBranchHistogram(self, branchname, nbins_histo, min_histo, max_histo):
        histogram_name = branchname + '_' + self.tree_name
        cutword = self.cuts_words[self.branches_info.monte_carlo_to_analyse]
        histogram = TH1F(histogram_name, histogram_name, int(nbins_histo + 1), float(min_histo - float(max_histo - min_histo) / float(2 * nbins_histo)), float(max_histo + float(max_histo - min_histo) / float(2 * nbins_histo)))
        histogram.SetBinErrorOption(TH1F.kPoisson)
        histogram.SetStats(kFALSE)
        self.tree.Draw('{branch}>>{histo}'.format(branch=branchname, histo=histogram_name), cutword, 'goff')
        histogram.Scale(self.scaling_factor)
        return deepcopy(histogram)

    def GetBranchHistogram2(self, branchname, nbins_histo, min_histo, max_histo):
        histogram_name = branchname + '2_' + self.tree_name
        histogram = TH1F(histogram_name, histogram_name, int(nbins_histo + 1), float(min_histo - float(max_histo - min_histo) / float(2 * nbins_histo)), float(min_histo - float(max_histo - min_histo) / float(2 * nbins_histo)))
        branch = 0
        for i in xrange(self.entries):
            self.tree.GetEntry(i)
            exec('branch = self.tree.'+branchname)
            histogram.Fill(branch)
        return deepcopy(histogram)

    # def CreateBranchInvariantMass(self):
    #     arrayIM = array('f', [0])
    #     branchIM = self.tree.Branch('invmassH', arrayIM, 'invmassH/F') # link array with branch
    #     for entry in xrange(self.entries):
    #         self.tree.GetEntry(entry)
    #         del arrayIM[:] # delete array contents
    #         xmj1 = self.tree.xmj1
    #         xmj2 = self.tree.xmj2
    #         enj1 = self.tree.enj1
    #         enj2 = self.tree.enj2
    #         acop = self.tree.acop
    #         thj1 = self.tree.thj1
    #         thj2 = self.tree.thj2
    #         # btag1 = self.tree.btag1
    #         # btag2 = self.tree.btag2
    #         # ucsdbt0 = self.tree.ucsdbt0
    #         # if btag1 > 0.5 && btag2 > 0.5:
    #         pj1 = TMath.Sqrt(enj1**2 - xmj1**2)
    #         pj2 = TMath.Sqrt(enj2**2 - xmj2**2)
    #         inv_mass = TMath.Sqrt(xmj1**2 + xmj2**2 + 2*(enj1*enj2 + pj1*pj2*(TMath.Cos(thj1)*TMath.Cos(thj2)-TMath.Sin(thj1)*TMath.Sin(thj2)*TMath.Cos(acop))))
    #         arrayIM.append(inv_mass) # append invariant mass in array
    #         branchIM.Fill() # save the content of the branch

    def generate_toy_experiments(self, type, branchname, num):
        name = type + '_' +branchname
        histo = self.branches_histogram_no_norm[branchname]
        return {i: ToyExperimentGen(self.branches_info, histo, branchname, self.rand, i, name).toy for i in xrange(num)}
