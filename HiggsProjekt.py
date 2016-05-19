# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile, TH1F, TCanvas, THStack, TLegend
from glob import glob
from copy import deepcopy
from Utils import *

class Data:

    def __init__(self, tree, name, luminosity):
        self.Tree = tree
        self.Name = name
        self.Luminosity = luminosity

class Analysis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'
        self.ResultsDir = 'Plots/'

        # dictionary of the tree name and the tree
        self.trees = self.load_trees()
        self.DataTree = self.get_tree()
        self.Luminosity = self.load_luminosities()
        self.BranchList = [br.GetName() for br in self.trees.values()[0].GetListOfBranches()]
        self.qq = self.trees['qq']
        self.BranchDict = self.load_branch_dict()
        self.data = []
        self.NEvents = 0
        self.CrossSection = 0
        self.Data = []

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        dic = {f.GetName().split('/')[-1].strip('.root').strip('higgs').strip('_'): t for f, t in zip(files, trees)}
        return deepcopy(dic)

    def load_luminosities(self):
        dic = {'qq': [2e5, 102], 'zz': [196e3, .975], 'ww': [2945e2, 3.35], 'eeqq': [594e4, 15600], 'zee': [295e2, 3.35], 'wen': [81786, 2.9]}
        lum = {key: val[0] / val[1] for key, val in dic.iteritems()}
        return lum

    def get_tree(self, tree='data'):
        assert tree in self.trees
        return self.trees[tree]

    def draw_histo(self):
        pass

    def draw_mass(self, tree_name, branch, show=True):
        assert tree_name in self.trees.keys(), 'There is no tree with name: {0}!'.format(tree_name)
        tree = self.trees[tree_name]
        assert branch in self.BranchList, 'There is no branch {0} in the tree!'.format(branch)
        h = TH1F(branch, '{typ} of {tree}'.format(tree=tree_name, typ=self.BranchDict[branch]), 70, 0, 140)
        tree.Draw('{typ}>>{typ}'.format(typ=branch), '{typ}>0'.format(typ=branch), 'goff')
        format_histo(h, x_tit='mass [GeV]', y_tit='entries')
        save_name = '{typ}_{nam}'.format(typ=self.BranchDict[branch].replace(' ', ''), nam=tree_name)
        self.Data.append(draw_histo(h, save_name, show, self.ResultsDir))

    def draw_missing_mass(self, name='data', show=True):
        self.draw_mass(tree_name=name, branch='mmis', show=show)

    def draw_visible_mass(self, name='data', show=True):
        self.draw_mass(branch='mvis', tree_name=name, show=show)

    def show_treenames(self):
        for key in self.trees.iterkeys():
            print key

    def print_all_branchvalues(self, entry=0, name='qq'):
        tree = self.get_tree(name)
        tree.GetEntry(entry)
        for branch in self.BranchList:
            print branch, tree.GetBranch(branch).GetLeaf(branch).GetValue()

    @staticmethod
    def load_branch_dict():
        dic = {}
        dic['mvis'] = 'Visible Mass'
        dic['mmis'] = 'Missing Mass'
        return dic

    def draw_bgk(self, branch='mvis'):
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
        bkg_trees = {name: tree for name, tree in self.trees.iteritems() if name != 'data' and not name.startswith('higgs')}
        legend = TLegend(.7, .7, .9, .9)
        L = sum(self.Luminosity.values())
        for name, tree in bkg_trees.iteritems():
            h = TH1F(branch, '{typ} of {tree}'.format(tree=name, typ=self.BranchDict[branch]), 70, 1, 140)
            tree.Draw('{br}>>{br}'.format(br=branch), '', 'goff')
            h.Scale(self.Luminosity[name] / L)
            h.SetLineColor(get_color())
            h.SetLineWidth(2)
            legend.AddEntry(h,h.GetTitle(), 'l')
            h_st.Add(h)
        self.Data.append(draw_histo(h_st, 'bla', True, self.ResultsDir, l=legend))



__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
