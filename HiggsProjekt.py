# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile, TH1F, THStack, TLegend, TCut, gROOT, gRandom, TMultiGraph
from glob import glob
from numpy import log, array, zeros
from Utils import *
from Cut import Cut, significance, purity, efficiency
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
from collections import OrderedDict


sig_col = 417  # 598  # 625
bkg_col = 810  # 418  # 619
dat_col = 425
verbose = False


class Data:

    def __init__(self, tree, name, lum):
        self.Tree = tree
        self.Name = name
        self.Luminosity = lum

        self.Branches = [br.GetName() for br in self.Tree.GetListOfBranches()]
        self.Toys = []

        self.Histos = {}

    def get_histo(self, branch='mvis', scaled=True, cut_string='', nbins=100, xmax=140, xmin=0):
        cut = TCut('cut', 'mvis>0')
        cut += TCut(cut_string)
        name = '{br}'.format(br=branch)
        name_sc = '{0}_scaled'.format(name)
        # if name in self.Histos:
        #     return self.Histos[name] if not scaled else self.Histos[name_sc]
        assert branch in self.Branches, 'There is no branch {0} in the tree!'.format(branch)
        typ = BranchDict[branch] if branch in BranchDict else branch
        h = TH1F(name, '{typ} of {tree}'.format(tree=self.Name, typ=typ), (xmax - xmin) / nbins, xmin, xmax)
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

        self.Files = None

        # trees
        trees = self.load_trees()
        luminosity = self.load_luminosities()
        self.Data = Data(trees['data'], 'data', 176.773)
        self.Background = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name != 'data' and not name.startswith('higgs')}
        self.Signal = {name: Data(tree, name, luminosity[name]) for name, tree in trees.iteritems() if name.startswith('higgs')}

        self.Cut = {sig.strip('higgs_'): Cut(self, sig.strip('higgs_')) for sig in self.Signal}
        self.AllCut = self.Cut['85'].AllCut

        self.Stuff = []
        self.SB = {}
        self.B = {}
        self.Obs = {}

    def load_trees(self):
        self.Files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees1 = [f.Get('h20') for f in self.Files]
        dic = {f.GetName().split('/')[-1].strip('.root').strip('higgs').strip('_'): t for f, t in zip(self.Files, trees1)}
        return dic

    # def reload_trees(self):
    #     trees = self.load_trees()
    #     for nam, sig in self.Signal.iteritems():
    #         sig.reload_tree(trees[nam])
    #
    # def reload_tree(self, sig):
    #     trees = self.load_trees()
    #     if sig in self.Signal:
    #         self.Signal[sig].reload_tree(trees[sig])
    #     else:
    #         self.Background[sig].reload_tree(trees[sig])

    @staticmethod
    def load_luminosities():
        dic = {'qq': [2e5, 102], 'zz': [196e3, .975], 'ww': [2945e2, 16.5], 'eeqq': [594e4, 15600], 'zee': [295e2, 3.35], 'wen': [81786, 2.9], 'higgs_85': [3972, .094], 'higgs_90': [3973, .0667],
               'higgs_95': [3973, .0333]}
        lum = {key: val[0] / val[1] for key, val in dic.iteritems()}
        return lum

    def draw_data(self, branch='mvis', show=True, scaled=True, nbins=2, xmax=120, cut='', draw_opt='e1', xmin=40):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        h = self.Data.get_histo(branch, scaled=scaled, nbins=nbins, xmax=xmax, cut_string=cut, xmin=xmin)
        h.SetFillColor(dat_col)
        self.Stuff.append(save_histo(h, 'Data{0}'.format(branch.title()), show, self.ResultsDir, draw_opt=draw_opt))
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        return h

    def draw_signal(self, sig='85', branch='mvis', show=True, scale=True, cut='', nbins=2, xmax=120, draw_opt='', xmin=40):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        name = 'higgs_{sig}'.format(sig=sig)
        if name not in self.Signal:
            log_warning('The signal "{sig}" does not exist!'.format(sig=sig))
            return
        h = self.Signal[name].get_histo(branch, scaled=scale, cut_string=cut, nbins=nbins, xmax=xmax, xmin=xmin)
        h.SetFillColor(sig_col)
        self.Stuff.append(save_histo(h, 'Signal{0}'.format(branch.title()), show, self.ResultsDir, lm=.12, draw_opt=draw_opt))
        # self.reload_tree(name)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        return h

    def draw_bkg(self, bkg='qq', branch='mvis', show=True, scale=True, nbins=2, xmax=120, cut='', xmin=20):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        if bkg not in self.Background:
            log_warning('The background "{sig}" does not exist!'.format(sig=bkg))
            return
        h = self.Background[bkg].get_histo(branch, scaled=scale, nbins=nbins, xmax=xmax, cut_string=cut, xmin=xmin)
        h.SetFillColor(bkg_col)
        self.Stuff.append(save_histo(h, 'Background{0}'.format(branch.title()), show, self.ResultsDir, lm=.12, draw_opt='bar2'))
        # self.reload_tree(bkg)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        return h

    def draw_full_bkg(self, branch='mvis', show=True, nbins=2, xmax=120, cut='', scale=True, xmin=40, draw_opt=''):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        histos = [self.draw_bkg(bkg, branch=branch, show=False, nbins=nbins, xmax=xmax, cut=cut, scale=scale, xmin=xmin) for bkg in self.Background]
        h_st = THStack('bkg', 'Background {nam}'.format(nam=branch))
        legend = TLegend(.7, .7, .9, .9)
        h0 = histos[0]
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        bkg = TH1F('h_bkg', 'Background', h0.GetNbinsX(), h0.GetXaxis().GetXmin(), h0.GetXaxis().GetXmax())
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
        self.Stuff.append(save_histo(bkg, 'FullBkg', show, self.ResultsDir, draw_opt=draw_opt))
        return bkg

    def draw_all(self, sig_name='85', nbins=2):
        sig_name = str(sig_name)
        cut = z.Cut[sig_name].AllCut
        data = self.draw_data(nbins=nbins, show=False, cut=cut)
        sig = self.draw_signal(sig_name, show=False, scale=True, nbins=nbins, cut=cut)
        bkg = self.draw_full_bkg(show=False, nbins=nbins, cut=cut)
        sig.Add(bkg)
        h_st = THStack('mc', 'Signal and Background for m_{{H}} = {m} GeV;{nam};Scaled Number of Entries'.format(nam='Visible Mass [GeV]', m=sig_name))
        leg = make_legend(x1=.12, y2=.88, w=.35)
        leg.AddEntry(sig, 'Signal + Background'.format(sig_name), 'f')
        leg.AddEntry(bkg, 'Background', 'f')
        leg.AddEntry(data, 'Data', 'pe')
        for h in [sig, bkg]:
            h_st.Add(h)
        h_st.Add(data, 'e1')
        gROOT.SetBatch(1)
        h_st.Draw()
        h_st.GetYaxis().SetTitleOffset(1.4)
        h_st.SetMaximum(3.5)
        self.Stuff.append(save_histo(h_st, 'AllWithCuts{0}'.format(sig_name), True, self.ResultsDir, draw_opt='nostack', l=leg))

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

    def get_full_bkg_toy(self, histos):
        toys = [self.Background[name].generate_toys(h) for name, h in histos.iteritems()]
        bkg = toys[0].Clone()
        bkg.Reset()
        for toy in toys:
            bkg.Add(toy)
        return bkg

    def test2(self, sig_name='85', n=1e5, h0=True, show=False, nbins=1000):
        n = int(n)
        cut = self.Cut[sig_name].AllCut
        bkg = self.draw_full_bkg(show=False, cut=cut)
        sig = self.draw_signal(sig=sig_name, show=False, cut=cut)
        data = bkg.Clone()
        data.Add(sig) if h0 else do_nothing()
        x = [-25, 20]
        x = [-8, 4] if sig_name == '95' else x
        x = [-12, 10] if sig_name == '90' else x
        h = TH1F('h', 'h', nbins, x[0], x[1])
        pbar = ProgressBar(widgets=[Percentage(), ' ', Bar(), '', ETA(), ' ', FileTransferSpeed()], maxval=n).start()
        for i in xrange(n):
            pbar.update(i + 1)
            ll = self.new_ll(sig, bkg, data)
            h.Fill(ll)
        format_histo(h, x_tit='q', y_tit='Number of Entries', y_off=1.3)
        self.Stuff.append(save_histo(h, 'test', show, self.ResultsDir))
        pbar.finish()
        return h

    def draw_both(self, sig='85', n=1e5, nbins=1000, show=True):
        # sb = self.h0_ll(show=False, n=n, sig_name=sig)
        # b = self.h0_ll(show=False, h0=False, n=n, sig_name=sig)
        sb = self.test2(show=False, n=n, sig_name=sig, nbins=nbins)
        b = self.test2(show=False, h0=False, n=n, sig_name=sig, nbins=nbins)
        # obs = self.observed_ll(sig_name=sig)
        # obs = self.test(sig_name=sig)
        obs = self.obs(sig)
        leg = make_legend(.15, .88, nentries=3, w=.35)
        h_st = THStack('mc', 'Likelihood Ratio Test for m_{{H}} = {0} Gev;q=-2ln(Q);Number of Entries'.format(sig))
        colors = [bkg_col, 601, bkg_col, 601]
        sb_fill = self.fill_till_threshold(sb, obs, 3)
        b_fill = self.fill_till_threshold(b, obs, 5, pos=False)
        for i, h in enumerate([sb_fill, b_fill, sb, b]):
            h.SetStats(0)
            h.SetLineWidth(2)
            h.SetLineColor(colors[i])
            h_st.Add(h)
        leg.AddEntry(sb, 'Signal + Background', 'l')
        leg.AddEntry(b, 'Background', 'l')
        gr = make_tgrapherrors('b', 'b', width=2)
        leg.AddEntry(gr, 'Observed', 'l')
        gROOT.SetBatch(1)
        h_st.Draw('nostack')
        gROOT.SetBatch(0)
        maxi = b.GetMaximum() * 1.05
        l = make_tgaxis(obs, 0, maxi, 'obs   ', width=2, offset=.3)
        h_st.SetMaximum(maxi)
        h_st.GetYaxis().SetTitleOffset(1.9)
        print 'CLs is:', self.get_cls(sb, b, obs)
        self.Stuff.append(save_histo(h_st, 'ProbDens{0}{1}'.format(sig, n), show, self.ResultsDir, l=l, draw_opt='nostack', l1=leg, lm=.13))
        self.SB[sig] = sb
        self.B[sig] = b
        self.Obs[sig] = obs

    def obs(self, sig_name='85'):
        sig_name = str(sig_name)
        cut = self.Cut[sig_name].AllCut
        data = self.draw_data(cut=cut, show=False)
        sig = self.draw_signal(sig=sig_name, show=False, cut=cut)
        bkg = self.draw_full_bkg(show=False, cut=cut)
        # self.bla = save_histo(bkg, 'bla', True, self.ResultsDir)
        ll = self.new_ll(sig, bkg, data, toy=False)
        return ll

    @staticmethod
    def new_ll(hs, hb, hd, toy=True):
        ll = hs.Integral()
        if verbose:
            print ll
        for ibin in xrange(hb.GetNbinsX()):
            s = hs.GetBinContent(ibin)
            b = hb.GetBinContent(ibin)
            n = hd.GetBinContent(ibin)
            n = gRandom.Poisson(n) if toy else n
            if b and n:
                if verbose:
                    print n, s, b, n * log(1 + s / b)
                ll -= n * log(1 + s / b)
        if verbose:
            print ll
        return 2 * ll

    def exclusion_plot(self, n=5e4, nbins=200):
        if not self.SB:
            for sig in self.Cut:
                self.draw_both(sig=sig, n=n, nbins=nbins, show=False)
        cls = {}
        for sig in self.Cut:
            cls[sig] = (self.get_cls(self.SB[sig], self.B[sig], self.Obs[sig]))
        gr = make_tgrapherrors('gr', 'Exclusion Values', width=2)
        gr1 = make_tgrapherrors('gr1', '90% limit', width=2, color=2)
        gr2 = make_tgrapherrors('gr2', '95% limit', width=2, color=4)
        l = make_legend(.12, .88, 3, w=.3)
        for g in [gr, gr1, gr2]:
            l.AddEntry(g, g.GetTitle(), 'l')
        cls = OrderedDict(sorted(cls.iteritems()))
        for i, (name, val) in enumerate(cls.iteritems()):
            gr.SetPoint(i, int(name), val * 100.)
        format_histo(gr, x_tit='m_{H} [GeV]', y_tit='CLs [%]', y_off=1.2)
        self.Stuff.append(save_histo(gr, 'ExclusionPlot', 1, self.ResultsDir, l=l))
        l1 = make_tgxaxis(84, 96, 10, '90%', color=2, offset=.3, width=2)
        l2 = make_tgxaxis(84, 96, 5, '95%', color=4, offset=.3, width=2)
        l1.Draw()
        l2.Draw()
        self.Stuff.append([l1, l2])
        save_plots('ExclusionPlot', self.ResultsDir)

    def brazilian_flag(self, n=5e4, nbins=200):
        if not self.SB:
            for sig in self.Cut:
                gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
                self.draw_both(sig=sig, n=n, nbins=nbins, show=False)
        quant = {}
        for sig in self.Cut:
            quant[sig] = (self.get_quantiles(self.B[sig]))
        quant = OrderedDict(sorted(quant.iteritems()))
        b_means = {sig: h.GetMean() for sig, h in self.B.iteritems()}
        b_means = OrderedDict(sorted(b_means.iteritems()))
        sb_means = {sig: h.GetMean() for sig, h in self.SB.iteritems()}
        sb_means = OrderedDict(sorted(sb_means.iteritems()))
        obs = {sig: obs for sig, obs in self.Obs.iteritems()}
        obs = OrderedDict(sorted(obs.iteritems()))
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        gr1 = make_tgrapherrors('gr1', 'Mean Sig + Bkg', color=bkg_col, width=2, marker_size=2, marker=21)
        gr2 = make_tgrapherrors('gr2', 'Mean Bkg', color=601, width=2, marker_size=2, marker=21)
        gr3 = make_tgrapherrors('gr3', 'Observed', width=2, marker_size=2, marker=21)
        gr4 = make_tgrapherrors('gr4', '2 #sigma', marker_size=0, width=2, fill_col=3)
        gr5 = make_tgrapherrors('gr5', '1 #sigma', width=2, fill_col=5)
        gr6 = make_tgrapherrors('gr6', 's21', width=2, fill_col=5)
        gr7 = make_tgrapherrors('gr7', 's22', width=2, fill_col=3)
        for i, (sig, val) in enumerate(sb_means.iteritems()):
            gr1.SetPoint(i, int(sig), val)
        for i, (sig, val) in enumerate(b_means.iteritems()):
            gr2.SetPoint(i, int(sig), val)
        for i, (sig, val) in enumerate(obs.iteritems()):
            gr3.SetPoint(i, int(sig), val)
        leg = make_legend(.58, .88, 5, w=.3)
        for gr in [gr1, gr2, gr3]:
            leg.AddEntry(gr, gr.GetTitle(), 'lp')

        self.fill_flag(gr4, quant, quant, 0, 1)
        self.fill_flag(gr5, quant, b_means, 1)
        self.fill_flag(gr6, b_means, quant, None, 2)
        self.fill_flag(gr7, quant, quant, 2, 3)

        for gr in [gr4, gr5]:
            leg.AddEntry(gr, gr.GetTitle(), 'f')

        mg = TMultiGraph('mg_ph', 'Brazilian Flag')
        for gr in [gr4, gr5, gr6, gr7]:
            mg.Add(gr, 'f')
            mg.Add(gr, 'l')
        for gr in [gr1, gr2, gr3]:
            mg.Add(gr, 'pl')
        gROOT.SetBatch(1)
        mg.Draw('A')
        gROOT.SetBatch()
        format_histo(mg, x_tit='m_{H} [GeV]', y_tit='q=-2ln(Q)', y_off=1.2)
        self.Stuff.append(save_histo(mg, 'BrazFlag', 1, self.ResultsDir, draw_opt='A', l=leg))

    @staticmethod
    def fill_flag(gr, d1, d2, e1=None, e2=None):
        for i, (sig, val) in enumerate(d1.iteritems()):
            gr.SetPoint(i, int(sig), val[e1] if e1 is not None else val)
        i = 5
        for sig, val in d2.iteritems():
            gr.SetPoint(i, int(sig), val[e2] if e2 is not None else val)
            i -= 1
        gr.SetPoint(6, gr.GetX()[0], gr.GetY()[0])

    @staticmethod
    def get_quantiles(b):
        y = zeros(4)
        x = array([(1 - .95) / 2., (1 - .68) / 2., (1 + .68) / 2., (1 + .95) / 2.])
        b.GetQuantiles(4, y, x)
        return y

    @staticmethod
    def get_cls(hs, hb, obs):
        s = hs.Clone()
        s.Scale(1 / hs.Integral())
        b = hb.Clone()
        b.Scale(1 / hb.Integral())
        psb = s.Integral(s.FindBin(obs), s.GetNbinsX() - 1)
        pb = b.Integral(1, b.FindBin(obs))
        return psb / (1 - pb)

    @staticmethod
    def fill_till_threshold(h, thr, col, pos=True):
        h_new = h.Clone()
        for ibin in xrange(h.GetNbinsX()):
            if not pos:
                if h.GetBinLowEdge(ibin) > thr:
                    h_new.SetBinContent(ibin, 0)
            else:
                if h.GetBinLowEdge(ibin) < thr:
                    h_new.SetBinContent(ibin, 0)
        h_new.SetFillColor(col)
        return h_new


__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
