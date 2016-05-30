from collections import OrderedDict
from ROOT import TCut, gROOT
from Utils import *
from numpy import sqrt


def purity(h1, h2):
    try:
        return h1.Integral() / (h1.Integral() + h2.Integral())
    except ZeroDivisionError:
        return 0


def significance(sig, bkg):
    try:
        sig_int = sig.Integral()
        bkg_int = bkg.Integral()
        return sig_int / sqrt(bkg_int) if sig_int and bkg_int else 0
    except ZeroDivisionError:
        return 0


def efficiency(sig, sig_nocut):
    return sig.Integral() / sig_nocut.Integral()


class Cut:

    def __init__(self, analysis, sig):
        self.Analysis = analysis
        self.CutStrings = self.define_cutstrings()
        self.Signal = sig

        self.AllCut = self.generate_cutstrings()

        self.Stuff = []

    @staticmethod
    def define_cutstrings():
        dic = OrderedDict()
        dic['btag1'] = TCut('btag1', '')
        dic['btag2'] = TCut('btag2', '')
        dic['mmis'] = TCut('mmis', '')
        dic['acop'] = TCut('acop', '')
        dic['acthm'] = TCut('acthm', '')
        dic['elmuon'] = TCut('acop', '')
        dic['ucsdbt0'] = TCut('ucsdbt0', '')
        dic['all_cut'] = TCut('all_cut', '')
        return dic

    def generate_cutstrings(self):
        self.reset_cut('all_cut')
        if self.Signal == '85':
            self.set_cut('mmis', 'mmis>76')
            self.set_cut('acop', 'acop<2.7')
            # self.set_cut('acthm', 'acthm<.9')
            self.set_cut('btag1', 'btag1>.25')
            self.set_cut('btag2', 'btag2>.15')
            self.set_cut('ucsdbt0', 'ucsdbt0>1.5')
        for name, cut in self.CutStrings.iteritems():
            if not name == 'all_cut' and str(cut):
                self.CutStrings['all_cut'] += cut
        return self.CutStrings['all_cut']

    def cut_exists(self, name):
        if name in self.CutStrings:
            return True
        else:
            log_warning('There is no cut with the name "{name}"!'.format(name=name))
            return False

    def reset_cut(self, name):
        if self.cut_exists(name):
            self.CutStrings[name].SetTitle('')

    def set_cut(self, name, value):
        if self.cut_exists(name):
            self.reset_cut(name)
            self.CutStrings[name] += str(value)

    def vary_el_muon(self, sig_name='85'):
        sig_nocut = self.Analysis.draw_signal(sig=sig_name, show=False)
        bkg_nocut = self.Analysis.draw_full_bkg(show=False)
        cut_string = 'ele_num || muon_num'
        self.set_cut('elmuon', cut_string)
        sig = self.Analysis.draw_signal(sig=sig_name, show=False, cut=self.CutStrings['elmuon'])
        bkg = self.Analysis.draw_full_bkg(show=False, cut=self.CutStrings['elmuon'])
        print 'Purity:', purity(sig, bkg), purity(sig_nocut, bkg_nocut)
        print 'Efficiency:', efficiency(sig, sig_nocut)
        print 'Significance:', significance(sig, bkg), significance(sig_nocut, bkg_nocut)

    def vary_cut(self, cut='acop', end_val=3.2, step=10., geq=False, off=1):
        sig_name = self.Signal
        sig_nocut = self.Analysis.draw_signal(sig=sig_name, show=False)
        name = 'm_{{H}}={0}GeV '.format(sig_name)
        gr = make_tgrapherrors('Purity_{0}'.format(cut), name + 'Purity for {0}'.format(cut))
        gr1 = make_tgrapherrors('Efficiency{0}'.format(cut), name + 'Efficiency for {0}'.format(cut))
        gr2 = make_tgrapherrors('Significance{0}'.format(cut), name + 'Significance for {0}'.format(cut))
        for i, val in enumerate(xrange(int(off * step), int(end_val * step) + 1)):
            gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
            val /= float(step)
            cut_string = '{cut}{sign}{value}'.format(cut=cut, value=val, sign='>' if geq else '<')
            self.set_cut(cut, cut_string)
            print self.CutStrings[cut]
            sig = self.Analysis.draw_signal(sig=sig_name, show=False, cut=self.CutStrings[cut])
            bkg = self.Analysis.draw_full_bkg(show=False, cut=self.CutStrings[cut])
            pur = purity(sig, bkg)
            eff = efficiency(sig, sig_nocut)
            gr.SetPoint(i, val, pur * 100.)
            gr1.SetPoint(i, val, eff * 100.)
            gr2.SetPoint(i, val, significance(sig, bkg) * 100.)
        format_histo(gr, x_tit='Cut Value', y_tit='Purity [%]', y_off=1.3)
        format_histo(gr1, x_tit='Cut Value', y_tit='Efficiency [%]', y_off=1.3)
        format_histo(gr2, x_tit='Cut Value', y_tit='Significance [%]', y_off=1.3)
        self.Stuff.append(save_histo(gr, 'Purity_{0}{1}'.format(cut, sig_name), False, self.Analysis.ResultsDir, lm=.12))
        self.Stuff.append(save_histo(gr1, 'Efficiency_{0}{1}'.format(cut, sig_name), False, self.Analysis.ResultsDir, lm=.12))
        self.Stuff.append(save_histo(gr2, 'Significance_{0}{1}'.format(cut, sig_name), False, self.Analysis.ResultsDir, lm=.12))
        c = TCanvas('c', 'c', 3500, 1300)
        c.Divide(3)
        for i, gra in enumerate([gr, gr1, gr2], 1):
            pad = c.cd(i)
            pad.SetLeftMargin(.12)
            gra.Draw('alp')
        save_plots('CutScan{0}{1}'.format(cut.title(), sig_name), self.Analysis.ResultsDir)
        self.Stuff.append([c])
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')

    def vary_btag(self, step=10., nbtag=1):
        self.vary_cut(cut='btag{0}'.format(nbtag), step=step, geq=True, end_val=1, off=0)

    def vary_ucsdbt0(self, step=2., end_val=13):
        self.vary_cut(cut='ucsdbt0', step=step, geq=True, end_val=end_val, off=0)

    def vary_acthm(self, step=20.):
        self.vary_cut(cut='acthm', step=step, end_val=1, off=0)

    def vary_mmmis(self, step=.2):
        self.vary_cut(cut='mmis', step=step, geq=True, end_val=100, off=50)
