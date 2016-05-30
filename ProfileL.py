# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TH1F, TMath, RooStats, TF1, TMinuit, Double, Long, gMinuit, kTRUE
from ToyExperimentGen import *
from AnalyzeInfo import *
from array import array
# from numpy import *
from Utils import *
__author__ = 'Pin-Jung & Diego Alejandro'

class ProfileL:
    def __init__(self, analyzeInfo, toy_background, toy_signal, background, signal, exclusion_mu=1, npar=1):
        self.branch_info = analyzeInfo
        self.num_bins = self.branch_info.branch_numbins[self.branch_info.test_statistics_branch]
        self.toy_bkg = toy_background
        self.toy_sgn = toy_signal
        self.toy_sgnbkg = deepcopy(self.toy_sgn)
        self.toy_sgnbkg.Add(self.toy_bkg)
        self.background = background
        self.signal = signal
        self.mu_excl = float(exclusion_mu)
        self.mu_values = linspace(-1,3,801)
        # Minuit parameters
        self.npar = npar
        # self.npar = 1
        self.start_value_mu = 0.5
        self.init_step_mu = 0.001
        self.max_iterations = 10000
        self.tolerance = 0.001
        self.min_mu = -1
        self.max_mu = 3
        self.working_toy = self.toy_bkg
        self.mu_toy_bkg = self.fit_mu(self.background, self.signal)  #self.fit_mu2()
        self.working_toy = self.toy_sgnbkg
        self.mu_toy_sgnbkg = self.fit_mu(self.background, self.signal)  #self.fit_mu2()
        #
        # For discovery:
        #
        self.working_toy = self.toy_bkg
        self.nll_q0_mu_bkg_num = self.nll_value(self.npar, [0])
        self.working_toy = self.toy_sgnbkg
        self.nll_q0_mu_sgnbkg_num = self.nll_value(self.npar, [0])
        # in discovery, q0 = 0 when mu_toy_* is smaller than 0
        if self.mu_toy_bkg < 0:
            self.nll_q0_mu_bkg_den = self.nll_q0_mu_bkg_num  # in this way q0 will be 0
        else:
            self.working_toy = self.toy_bkg
            self.nll_q0_mu_bkg_den = self.nll_value(self.npar, [self.mu_toy_bkg])
        if self.mu_toy_sgnbkg < 0:
            self.nll_q0_mu_sgnbkg_den = self.nll_q0_mu_sgnbkg_num  # in this way q1 will be 0
        else:
            self.working_toy = self.toy_sgnbkg
            self.nll_q0_mu_sgnbkg_den = self.nll_value(self.npar, [self.mu_toy_sgnbkg])
        self.q0_bkg = self.nll_q0_mu_bkg_num - self.nll_q0_mu_bkg_den
        self.Z0_bkg = TMath.Sqrt(self.q0_bkg)
        self.q0_sgnbkg = self.nll_q0_mu_sgnbkg_num - self.nll_q0_mu_sgnbkg_den
        self.Z0_sgnbkg = TMath.Sqrt(self.q0_sgnbkg)
        #
        # For exclusion:
        #
        self.working_toy = self.toy_bkg
        self.nll_qe_mu_bkg_num = self.nll_value(self.npar, [self.mu_excl])
        self.working_toy = self.toy_sgnbkg
        self.nll_qe_mu_sgnbkg_num = self.nll_value(self.npar, [self.mu_excl])
        # if mu_toy_* is smaller than 0 then q0 should be -2*ln(L(mu_excl,the'')/L(0,the'')); if mu_toy_* is larger than mu_excl, q0 should be 0
        if self.mu_toy_bkg < 0:
            self.working_toy = self.toy_bkg
            self.nll_qe_mu_bkg_den = self.nll_value(self.npar, [0])  # for L(0,the'')
        elif self.mu_toy_bkg > self.mu_excl:
            self.nll_qe_mu_bkg_den = self.nll_qe_mu_bkg_num  # in this way q0 will be 0
        else:
            self.working_toy = self.toy_bkg
            self.nll_qe_mu_bkg_den = self.nll_value(self.npar, [self.mu_toy_bkg])
        if self.mu_toy_sgnbkg < 0:
            self.working_toy = self.toy_sgnbkg
            self.nll_qe_mu_sgnbkg_den = self.nll_value(self.npar, [0])  # for L(0,the'')
        elif self.mu_toy_sgnbkg > self.mu_excl:
            self.nll_qe_mu_sgnbkg_den = self.nll_qe_mu_sgnbkg_num  # in this way q0 will be 0
        else:
            self.working_toy = self.toy_sgnbkg
            self.nll_qe_mu_sgnbkg_den = self.nll_value(self.npar, [self.mu_toy_sgnbkg])
        self.qe_bkg = self.nll_qe_mu_bkg_num - self.nll_qe_mu_bkg_den
        self.Ze_bkg = TMath.Sqrt(self.qe_bkg)
        self.qe_sgnbkg = self.nll_qe_mu_sgnbkg_num - self.nll_qe_mu_sgnbkg_den
        self.Ze_sgnbkg = TMath.Sqrt(self.qe_sgnbkg)

    def nll_value(self, npar, par):
        '''
        :param npar: number of parameters, should be 1
        :param par: value of "mu", should be handed as a list of one element. e.g. nll_value(1,[0.5])
        :return: the value of the negative log-likelihood
        '''
        nll = Double(0)
        for bin in xrange(1, self.num_bins + 1):
            b = self.background.GetBinContent(bin)
            s = self.signal.GetBinContent(bin)
            t = self.working_toy.GetBinContent(bin)
            if b + par[0]*s == 0:
                f = 0
            else:
                f = (-2)*TMath.Log(TMath.Poisson(t, b + par[0]*s))
            nll += f
        return nll

    def fcn(self, npar, deriv, f, apar, iflag):
        f[0] = self.nll_value(npar, apar)

    def fit_mu(self, background, signal):
        myMinuit = TMinuit(self.npar)
        myMinuit.SetFCN(self.fcn)
        gMinuit.Command('SET PRINT -1')
        ierflg = Long(0)
        myMinuit.mnparm(0, 'mu', self.start_value_mu, self.init_step_mu, self.min_mu, self.max_mu, ierflg)
        arglist = array('d', (0, 0))
        arglist[0] = self.max_iterations
        arglist[1] = self.tolerance
        myMinuit.mnexcm("MINIMIZE", arglist, 2, ierflg)
        # check TMinuit status
        amin, edm, errdef = Double(0.), Double(0.), Double(0.)
        nvpar, nparx, icstat = Long(0), Long(0), Long(0)
        myMinuit.mnstat(amin, edm, errdef, nvpar, nparx, icstat)
        # get final results
        p, pe = Double(0), Double(0)
        myMinuit.GetParameter(0, p, pe)
        # finalPar = float(p)
        # finalParErr = float(pe)
        # print_banner('MINUIT fit completed:')
        # print ' fcn@minimum = %.3g' %(amin)," error code =", ierflg, " status =", icstat
        # print " Results: \t value error"
        # print ' %s: \t%10.3e +/- %.1e '%('mu', finalPar, finalParErr)
        return p

    def fit_mu2(self):
        min = 10000
        ir = self.mu_values[0]
        for i in self.mu_values:
            value = self.nll_value(1, [i])
            if value > min:
                return ir
            min = value
            ir = i
        return self.mu_values[-1]