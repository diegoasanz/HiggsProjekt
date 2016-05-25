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

    def get_histo(self, branch='mvis', scaled=False):
        name = '{br}_{sc}scaled'.format(br=branch, sc='' if scaled else 'un')
        if name in self.Histos:
            return self.Histos[name]
        assert branch in self.Branches, 'There is no branch {0} in the tree!'.format(branch)
        typ = BranchDict[branch] if branch in BranchDict else branch
        h = TH1F(name, '{typ} of {tree}'.format(tree=self.Name, typ=typ), 28, 0, 140)
        self.Tree.Draw('{br}>>{typ}'.format(br=branch, typ=name), '{br}>0'.format(br=branch), 'goff')
        format_histo(h, x_tit='Mass [GeV]', y_tit='Number of Entries', y_off=1.5)
        h.Scale(176.773 / self.Luminosity) if scaled else do_nothing()
        self.Histos[branch] = h
        return h


class Analysis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'
        self.ResultsDir = 'Plots/'

        # trees
        trees = self.load_trees()
        luminosity = self.load_luminosities()
        self.Data = Data(trees['data'], 'data', 176.773)
        self.Background = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name != 'data' and not name.startswith('higgs')}
        # self.Signal = [Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name.startswith('higgs')]
        self.Signal = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name.startswith('higgs')}

        self.Stuff = []

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        dic = {f.GetName().split('/')[-1].strip('.root').strip('higgs').strip('_'): t for f, t in zip(files, trees)}
        return deepcopy(dic)

    @staticmethod
    def load_luminosities():
        dic = {'qq': [2e5, 102], 'zz': [196e3, .975], 'ww': [2945e2, 3.35], 'eeqq': [594e4, 15600], 'zee': [295e2, 3.35], 'wen': [81786, 2.9], 'higgs_85': [3972, .094], 'higgs_90': [3973, .0667],
               'higgs_95': [3973, .0333]}
        lum = {key: val[0] / val[1] for key, val in dic.iteritems()}
        return lum

    def draw_data(self, branch='mvis', show=True, scaled=True):
        h = self.Data.get_histo(branch, scaled=scaled)
        h.SetFillColor(425)
        self.Stuff.append(save_histo(h, 'Data{0}'.format(branch.title()), show, self.ResultsDir))
        return h

    def draw_signal(self, sig='85', branch='mvis', show=True):
        name = 'higgs_{sig}'.format(sig=sig)
        if name not in self.Signal:
            log_warning('The signal "{sig}" does not exist!'.format(sig=sig))
            return
        h = self.Signal[name].get_histo(branch, scaled=True)
        h.SetFillColor(625)
        self.Stuff.append(save_histo(h, 'Signal{0}'.format(branch.title()), show, self.ResultsDir, lm=.12))
        return h

    def draw_bkg(self, bkg='qq', branch='mvis', show=True):
        if bkg not in self.Background:
            log_warning('The background "{sig}" does not exist!'.format(sig=bkg))
            return
        h = self.Background[bkg].get_histo(branch)
        h.SetFillColor(425)
        self.Stuff.append(save_histo(h, 'Background{0}'.format(branch.title()), show, self.ResultsDir, lm=.12))
        return h

    def draw_full_bkg(self, branch='mvis', show=True):
        histos = [bkg.get_histo(branch, scaled=True, fac=1000) for bkg in self.Background.itervalues()]
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
        legend = TLegend(.7, .7, .9, .9)
        bkg = TH1F('h_bkg', 'Full Background', 28, 0, 140)
        for h in histos:
            h.SetLineColor(get_color())
            h.SetLineWidth(2)
            legend.AddEntry(h, h.GetTitle(), 'l')
            h_st.Add(h)
            bkg.Add(h)
        format_histo(bkg, x_tit='Mass [GeV]', y_tit='Number of Entries', fill_color=393)  # 425
        self.Stuff.append(save_histo(h_st, 'FullBkg', show, self.ResultsDir, l=legend))
        return bkg

    def draw_mc(self, branch='mvis', show=True, sig='85'):
        sig = self.draw_signal(sig, branch, False)
        bkg = self.draw_full_bkg(branch, False)
        h_st = THStack('mc', 'Signal and Background {nam}'.format(nam=branch))
        for h in [sig, bkg]:
            h_st.Add(h)
        self.Stuff.append(save_histo(h_st, 'MC', show, self.ResultsDir, draw_opt='nostack'))

    def draw_lb(self):
        gr = make_tgrapherrors('gr_ll', 'Log Likelihood')
        h_bkg = self.draw_full_bkg(show=False)
        h_data = self.draw_data(show=False)
        bk = h_bkg.GetBinContent(h_bkg.FindBin(85))
        n = h_data.GetBinContent(h_bkg.FindBin(85))
        ll = 2 * sk
        for ibin in xrange(h_sig.GetNbinsX()):
            sj = h_sig.GetBinContent(ibin)
            bj = h_bkg.GetBinContent(ibin)
            if not (bj and sj):
                ll += log(1 + sk * sj / (bk * bj))
        print ll


__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
