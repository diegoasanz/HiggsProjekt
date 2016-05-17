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
        self.names = self.get_names_trees()
        self.trees = self.load_trees()
        self.data_name = 'data'
        self.data_tree = ''
        self.background_trees = {}
        self.background_names = []
        self.mc_higgs_trees = {}
        self.mc_higgs_names = []
        self.organize_trees(self.trees,self.names)
        self.cross_sections = {'eeqq': 15600, 'qq': 102, 'wen': 2.9, 'ww': 16.5, 'zee': 3.35, 'zz': 0.975, '85': 0.094, '90': 0.0667, '95': 0.0333}
        self.num_events = {'eeqq': 5940000, 'qq': 200000, 'wen': 81786, 'ww': 294500, 'zee': 29500, 'zz': 196000, '85': 3972, '90': 3973, '95': 3971}
        self.branch_info = BranchInfo()
        self.branch_numbins = self.branch_info.branch_numbins
        self.branch_min = self.branch_info.branch_min
        self.branch_max = self.branch_info.branch_max
        self.background_data_trees = self.create_background_data_trees()
        self.get_data = GetData(self.trees, self.names, 'mmis')
        self.histograms = self.get_data.histograms
        self.norm_histograms = self.get_data.norm_histograms
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

    def stacked_histograms(self, histograms, branchname):
        s1 = THStack(branchname+'stack', 's1'+branchname)
        s1.Add(histograms)
        s1.Draw('nostack')

    def organize_trees(self,dic_trees,names):
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
        dic = {name: DataTree(self.background_trees[name],name,self.cross_sections[name],self.num_events[name]) for name in self.background_names}
        return deepcopy(dic)

# This is the main that it is called if you start the python script
if __name__ == '__main__':
    # print_banner is located in Utils Class found in Utils.py. This Class is for useful utilities.
    # print_banner is a nice way to print the information in terminal
    print_banner('STARTING HIGGS ANALYSIS')
    # this creates an instance (object) of the Analysis class that is defined above.
    z = Analysis()
