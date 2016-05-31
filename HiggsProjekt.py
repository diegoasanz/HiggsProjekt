# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile, TH1F, THStack, TLegend, TCut, gROOT, gRandom
from glob import glob
from numpy import log
from math import factorial
from Utils import *
from Cut import Cut, significance, purity, efficiency
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed


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
        h = self.Data.get_histo(branch, scaled=scaled, nbins=nbins, xmax=xmax, cut_string=cut, xmin=xmin)
        h.SetFillColor(dat_col)
        self.Stuff.append(save_histo(h, 'Data{0}'.format(branch.title()), show, self.ResultsDir, draw_opt=draw_opt))
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
    def neg_log_lr(h_s, h_b, seed_b, data, h0=True):
        ll = 0
        for ibin in xrange(seed_b.GetNbinsX()):
            s = h_s.GetBinContent(ibin) if h0 else 0
            b = h_b.GetBinContent(ibin)
            n = data.GetBinContent(ibin)
            b1 = seed_b.GetBinContent(ibin)
            if b1:
                ll += s - log((s + b) / b1) * n
        return 2 * ll

    def observed_ll(self, sig_name='85'):
        sig_name = str(sig_name)
        cut = self.Cut[sig_name].AllCut
        sig = self.draw_data(cut=cut, show=False)
        bkg = self.draw_data(show=False)
        bkg.Add(sig, -1)
        ll = self.neg_log_lr(sig, bkg, bkg, sig)
        return ll

    def h0(self):
        sig_name = '85'
        cut = self.Cut[sig_name].AllCut
        sig = self.draw_signal(sig_name, show=False, scale=True, nbins=2, cut=cut)
        bkg = self.draw_full_bkg(show=False, nbins=2, cut=cut)
        ll = self.neg_log_lr(sig, bkg)
        print ll
        return ll

    def get_full_bkg_toy(self, histos):
        toys = [self.Background[name].generate_toys(h) for name, h in histos.iteritems()]
        bkg = toys[0].Clone()
        bkg.Reset()
        for toy in toys:
            bkg.Add(toy)
        return bkg

    def h0_ll(self, sig_name='85', n=10000., h0=True, show=False):
        n = int(n)
        cut = self.Cut[sig_name].AllCut
        data = self.draw_data(nbins=2, show=False, cut=cut)
        sig_seed = self.draw_signal(sig=sig_name, show=False, cut=cut, scale=False)
        bkg_seeds = {bkg: self.draw_bkg(bkg, branch='mvis', show=False, nbins=2, xmax=120, cut=cut, scale=False, xmin=40) for bkg in self.Background}
        bkg1 = self.draw_full_bkg(show=False, cut=cut)
        h = TH1F('h', 'h', 100, -20, 20)
        pbar = ProgressBar(widgets=[Percentage(), ' ', Bar(), '', ETA(), ' ', FileTransferSpeed()], maxval=n).start()
        for i in xrange(n):
            pbar.update(i + 1)
            sig = self.Signal['higgs_{0}'.format(sig_name)].generate_toys(sig_seed)
            bkg = self.get_full_bkg_toy(bkg_seeds)
            bkg2 = self.get_full_bkg_toy(bkg_seeds)
            ll = self.neg_log_lr(sig, bkg, bkg2, data, h0)
            h.Fill(ll)
        format_histo(h, x_tit='q', y_tit='Number of Entries', y_off=1.3)
        self.Stuff.append(save_histo(h, 'test', show, self.ResultsDir))
        pbar.finish()
        return h

    def test1(self, sig_name='85', n=10000., h0=True, show=False):
        n = int(n)
        cut = self.Cut[sig_name].AllCut
        data = self.draw_data(nbins=2, show=False, cut=cut)
        sig_seed = self.draw_signal(sig=sig_name, show=False, cut=cut, scale=False)
        bkg_seeds = {bkg: self.draw_bkg(bkg, branch='mvis', show=False, nbins=2, xmax=120, cut=cut, scale=False, xmin=40) for bkg in self.Background}
        b_pdf = self.draw_full_bkg(show=False, cut=cut)
        b_pdf.Scale(1 / b_pdf.Integral())
        s_pdf = self.draw_signal(sig=sig_name, show=False, cut=cut)
        s_pdf.Scale(1 / s_pdf.Integral())
        xmin = 0 if not sig_name == '95' else .5
        xmax = 4 if not sig_name == '95' else 2
        h = TH1F('h', 'h', 100, xmin, xmax)
        pbar = ProgressBar(widgets=[Percentage(), ' ', Bar(), '', ETA(), ' ', FileTransferSpeed()], maxval=n).start()
        for i in xrange(n):
            pbar.update(i + 1)
            sig = self.Signal['higgs_{0}'.format(sig_name)].generate_toys(sig_seed) if h0 else 0
            bkg = self.get_full_bkg_toy(bkg_seeds)
            bkg2 = self.get_full_bkg_toy(bkg_seeds)
            ll = self.ratio(sig, bkg, bkg2, data, s_pdf, b_pdf)
            h.Fill(ll)
        format_histo(h, x_tit='q', y_tit='Number of Entries', y_off=1.3)
        self.Stuff.append(save_histo(h, 'test', show, self.ResultsDir))
        pbar.finish()
        return h

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

    def test3(self):
        sig_seed = self.draw_signal(sig=sig_name, show=False, cut=cut, scale=False)
        bkg_seeds = {bkg: self.draw_bkg(bkg, branch='mvis', show=False, nbins=2, xmax=120, cut=cut, scale=False, xmin=40) for bkg in self.Background}
        h = TH1F('h', 'h', 100, 0, 5)
        for i in xrange(10000):
            s = self.Signal['higgs_{0}'.format('85')].generate_toys(sig_seed)
            b = self.get_full_bkg_toy(bkg_seeds)


    def test(self, sig_name=85):
        sig_name = str(sig_name)
        cut = self.Cut[sig_name].AllCut
        sig = self.draw_data(cut=cut, show=False)
        bkg = self.draw_data(show=False)
        bkg.Add(sig, -1)
        b_pdf = self.draw_full_bkg(show=False, cut=cut)
        b_pdf.Scale(1 / b_pdf.Integral())
        s_pdf = self.draw_signal(sig=sig_name, show=False, cut=cut)
        s_pdf.Scale(1 / s_pdf.Integral())
        ll = self.ratio(sig, bkg, bkg, sig, s_pdf, b_pdf, d=True)
        print ll
        return ll

    def lsb(self, hs, hb, hd, sh, sb, d=False):
        n = hd.Integral()
        s = hs.Integral() if hs else 0
        b = hb.Integral()
        ll = n * log(s + b) - s - b - log(factorial(n))
        if not d:
            for ibin in xrange(hb.GetNbinsX()):
                ll += (s * sh.GetBinContent(ibin) + b * sb.GetBinContent(ibin)) / (s + b)
        return ll

    def lb(self, hb, hd, sb, d=False):
        n = hd.Integral()
        b = hb.Integral()
        ll =  n * log(b) - b - log(factorial(n))
        if not d:
            for ibin in xrange(sb.GetNbinsX()):
                ll += sb.GetBinContent(ibin)
        return ll

    def ratio(self, hs, hb1, hb2, hd, sh, sb, d=False):
        return self.lsb(hs, hb1, hd, sh, sb, d) / self.lb(hb2, hd, sb, d)

    def draw_both(self, sig='85', n=1e5, nbins=1000):
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
        print 'CLs is:', self.get_CLs(sb, b, obs)
        self.Stuff.append(save_histo(h_st, 'ProbDens{0}'.format(sig), 1, self.ResultsDir, l=l, draw_opt='nostack', l1=leg, lm=.13))

    def fill_till_threshold(self, h, thr, col, pos=True):
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


    def obs(self, sig_name='85'):
        sig_name = str(sig_name)
        cut = self.Cut[sig_name].AllCut
        data = self.draw_data(cut=cut, show=False)
        sig = self.draw_signal(sig=sig_name, show=False, cut=cut)
        bkg = self.draw_full_bkg(show=False, cut=cut)
        # self.bla = save_histo(bkg, 'bla', True, self.ResultsDir)
        ll = self.new_ll(sig, bkg, data, toy=False)
        return ll

    def test4(self, h0=True):
        cut = self.AllCut
        bkg = self.draw_full_bkg(show=False, cut=cut, nbins=5)
        sig = self.draw_signal(sig='85', show=False, cut=cut, nbins=5)
        data = bkg.Clone()
        data.Add(sig) if h0 else do_nothing()

        sig_seed = self.draw_signal(sig='85', show=False, cut=cut, scale=False, nbins=5)
        bkg_seeds = {bkg: self.draw_bkg(bkg, branch='mvis', show=False, nbins=5, xmax=120, cut=cut, scale=False, xmin=40) for bkg in self.Background}
        toy_data = self.get_full_bkg_toy(bkg_seeds)
        toy_data.Add(self.Signal['higgs_{0}'.format(85)].generate_toys(sig_seed)) if h0 else do_nothing()

        print self.new_ll(sig, bkg, toy_data)

    def new_ll(self, hs, hb, hd, toy=True):
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


    def get_CLs(self, hs, hb, obs):
        s = hs.Clone()
        s.Scale(1 / hs.Integral())
        b = hb.Clone()
        b.Scale(1 / hb.Integral())
        psb = s.Integral(s.FindBin(obs), s.GetNbinsX() - 1)
        pb = b.Integral(1, b.FindBin(obs))
        return psb / (1 - pb)



__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analysis()
