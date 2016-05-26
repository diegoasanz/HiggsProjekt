# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, RooFit, RooWorkspace, RooRealVar, RooGaussian, RooPlot, kTRUE, kFALSE
from glob import glob
from copy import deepcopy
from DataTree import *
from BranchInfo import *

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *


class Analysis:
    # this method is the initialization of the Analysis class. This is the constructor of the Analysis class.
    def __init__(self):
        '''
        :param self: it menas that it takes itself as parameter to initialize
        :return: this method does not return anything, it is just the constructor.
        '''

        # This is the folder name where the data is stored. Download it from the student forum page in moodle and save the data in the same path of this projekt
        self.DataFolder = 'l3higgs189/'

        # This calls the method 'load_trees' of the Analysis class, and the results are stored in the variable trees.
        # trees variable will have a dictionary with the tree name and the tree
        print_banner('Loading names of trees...', '%')
        self.names = self.get_names_trees()
        print_banner('Loading trees...', '%')
        self.trees = self.load_trees()
        self.data_name = 'data'
        self.data_tree = ''
        self.background_trees = {}
        self.background_names = []
        self.mc_higgs_trees = {}
        self.mc_higgs_names = []
        print_banner('Organizing trees on background, data, and MC...', '%')
        self.organize_trees(self.trees, self.names)
        self.cross_sections = {'eeqq': 15600, 'qq': 102, 'wen': 2.9, 'ww': 16.5, 'zee': 3.35, 'zz': 0.975, '85': 0.094, '90': 0.0667, '95': 0.0333}
        self.num_events = {'eeqq': 5940000, 'qq': 200000, 'wen': 81786, 'ww': 294500, 'zee': 29500, 'zz': 196000, '85': 3972, '90': 3973, '95': 3971}
        print_banner('Loading branches information and settings...', '%')
        self.branch_info = BranchInfo()
        self.branch_names = self.branch_info.branch_names
        self.branch_numbins = self.branch_info.branch_numbins
        self.branch_mins = self.branch_info.branch_min
        self.branch_maxs = self.branch_info.branch_max
        print_banner('Totaling the histograms of the backgrounds for each branch...', '%')
        self.background_data_trees = self.create_background_data_trees()
        self.total_background_histograms_dict = self.totalBackgrounds(self.background_names, self.background_data_trees, self.branch_names, self.branch_numbins, self.branch_mins, self.branch_maxs)
        print_banner('Creating histograms for each MC...', '%')
        self.mc_higgs_data_trees = self.create_mc_data_trees()
        self.mc_histograms_dict = self.monteCarloHistograms(self.mc_higgs_names, self.mc_higgs_data_trees, self.branch_names, self.branch_numbins, self.branch_mins, self.branch_maxs)
        # self.get_data = GetData(self.trees, self.names, 'mmis')
        # self.histograms = self.get_data.histograms
        # self.norm_histograms = self.get_data.norm_histograms
        self.stuff = []
        #   self.stack = self.stacked_histograms(self.norm_histograms[self.names], 'mmis')

    def get_names_trees(self):
        files = glob('{dir}*.root'.format(dir=self.DataFolder))
        names = [i.split('/')[-1].strip('.root').split('higgs_')[-1] for i in files]
        return names

    # This method loads the trees from the root file located at the DataFolder
    def load_trees(self):
        # 'files' is a vector of TFile. Here 'glob' looks for any file that ends with .root and makes a list out of it.
        # Each entry of the vector 'files', is a TFile that opens each of the root files inside the class' variable 'DataFoler'.
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        # 'trees' is a vector of TTree. Here for each element TFile in 'files', the tree 'h20' is extracted.
        # each entry of 'trees' has the corresponding tree of the root file in 'files'
        trees = [f.Get('h20') for f in files]
        # 'dic' is a Python dictionary that assigns each stem of the file name 'f' (from the vector 'files') with a
        # tree 't' (from the vector 'trees')
        dic = {f.GetName().split('/')[-1].strip('.root').split('higgs_')[-1]: t for f, t in zip(files, trees)}
        # returns a complete copy of this dictionary. If it was not copied, as soon as the method exits, all the information would be lost. That
        # is why, it needs to be 'deepcopied' so that this dictionary can be used outside this method.
        return deepcopy(dic)

    def organize_trees(self, dic_trees, names):
        for name in names:
            if name == self.data_name:
                self.data_tree = dic_trees[name]
            elif name.isdigit():
                self.mc_higgs_trees[name] = dic_trees[name]
                self.mc_higgs_names.append(name)
            else:
                self.background_trees[name] = dic_trees[name]
                self.background_names.append(name)

    def create_background_data_trees(self):
        dic = {name: DataTree(self.background_trees[name], name, self.cross_sections[name], self.num_events[name]) for name in self.background_names}
        return deepcopy(dic)

    def create_mc_data_trees(self):
        dic = {name: DataTree(self.mc_higgs_trees[name], name, self.cross_sections[name], self.num_events[name]) for name in self.mc_higgs_names}
        return deepcopy(dic)

    def totalBackgrounds(self, names, data_trees, branches_names, branches_nbins, branches_mins, branches_maxs):
        total_background_histograms_dict = {}
        for branch in branches_names:
            self.accumulateHistogram(total_background_histograms_dict, names, data_trees, branch, branches_nbins[branch], branches_mins[branch], branches_maxs[branch])
        return deepcopy(total_background_histograms_dict)

    def accumulateHistogram(self, dictionary, names, data_trees, branch_name, branch_nbin, branch_min, branch_max):
        nbins = int(branch_nbin + 1)
        hmin = branch_min - float(branch_max - branch_min) / float(2 * branch_nbin)
        hmax = branch_max + float(branch_max - branch_min) / float(2 * branch_nbin)
        histo_name = branch_name + '_background'
        h1 = TH1F(histo_name, histo_name, nbins, hmin, hmax)
        h1.SetBinErrorOption(TH1F.kPoisson)
        # h1.sumw2() # if weighted distribution
        for name in names:
            h2 = data_trees[name].branches_histograms[branch_name]
            # scale = data_trees[name].scaling_factor
            # h1.Add(h2, scale)
            h1.Add(h2)
        h1.SetLineColor(TColor.kRed)
        h1.SetFillColor(TColor.kRed)
        dictionary[branch_name] = h1

    def monteCarloHistograms(self, names, data_trees, branch_names, branches_nbins, branches_mins, branches_maxs):
        mc_histograms_dict = {name: {branch: data_trees[name].branches_histograms[branch] for branch in branch_names} for name in names}
        for name in names:
            for branch in branch_names:
                # mc_histograms_dict[name][branch].Scale(data_trees[name].scaling_factor)
                mc_histograms_dict[name][branch].SetLineColor(TColor.kBlue)
                mc_histograms_dict[name][branch].SetFillColor(TColor.kBlue)
                mc_histograms_dict[name][branch].SetBinErrorOption(TH1F.kPoisson)
        return deepcopy(mc_histograms_dict)

    def overlayMCBckgrndSignal(self, mcname, branchname, doLogY=kTRUE):
        self.stacked_histograms(self.total_background_histograms_dict[branchname],self.mc_histograms_dict[mcname][branchname], 'total_' + mcname + '_' + branchname, doLogY)

    def compareMCBckgrndSignal(self, backgroundname, mcname, branchname, doLogY=kFALSE):
        self.stacked_histograms(self.background_data_trees[backgroundname].branches_histograms[branchname],self.mc_histograms_dict[mcname][branchname], mcname + '_' + branchname, doLogY)

    def stacked_histograms(self, backgroundHisto, mcHisto, branchname, doLogY):
        c1 = TCanvas('c1', 'c1', 1)
        c1.cd()
        s1 = THStack(branchname + '_stack', 's1_' + branchname)
        s1.Add(backgroundHisto)
        s1.Add(mcHisto)
        s1.Draw()
        c1.BuildLegend()
        if doLogY:
            c1.SetLogy()
        self.stuff.append(s1)


# This is the main that it is called if you start the python script
if __name__ == '__main__':
    # print_banner is located in Utils Class found in Utils.py. This Class is for useful utilities.
    # print_banner is a nice way to print the information in terminal
    print_banner('STARTING HIGGS ANALYSIS')
    # this creates an instance (object) of the Analysis class that is defined above.
    z = Analysis()
