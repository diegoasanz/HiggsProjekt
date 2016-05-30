# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile, TH1F, THStack, TLegend, TCut, gROOT, gRandom
from glob import glob
from copy import deepcopy
from numpy import log
from Utils import *
from Cut import Cut, significance, purity, efficiency
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed


sig_col = 810  # 598  # 625
bkg_col = 1  # 418  # 619
dat_col = 425


class Data:

    def __init__(self, tree, name, lum):
        self.Tree = tree
        self.Name = name
        self.Luminosity = lum

        self.Branches = [br.GetName() for br in self.Tree.GetListOfBranches()]
        self.Toys = []

        self.Histos = {}

    def get_histo(self, branch='mvis', scaled=True, cut_string='', nbins=100, xmax=140):
        cut = TCut('cut', 'mvis>0')
        cut += TCut(cut_string)
        name = '{br}'.format(br=branch)
        name_sc = '{0}_scaled'.format(name)
        # if name in self.Histos:
        #     return self.Histos[name] if not scaled else self.Histos[name_sc]
        assert branch in self.Branches, 'There is no branch {0} in the tree!'.format(branch)
        typ = BranchDict[branch] if branch in BranchDict else branch
        h = TH1F(name, '{typ} of {tree}'.format(tree=self.Name, typ=typ), nbins, 0, xmax)
        self.Tree.Draw('{br}>>{typ}'.format(br=branch, typ=name), cut, 'goff')
        format_histo(h, x_tit='Mass [GeV]', y_tit='Number of Entries', y_off=1.5, stats=0)
        self.Histos[branch] = h
        h.SetBarWidth(.9)
        h_scaled = h.Clone()
        h.SetName(name_sc)
        h_scaled.Scale(176.773 / self.Luminosity)
        self.Histos[name_sc] = h_scaled
        return h_scaled if scaled else h

    def get_mass_histo(self, branch='mvis', scaled=True, cut_string=''):
        return self.get_histo(branch, scaled, cut_string, 28, 140)

    def generate_toys(self, h, ntoys=1):
        toy = None
        for i in xrange(ntoys):
            toy = h.Clone()
            toy.Reset()
            for ibin in xrange(h.GetNbinsX()):
                toy.SetBinContent(ibin, gRandom.Poisson(h.GetBinContent(ibin)))
            toy.Scale(176.773 / self.Luminosity)
        return toy

    def reload_tree(self, tree):
        self.Tree = tree


