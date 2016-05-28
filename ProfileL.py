# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TH1F, TMath, RooStats, TF1, TMinuit, Double, Long
from ToyExperimentGen import *
from AnalyzeInfo import *
from array import array
from Utils import *
__author__ = 'Pin-Jung & Diego Alejandro'

class ProfileL:
    def __init__(self, toy, background, signal):
        self.branch_info = AnalyzeInfo()
        self.num_bins = self.branch_info.branch_numbins[self.branch_info.test_statistics_branch]
        self.toy = toy
        self.background = background
        self.signal = signal
        self.nll = Double(0)
        self.npar = 1
        self.start_value_mu = 0.5
        self.init_step_mu = 0.001
        self.max_iterations = 1000
        self.tolerance = 3
        self.min_mu = -1
        self.max_mu = 10
        self.mu = self.fit_mu(self.toy, self.background, self.signal)

    def nll_value(self, npar, par):
        '''

        :param npar: number of parameters, should be 1
        :param par: value of "mu", should be handed as a list of one element. e.g. nll_value(1,[0.5])
        :return: the value of the negative log-likelihood
        '''
        self.nll = Double(0)
        for bin in xrange(1, self.num_bins + 1):
            b = self.background.GetBinContent(bin)
            s = self.signal.GetBinContent(bin)
            t = self.toy.GetBinContent(bin)
            f = (-2)*TMath.Log(TMath.Poisson(t,b + par[0]*s))
            self.nll += f
        return self.nll

    def fcn(self, npar, deriv, f, apar, iflag):
        f[0] = self.nll_value(npar, apar)

    def fit_mu(self,toy, background, signal):
        myMinuit = TMinuit(self.npar)
        myMinuit.SetFCN(self.fcn)
        ierflg = Long(0)
        myMinuit.mnparm(0, 'mu', self.start_value_mu, self.init_step_mu, self.min_mu, self.max_mu, ierflg)
        arglist = array('d', (0, 0))
        arglist[0] = self.max_iterations
        arglist[1] = self.tolerance
        myMinuit.mnexcm("MIGRAD", arglist, 2, ierflg)
        # check TMinuit status
        amin, edm, errdef = Double(0.), Double(0.), Double(0.)
        nvpar, nparx, icstat = Long(0), Long(0), Long(0)
        myMinuit.mnstat(amin, edm, errdef, nvpar, nparx, icstat)
        # get final results
        p, pe = Double(0), Double(0)
        myMinuit.GetParameter(0, p, pe)
        finalPar = float(p)
        finalParErr = float(pe)
        print_banner('MINUIT fit completed:')
        print ' fcn@minimum = %.3g' %(amin)," error code =", ierflg, " status =", icstat
        print " Results: \t value error"
        print ' %s: \t%10.3e +/- %.1e '%('mu', finalPar, finalParErr)
        return p


    def qValue(self, toy, histogram_num, histogram_den, sig_bkg_histos, sig_histos, bkg_histos, data_histos):
        numBins = self.branch_info.number_toys
        auxiliary_histo = TH1F('h1', 'h1', numBins, 0, numBins)
        auxiliary_histo.SetBinErrorOption(TH1F.kPoisson)
        for bin in xrange(1, numBins+1):
            toy_bin_cont = toy.GetBinContent(bin)
            h_num_bin_cont = histogram_num.GetBinContent(bin)
            h_den_bin_cont = histogram_den.GetBinContent(bin)
            auxiliary_histo.SetBinContent(bin, log(TMath.Poisson(toy_bin_cont, h_num_bin_cont) - log(TMath.Poisson(toy_bin_cont, h_den_bin_cont))))
        return ((-2) * auxiliary_histo.Integral())
        # self.pdf = PDFGenerator(branchName, sig_bkg_histos, bkg_histos)
        # self.numBins = self.branch_info.branch_numbins[branchName]
        # self.sig_value = {binN: sig_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        # self.bkg_value = {binN: bkg_histos[branchName].GetBinContent() for binN in xrange(self.numBins)}
        # self.data_value = {binN: data_histos[higgsName][branchName]. GetBinContent for binN in xrange(self.numBins)}
        # self.mc_value = {binN: self.pdf.functionSB[binN] for binN in xrange(self.numBins)}

    def poisson(self, ):
        s = self.sig_value[binN]
        b = self.bkg_value[binN]
        mc = self.mc_value[binN]
        pdf = TF1("pdf", "TMath.Poisson(u * s + b, mc)", 0, 1)
        return deepcopy(pdf)

    def likelihood(self):
        L = 1
        for binN in xrange(1, self.numBins+1, 1):
            L * self.poisson(binN)
        return L

    def max_likelihood(self, L):
        for u in xrange(0, 1, 0.001):
            if L(u+1) - L(u) == 0:
                return u
