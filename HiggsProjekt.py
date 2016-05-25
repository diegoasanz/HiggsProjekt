# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile, TH1F, THStack, TLegend
from glob import glob
from copy import deepcopy
from numpy import log
from Utils import *


class Data:

    def __init__(self, tree, name, lum):
        self.Tree = tree
        self.Name = name
        self.Luminosity = lum

        self.Branches = [br.GetName() for br in self.Tree.GetListOfBranches()]

        self.Histos = {}

    def get_histo(self, branch='mvis', scaled=False, fac=1000):
        name = '{br}_{sc}scaled'.format(br=branch, sc='' if scaled else 'un')
        if name in self.Histos:
            return self.Histos[name]
        assert branch in self.Branches, 'There is no branch {0} in the tree!'.format(branch)
        typ = BranchDict[branch] if branch in BranchDict else branch
        h = TH1F(branch, '{typ} of {tree}'.format(tree=self.Name, typ=typ), 28, 0, 140)
        self.Tree.Draw('{typ}>>{typ}'.format(typ=branch), '{typ}>0'.format(typ=branch), 'goff')
        format_histo(h, x_tit='Mass [GeV]', y_tit='Number of Entries', y_off=1.5)
        h.Scale(self.Luminosity / full_lum) if scaled else do_nothing()
        self.Histos[branch] = h
        return h


class Analysis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'
        self.ResultsDir = 'Plots/'

        # trees
        trees = self.load_trees()
        luminosity = self.load_luminosities()
        self.Data = Data(trees['data'], 'data', 176e-3)
        self.Background = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name != 'data' and not name.startswith('higgs')}
        # self.Signal = [Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name.startswith('higgs')]
        self.Signal = {name: Data(tree, name, 0) for name, tree in trees.iteritems() if name.startswith('higgs')}

        self.Stuff = []

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        dic = {f.GetName().split('/')[-1].strip('.root').strip('higgs').strip('_'): t for f, t in zip(files, trees)}
        return deepcopy(dic)

    def load_luminosities(self):
        dic = {'qq': [2e5, 102], 'zz': [196e3, .975], 'ww': [2945e2, 3.35], 'eeqq': [594e4, 15600], 'zee': [295e2, 3.35], 'wen': [81786, 2.9]}
        lum = {key: val[0] / val[1] for key, val in dic.iteritems()}
        return lum

    def draw_data(self, branch='mvis', show=True):
        h = self.Data.get_histo(branch)
        h.SetFillColor(393)
        self.Stuff.append(save_histo(h, 'Data{0}'.format(branch.title()), show, self.ResultsDir))
        return h

    def draw_signal(self, sig='85', branch='mvis', show=True):
        name = 'higgs_{sig}'.format(sig=sig)
        if not name in self.Signal:
            log_warning('The signal "{sig}" does not exist!'.format(sig=sig))
            return
        h = self.Signal[name].get_histo(branch)
        h.SetFillColor(625)
        self.Stuff.append(save_histo(h, 'Signal{0}'.format(branch.title()), show, self.ResultsDir, lm=.12))
        return h

    def draw_bkg(self, bkg='qq', branch='mvis', show=True):
        if not bkg in self.Background:
            log_warning('The background "{sig}" does not exist!'.format(sig=bkg))
            return
        h = self.Background[bkg].get_histo(branch)
        h.SetFillColor(425)
        self.Stuff.append(save_histo(h, 'Background{0}'.format(branch.title()), show, self.ResultsDir, lm=.12))
        return h

    def draw_full_bkg(self, branch='mvis', show=True):
        full_lum = sum([bkg.Luminosity for bkg in self.Background.itervalues()])
        histos = [bkg.get_histo(branch, scaled=True, full_lum=full_lum) for bkg in self.Background.itervalues()]
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
        legend = TLegend(.7, .7, .9, .9)
        bkg = TH1F('h_bkg', 'Full Background', 28, 0, 140)
        for h in histos:
            h.SetLineColor(get_color())
            h.SetLineWidth(2)
            legend.AddEntry(h,h.GetTitle(), 'l')
            h_st.Add(h)
            bkg.Add(h)
        format_histo(bkg, x_tit='Mass [GeV]', y_tit='Number of Entries', fill_color=425)
        self.Stuff.append(save_histo(h_st, 'FullBkg', show, self.ResultsDir, l=legend))
        return bkg

    def draw_mc(self, branch='mvis', show=True, sig='85'):
        sig = self.draw_signal(sig, branch, False)
        bkg = self.draw_full_bkg(branch, False)
        h_st = THStack('mc', 'Signal and Background {nam}'.format(nam=branch))
        for h in [sig, bkg]:
            h_st.Add(h)
        self.Stuff.append(save_histo(h_st, 'MC', show, self.ResultsDir, draw_opt='nostack'))


    def print_all_branchvalues(self, entry=0, name='qq'):
        tree = self.get_tree(name)
        tree.GetEntry(entry)
        for branch in self.BranchList:
            print branch, tree.GetBranch(branch).GetLeaf(branch).GetValue()

    @staticmethod
    def load_branch_dict():
        BranchDict = {'mvis': 'Visible Mass', 'mmis': 'Missing Mass'}
        return dic

    def draw_bgk(self, branch='mvis'):
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
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
        self.Data.append(save_histo(h_st, 'bla', True, self.ResultsDir, l=legend))



__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
