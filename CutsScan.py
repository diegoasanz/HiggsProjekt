# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, THStack, TColor, TCanvas, TPad, gROOT, gPad, RooFit, RooWorkspace, RooRealVar, RooGaussian, RooPlot, kTRUE, kFALSE, TMath, TH1F, TRandom3, gStyle, Double, TH2D
from glob import glob
from copy import deepcopy
from DataTree import *
from AnalyzeInfo import *
from ToyExperimentGen import *
from ProfileL import *
from numpy import *
from HiggsProjekt import *
import os


__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class CutsScan:
    def __init__(self, teststat, branch, cut_low_ini=-1, cut_low_end=1000, cut_high_ini=1000, cut_high_end=-1):
        self.analyze_info = AnalyzeInfo()
        self.teststat = teststat
        self.branch_cut = branch
        self.analyze_info.change_test_statistics_branch(teststat)
        self.analyze_info.switch_off_all_cuts()
        self.analyze_info.change_silent_analysis(1)
        self.analyze_info.change_number_toys(0)
        self.cut_low_ini = cut_low_ini
        self.cut_low_end = cut_low_end
        self.cut_high_ini = cut_high_ini
        self.cut_high_end = cut_high_end
        self.stuff = []
        print_banner('STARTING WITH HIGGS 85', '%')
        self.start_analysis('85')
        self.make_analysis()
        self.save_histograms('85')
        print_banner('STARTING WITH HIGGS 90', '%')
        self.start_analysis('90')
        self.make_analysis()
        self.save_histograms('90')
        print_banner('STARTING WITH HIGGS 95', '%')
        self.start_analysis('95')
        self.make_analysis()
        self.save_histograms('95')

    def start_analysis(self, mh='85'):
        self.analyze_info.change_montecarlo_to_analyse(mh)
        self.analyze_info.switch_off_all_cuts()
        print_banner('Creating Analysis...', '=')
        self.analysis = Analysis(self.analyze_info)
        self.s_ini = Double(self.analysis.mc_histograms_dict[self.analyze_info.monte_carlo_to_analyse][self.teststat].Integral())
        if self.cut_low_ini == -1:
            self.low_cut_ini = self.analyze_info.branch_min[self.branch_cut]
            self.high_cut_ini = self.analyze_info.branch_max[self.branch_cut]
            self.low_cut_end = self.high_cut_ini
            self.high_cut_end = self.low_cut_ini
        else:
            self.low_cut_ini = self.cut_low_ini
            self.high_cut_ini = self.cut_high_ini
            self.low_cut_end = self.cut_low_end
            self.high_cut_end = self.cut_high_end
        self.numdiv = 10
        self.low_cut_step = float(self.low_cut_end - self.low_cut_ini)/float(int(self.numdiv))
        self.high_cut_step = float(self.high_cut_end - self.high_cut_ini)/float(self.numdiv)
        self.h_stam_name = mh + '_'+self.branch_cut
        self.h_eff = TH2D(self.h_stam_name+'_Efficiency', self.h_stam_name+'_Efficiency', int(self.numdiv+1),
                          self.low_cut_ini - float(self.low_cut_end - self.low_cut_ini) / float(2*int(self.numdiv+1)),
                          self.low_cut_end + float(self.low_cut_end - self.low_cut_ini) / float(2*int(self.numdiv+1)),
                          int(self.numdiv+1), self.high_cut_end - float(self.high_cut_ini - self.high_cut_end) / float(2 * int(self.numdiv+1)),
                          self.high_cut_ini + float(self.high_cut_ini - self.high_cut_end) / float(2 * int(self.numdiv+1)))
        self.h_purity = TH2D(self.h_stam_name + '_Purity', self.h_stam_name + '_Purity', int(self.numdiv+1),
                             self.low_cut_ini - float(self.low_cut_end - self.low_cut_ini) / float(2 * int(self.numdiv + 1)),
                             self.low_cut_end + float(self.low_cut_end - self.low_cut_ini) / float(2 * int(self.numdiv + 1)),
                             int(self.numdiv + 1), self.high_cut_end - float(self.high_cut_ini - self.high_cut_end) / float(2 * int(self.numdiv + 1)),
                             self.high_cut_ini + float(self.high_cut_ini - self.high_cut_end) / float( 2 * int(self.numdiv + 1)))
        self.h_signif = TH2D(self.h_stam_name + '_Significance', self.h_stam_name + '_Significance', int(self.numdiv+1),
                             self.low_cut_ini - float(self.low_cut_end - self.low_cut_ini) / float(2 * int(self.numdiv + 1)),
                             self.low_cut_end + float(self.low_cut_end - self.low_cut_ini) / float(2 * int(self.numdiv + 1)),
                             int(self.numdiv + 1), self.high_cut_end - float(self.high_cut_ini - self.high_cut_end) / float(2 * int(self.numdiv + 1)),
                             self.high_cut_ini + float(self.high_cut_ini - self.high_cut_end) / float( 2 * int(self.numdiv + 1)))

    def make_analysis(self):
        print_banner('Filling histograms with data...', '-')
        for cutx in linspace(self.low_cut_ini, self.low_cut_end, int(self.numdiv+1)):
            for cuty in linspace(self.high_cut_ini, self.high_cut_end, int(self.numdiv+1)):
                if cuty > cutx:
                    self.make_cuts(cutx, cuty)

    def make_cuts(self, x, y):
        del self.analysis
        self.analyze_info.change_toggle_cuts(self.branch_cut, 1)
        self.analyze_info.change_cut_low(self.branch_cut, x)
        self.analyze_info.change_cut_high(self.branch_cut, y)
        self.analysis = Analysis(self.analyze_info)
        self.s = Double(self.analysis.mc_histograms_dict[self.analyze_info.monte_carlo_to_analyse][self.teststat].Integral())
        deltax = float(linspace(self.low_cut_ini, self.low_cut_end, int(self.numdiv+1))[1] - linspace(self.low_cut_ini, self.low_cut_end, int(self.numdiv+1))[0])
        deltay = float(linspace(self.high_cut_end, self.high_cut_ini, int(self.numdiv + 1))[1] -linspace(self.high_cut_end, self.high_cut_ini, int(self.numdiv + 1))[0])
        binx = int(float(x - self.low_cut_ini)/deltax + 1)
        biny = int(float(y - self.high_cut_end)/deltay + 1)
        self.h_eff.SetBinContent(binx, biny, float(self.s/self.s_ini))
        self.h_purity.SetBinContent(binx, biny, float(self.analysis.purity(self.teststat)))
        self.h_signif.SetBinContent(binx, biny, float(self.analysis.significance(self.teststat)))

    def save_histograms(self, mc='85'):
        print_banner('Saving histograms', '-')
        if not os.path.exists(mc+'/'):
            os.makedirs(mc+'/')
        if not os.path.exists(mc+'/'+self.teststat+'/'):
            os.makedirs(mc+'/'+self.teststat+'/')
        f = TFile(mc+'/'+self.teststat+'/histos.root','RECTREATE')
        gStyle.SetPalette(53)
        self.h_eff.SetContour(1024)
        self.h_eff.SetStats(kFALSE)
        self.h_eff.GetXaxis().SetTitle('low cut')
        self.h_eff.GetYaxis().SetTitle('high cut')
        c0 = TCanvas('c0', 'c0', 700, 700)
        c0.cd()
        self.h_eff.Draw('colz')
        c0.SaveAs(mc+'/'+self.teststat+'/'+self.h_stam_name+'_h_eff.png')
        self.h_purity.SetContour(1024)
        self.h_purity.SetStats(kFALSE)
        self.h_purity.GetXaxis().SetTitle('low cut')
        self.h_purity.GetYaxis().SetTitle('high cut')
        c1 = TCanvas('c1', 'c1', 700, 700)
        c1.cd()
        self.h_purity.Draw('colz')
        c1.SaveAs(mc + '/' + self.teststat + '/'+self.h_stam_name+'_h_purity.png')
        self.h_signif.SetContour(1024)
        self.h_signif.SetStats(kFALSE)
        self.h_signif.GetXaxis().SetTitle('low cut')
        self.h_signif.GetYaxis().SetTitle('high cut')
        c2 = TCanvas('c2', 'c2', 700, 700)
        c2.cd()
        self.h_signif.Draw('colz')
        c2.SaveAs(mc + '/' + self.teststat + '/'+self.h_stam_name+'_h_signif.png')
        f.Write()
        f.Close()
        del f
        # self.stuff.append(c0)
        # self.stuff.append(c1)
        # self.stuff.append(c2)