class Analysis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'
        self.ResultsDir = 'Plots/'

        # trees
        trees = self.load_trees()
        luminosity = self.load_luminosities()
        self.Data = Data(trees['data'], 'data', 176.773)
        self.Background = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name != 'data' and not name.startswith('higgs')}
        self.Signal = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name.startswith('higgs')}

        self.Cut = {sig.strip('higgs_'): Cut(self, sig.strip('higgs_')) for sig in self.Signal}

        self.Stuff = []

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        dic = {f.GetName().split('/')[-1].strip('.root').strip('higgs').strip('_'): t for f, t in zip(files, trees)}
        return deepcopy(dic)

    def reload_trees(self):
        trees = self.load_trees()
        for nam, sig in self.Signal.iteritems():
            sig.reload_tree(trees[nam])

    def reload_tree(self, sig):
        trees = self.load_trees()
        if sig in self.Signal:
            self.Signal[sig].reload_tree(trees[sig])
        else:
            self.Background[sig].reload_tree(trees[sig])

    @staticmethod
    def load_luminosities():
        dic = {'qq': [2e5, 102], 'zz': [196e3, .975], 'ww': [2945e2, 16.5], 'eeqq': [594e4, 15600], 'zee': [295e2, 3.35], 'wen': [81786, 2.9], 'higgs_85': [3972, .094], 'higgs_90': [3973, .0667],
               'higgs_95': [3973, .0333]}
        lum = {key: val[0] / val[1] for key, val in dic.iteritems()}
        return lum

    def draw_data(self, branch='mvis', show=True, scaled=True, nbins=28, xmax=140, cut=''):
        h = self.Data.get_histo(branch, scaled=scaled, nbins=nbins, xmax=xmax, cut_string=cut)
        h.SetFillColor(dat_col)
        self.Stuff.append(save_histo(h, 'Data{0}'.format(branch.title()), show, self.ResultsDir, draw_opt='bar2'))
        return h

    def draw_signal(self, sig='85', branch='mvis', show=True, scale=True, cut='', nbins=28, xmax=140):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        name = 'higgs_{sig}'.format(sig=sig)
        if name not in self.Signal:
            log_warning('The signal "{sig}" does not exist!'.format(sig=sig))
            return
        h = self.Signal[name].get_histo(branch, scaled=scale, cut_string=cut, nbins=nbins, xmax=xmax)
        h.SetFillColor(sig_col)
        self.Stuff.append(save_histo(h, 'Signal{0}'.format(branch.title()), show, self.ResultsDir, lm=.12, draw_opt='bar2'))
        self.reload_tree(name)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        return h

    def draw_bkg(self, bkg='qq', branch='mvis', show=True, scale=True, nbins=28, xmax=140, cut=''):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        if bkg not in self.Background:
            log_warning('The background "{sig}" does not exist!'.format(sig=bkg))
            return
        h = self.Background[bkg].get_histo(branch, scaled=scale, nbins=nbins, xmax=xmax, cut_string=cut)
        h.SetFillColor(bkg_col)
        self.Stuff.append(save_histo(h, 'Background{0}'.format(branch.title()), show, self.ResultsDir, lm=.12, draw_opt='bar2'))
        self.reload_tree(bkg)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        return h

    def draw_full_bkg(self, branch='mvis', show=True, nbins=28, xmax=140, cut='', scale=False):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        histos = [self.draw_bkg(bkg, branch=branch, show=False, nbins=nbins, xmax=xmax, cut=cut, scale=scale) for bkg in self.Background]
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
        legend = TLegend(.7, .7, .9, .9)
        h0 = histos[0]
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        bkg = TH1F('h_bkg', 'Full Background', h0.GetNbinsX(), h0.GetXaxis().GetXmin(), h0.GetXaxis().GetXmax())
        for h in histos:
            h.SetLineColor(get_color())
            h.SetLineWidth(2)
            legend.AddEntry(h, h.GetTitle(), 'l')
            h_st.Add(h)
            bkg.Add(h)
        format_histo(bkg, x_tit='Mass [GeV]', y_tit='Number of Entries', y_off=1.2, fill_color=bkg_col, stats=0)  # 425
        bkg.SetBarWidth(.9)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        self.Stuff.append(save_histo(h_st, 'AllBkg', False, self.ResultsDir, l=legend))
        self.Stuff.append(save_histo(bkg, 'FullBkg', show, self.ResultsDir, draw_opt='bar2'))
        return bkg

    def draw_mc(self, branch='mvis', show=True, sig_name='85', stack=False, nbins=28, xmax=140, logy=False):
        sig = self.draw_signal(sig_name, branch, False, scale=True, nbins=nbins, xmax=xmax)
        bkg = self.draw_full_bkg(branch, False, nbins=nbins, xmax=xmax)
        leg = make_legend(x1=.12, y2=.88, w=.3)
        leg.AddEntry(sig, 'Signal higgs_{0}'.format(sig_name), 'f')
        leg.AddEntry(bkg, 'Full Background', 'f')
        save_name = 'MC_{0}'.format(branch)
        if not stack:
            bkg.SetTitle('Monte Carlo for {0}'.format(branch))
            sig.SetBarOffset(.5)
            sig.SetBarWidth(.49)
            bkg.SetBarWidth(.49)
            c = TCanvas('c', 'c', 2000, 2000)
            c.SetLogy() if logy else do_nothing()
            bkg.Draw('bar2')
            sig.Draw('bar2same')
            leg.Draw()
            save_plots(save_name, self.ResultsDir)
            self.Stuff.append([c, bkg, sig, leg])
        else:
            h_st = THStack('mc', 'Signal and Background for {nam};{nam};Scaled Number of Entries'.format(nam=branch))
            for h in [bkg, sig]:
                h_st.Add(h)
            gROOT.SetBatch(1)
            h_st.Draw()
            h_st.GetYaxis().SetTitleOffset(1.3)
            self.Stuff.append(save_histo(h_st, save_name, show, self.ResultsDir, draw_opt='nostack', l=leg, logy=logy))

    def draw_all_branches(self, sig='85'):
        for branch in self.Data.Branches:
            cut = ''
            if branch in ['mvis', 'mmis']:
                cut = '{br}>0'.format(br=branch)
            self.Signal['higgs_{0}'.format(sig)].Tree.Draw(branch, cut)
            h = gROOT.FindObject('htemp')
            save_histo(h, 'Signal{0}'.format(branch.title()), False, self.ResultsDir, lm=.12)

    def no_cut_results(self, sig='85'):
        print 'Results without any cut:'
        sig = self.draw_signal(sig, show=False)
        bkg = self.draw_full_bkg(show=False)
        print '  Purity:'.ljust(15), '{0:6.2f}%'.format(purity(sig, bkg) * 100.)
        print '  Significance:'.ljust(15), '{0:6.2f}%'.format(significance(sig, bkg) * 100.)
        print '  Efficiency:'.ljust(15), '{0:6.2f}%'.format(100)

    def final_cut_results(self, sig='85'):
        print 'Results with all cuts:'
        cut = self.Cut[sig].AllCut
        sig_nocut = self.draw_signal(sig, show=False)
        sig = self.draw_signal(sig, cut=cut, show=False)
        bkg = self.draw_full_bkg(cut=cut, show=False)
        print '  Purity:'.ljust(15), '{0:6.2f}%'.format(purity(sig, bkg) * 100.)
        print '  Significance:'.ljust(15), '{0:6.2f}%'.format(significance(sig, bkg) * 100.)
        print '  Efficiency:'.ljust(15), '{0:6.2f}%'.format(efficiency(sig, sig_nocut) * 100.)

    # def test(self, show=True):
    #     cut = self.Cut['85'].AllCut
    #     data_nocut = self.draw_data(show=False)
    #     data = self.draw_data(cut=cut, show=False)
    #     h1 = TH1F('h', 'h', 10, 0, .5)
    #     h2 = h1.Clone
    #     for ibin in xrange(data_nocut.GetNbinsX()):
    #         s = data.GetBinContent(ibin)
    #         b = data_nocut.GetBinContent(ibin) - data.GetBinContent(ibin)
    #         print ibin, s, b
    #         if b:
    #             h1.Fill(log(1 + s / b))
    #             print log(1 + s / b)
    #     format_histo(h1, x_tit='ln(1 + s/b)', y_tit='Number of Entries')
    #     self.Stuff.append(save_histo(h1, 'test', show, self.ResultsDir, lm=1.2, draw_opt='e1'))

    @staticmethod
    def neg_log_lr(h_sig, h_bkg, b_seed, s_seed):
        pdf_s = s_seed.Clone()
        pdf_s.Scale(1 / s_seed.Integral())
        pdf_b = b_seed.Clone()
        pdf_b.Scale(1 / b_seed.Integral())
        s = h_sig.Integral()
        b = h_bkg.Integral()
        ll = 2 * s
        for ibin in xrange(h_sig.GetNbinsX()):
            if pdf_b.GetBinContent(ibin):
                ll -= log(1 + s * pdf_s.GetBinContent(ibin) / (b * pdf_b.GetBinContent(ibin)))
        return ll

    def observed_ll(self):
        cut = self.Cut['85'].AllCut
        sig = self.draw_data(cut=cut, show=False)
        bkg = self.draw_data(show=False)
        bkg.Add(sig, -1)
        ll = self.neg_log_lr(sig, bkg, bkg, sig)
        print ll
        return ll

    def h0_ll(self, sig_name='85', n=10000):
        cut = self.Cut[sig_name].AllCut
        sig_seed = self.draw_signal(sig=sig_name, show=False, cut=cut, scale=False)
        bkg = self.draw_full_bkg(show=False, cut=cut)
        ll = self.neg_log_lr(sig_seed, bkg, bkg, sig_seed)
        h = TH1F('h', 'h', 100, -18, -15)
        h.Fill(ll)
        pbar = ProgressBar(widgets=[Percentage(), ' ', Bar(), '', ETA(), ' ', FileTransferSpeed()], maxval=n-1).start()
        for i in xrange(n - 1):
            # print '\r{0:02d}'.format(i),
            pbar.update(i+1)
            sig = self.Signal['higgs_{0}'.format(sig_name)].generate_toys(sig_seed)
            ll = self.neg_log_lr(sig, bkg, bkg, sig_seed)
            h.Fill(ll)
        format_histo(h, x_tit='q', y_tit='Number of Entries', y_off=1.3)
        self.Stuff.append(save_histo(h, 'test', 1, self.ResultsDir))
        pbar.finish()


__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