if __name__ == '__main__':
    print_banner('STARTING HIGGS CUTS ANALYSIS', '#')
    mode = int(raw_input('Mode: 0 for Automatic; 1 for general specific; 2 for very specific: ? '))
    if mode == 0:
        ana = AnalyzeInfo()
        for branch in ana.branch_names:
            if (branch != 'ievt') or (branch != 'irun') or (branch != 'mvis') or (branch != 'mvissc'):
                teststat = 'mvis'
                print_banner('Running: {test} with branch {bra}'.format(test=teststat, bra=branch),'=')
                w = CutsScan(teststat, branch)
                del w
                teststat = 'mvissc'
                print_banner('Running: {test} with branch {bra}'.format(test=teststat, bra=branch), '=')
                w = CutsScan(teststat, branch)
                del w
    elif mode == 1:
        teststat = raw_input('Enter the name of the test statistics used: ')
        branch = raw_input('Enter the name of the branch to study its cuts: ')
        w = CutsScan(teststat, branch)
    else:
        teststat = raw_input('Enter the name of the test statistics used: ')
        branch = raw_input('Enter the name of the branch to study its cuts: ')
        cut_low_ini = float(raw_input('Enter the initial low cut: '))
        cut_low_end = float(raw_input('Enter the final low cut: '))
        cut_high_ini = float(raw_input('Enter the initial high cut: '))
        cut_high_end = float(raw_input('Enter the final high cut: '))
        w = CutsScan(teststat, branch, cut_low_ini, cut_low_end, cut_high_ini, cut_high_end)