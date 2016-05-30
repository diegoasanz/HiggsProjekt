# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile, TMath
from ROOT import TTree
from ROOT import TH1F
from glob import glob
from copy import deepcopy

__author__ = 'Pin-Jung & Diego Alejandro'

class AnalyzeInfo:
    def __init__(self):
        # branches names:
        self.branch_names = []
        self.branch_names.append('acop')
        self.branch_names.append('acthm')
        self.branch_names.append('btag1')
        self.branch_names.append('btag2')
        self.branch_names.append('ele_ene')
        self.branch_names.append('ele_num')
        self.branch_names.append('ele_phi')
        self.branch_names.append('ele_the')
        self.branch_names.append('encm')
        self.branch_names.append('enj1')
        self.branch_names.append('enj2')
        self.branch_names.append('fmvis')
        self.branch_names.append('ievt')
        self.branch_names.append('irun')
        self.branch_names.append('maxcthj')
        self.branch_names.append('maxxov')
        self.branch_names.append('mmis')
        self.branch_names.append('muon_ene')
        self.branch_names.append('muon_num')
        self.branch_names.append('muon_phi')
        self.branch_names.append('muon_the')
        self.branch_names.append('mvis')
        self.branch_names.append('mvissc')
        self.branch_names.append('phj1')
        self.branch_names.append('phj2')
        self.branch_names.append('pho_ene')
        self.branch_names.append('pho_num')
        self.branch_names.append('pho_phi')
        self.branch_names.append('pho_the')
        self.branch_names.append('thj1')
        self.branch_names.append('thj2')
        self.branch_names.append('ucsdbt0')
        self.branch_names.append('xmj1')
        self.branch_names.append('xmj2')
        # self.branch_names.append('invmassH')

        # minimum values
        self.branch_min = {}
        self.branch_min['acop'] = TMath.Pi()/20
        self.branch_min['acthm'] = float(1/20)
        self.branch_min['btag1'] = float(1/20)
        self.branch_min['btag2'] = float(1/20)
        self.branch_min['ele_ene'] = 0
        self.branch_min['ele_num'] = 0
        self.branch_min['ele_phi'] = 2*TMath.Pi()/20 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['ele_the'] = TMath.Pi()/20
        self.branch_min['encm'] = 0
        self.branch_min['enj1'] = 20
        self.branch_min['enj2'] = 20
        self.branch_min['fmvis'] = 60
        self.branch_min['ievt'] = 0
        self.branch_min['irun'] = 0
        self.branch_min['maxcthj'] = float(1/20)
        self.branch_min['maxxov'] = float(1/20)
        self.branch_min['mmis'] = 45
        self.branch_min['muon_ene'] = 0
        self.branch_min['muon_num'] = 0
        self.branch_min['muon_phi'] = 2*TMath.Pi()/20 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['muon_the'] = TMath.Pi()/20
        self.branch_min['mvis'] = 40
        self.branch_min['mvissc'] = 50
        self.branch_min['phj1'] = 0 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['phj2'] = 0 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['pho_ene'] = 0
        self.branch_min['pho_num'] = 0
        self.branch_min['pho_phi'] = 2*TMath.Pi()/20 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['pho_the'] = TMath.Pi()/20
        self.branch_min['thj1'] = 0
        self.branch_min['thj2'] = 0
        self.branch_min['ucsdbt0'] = 0
        self.branch_min['xmj1'] = 0 # there may be many 0 of events without jets
        self.branch_min['xmj2'] = 0 # there may be many 0 of events without jets
        # self.branch_min['invmassH'] = 10

        # maximum values
        self.branch_max = {}
        self.branch_max['acop'] = TMath.Pi()
        self.branch_max['acthm'] = 1
        self.branch_max['btag1'] = 1
        self.branch_max['btag2'] = 1
        self.branch_max['ele_ene'] = 70
        self.branch_max['ele_num'] = 4
        self.branch_max['ele_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['ele_the'] = TMath.Pi()
        self.branch_max['encm'] = 200
        self.branch_max['enj1'] = 100
        self.branch_max['enj2'] = 100
        self.branch_max['fmvis'] = 110
        self.branch_max['ievt'] = 5000
        self.branch_max['irun'] = 1000000
        self.branch_max['maxcthj'] = 1
        self.branch_max['maxxov'] = 1
        self.branch_max['mmis'] = 135
        self.branch_max['muon_ene'] = 20
        self.branch_max['muon_num'] = 3
        self.branch_max['muon_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['muon_the'] = TMath.Pi()
        self.branch_max['mvis'] = 150
        self.branch_max['mvissc'] = 100
        self.branch_max['phj1'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['phj2'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['pho_ene'] = 70
        self.branch_max['pho_num'] = 6
        self.branch_max['pho_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['pho_the'] = TMath.Pi()
        self.branch_max['thj1'] = 3
        self.branch_max['thj2'] = 3
        self.branch_max['ucsdbt0'] = 20
        self.branch_max['xmj1'] = 80
        self.branch_max['xmj2'] = 60
        # self.branch_max['invmassH'] = 150

        # number of bins
        self.branch_numbins = {}
        self.branch_numbins['acop'] = 19
        self.branch_numbins['acthm'] = 19
        self.branch_numbins['btag1'] = 19
        self.branch_numbins['btag2'] = 19
        self.branch_numbins['ele_ene'] = 14
        self.branch_numbins['ele_num'] = 4
        self.branch_numbins['ele_phi'] = 19
        self.branch_numbins['ele_the'] = 19
        self.branch_numbins['encm'] = 40
        self.branch_numbins['enj1'] = 16
        self.branch_numbins['enj2'] = 16
        self.branch_numbins['fmvis'] = 10
        self.branch_numbins['ievt'] = 100
        self.branch_numbins['irun'] = 100
        self.branch_numbins['maxcthj'] = 19
        self.branch_numbins['maxxov'] = 19
        self.branch_numbins['mmis'] = 18
        self.branch_numbins['muon_ene'] = 4
        self.branch_numbins['muon_num'] = 3
        self.branch_numbins['muon_phi'] = 19
        self.branch_numbins['muon_the'] = 19
        self.branch_numbins['mvis'] = 22
        self.branch_numbins['mvissc'] = 10
        self.branch_numbins['phj1'] = 20
        self.branch_numbins['phj2'] = 20
        self.branch_numbins['pho_ene'] = 14
        self.branch_numbins['pho_num'] = 6
        self.branch_numbins['pho_phi'] = 19
        self.branch_numbins['pho_the'] = 19
        self.branch_numbins['thj1'] = 20
        self.branch_numbins['thj2'] = 20
        self.branch_numbins['ucsdbt0'] = 20
        self.branch_numbins['xmj1'] = 16
        self.branch_numbins['xmj2'] = 12
        # self.branch_numbins['invmassH'] = 28

        self.branch_85_lowcut = {}
        self.branch_85_lowcut['acop'] = 1.4
        self.branch_85_lowcut['acthm'] = 0
        self.branch_85_lowcut['btag1'] = 0.3
        self.branch_85_lowcut['btag2'] = 0.3
        self.branch_85_lowcut['ele_ene'] = 0
        self.branch_85_lowcut['ele_num'] = 0
        self.branch_85_lowcut['ele_phi'] = 0
        self.branch_85_lowcut['ele_the'] = 0
        self.branch_85_lowcut['encm'] = -1
        self.branch_85_lowcut['enj1'] = 35
        self.branch_85_lowcut['enj2'] = 20
        self.branch_85_lowcut['fmvis'] = -1
        self.branch_85_lowcut['ievt'] = -1
        self.branch_85_lowcut['irun'] = -1
        self.branch_85_lowcut['maxcthj'] = 0.04
        self.branch_85_lowcut['maxxov'] = 0.12
        self.branch_85_lowcut['mmis'] = 82
        self.branch_85_lowcut['muon_ene'] = 0
        self.branch_85_lowcut['muon_num'] = 0
        self.branch_85_lowcut['muon_phi'] = 0
        self.branch_85_lowcut['muon_the'] = 0.82
        self.branch_85_lowcut['mvis'] = -1
        self.branch_85_lowcut['mvissc'] = -1
        self.branch_85_lowcut['phj1'] = 0
        self.branch_85_lowcut['phj2'] = 0
        self.branch_85_lowcut['pho_ene'] = 1.2
        self.branch_85_lowcut['pho_num'] = 0
        self.branch_85_lowcut['pho_phi'] = 0
        self.branch_85_lowcut['pho_the'] = 0
        self.branch_85_lowcut['thj1'] = 0.9
        self.branch_85_lowcut['thj2'] = 0.9
        self.branch_85_lowcut['ucsdbt0'] = 2
        self.branch_85_lowcut['xmj1'] = 1
        self.branch_85_lowcut['xmj2'] = 1
        # self.branch_85_lowcut['invmassH'] = 28

        self.branch_85_highcut = {}
        self.branch_85_highcut['acop'] = 2.8
        self.branch_85_highcut['acthm'] = 0.65
        self.branch_85_highcut['btag1'] = 1
        self.branch_85_highcut['btag2'] = 1
        self.branch_85_highcut['ele_ene'] = 1000
        self.branch_85_highcut['ele_num'] = 2
        self.branch_85_highcut['ele_phi'] = 1000
        self.branch_85_highcut['ele_the'] = 1000
        self.branch_85_highcut['encm'] = 1000
        self.branch_85_highcut['enj1'] = 68
        self.branch_85_highcut['enj2'] = 45
        self.branch_85_highcut['fmvis'] = 1000
        self.branch_85_highcut['ievt'] = 100000
        self.branch_85_highcut['irun'] = 100000
        self.branch_85_highcut['maxcthj'] = 0.84
        self.branch_85_highcut['maxxov'] = 0.44
        self.branch_85_highcut['mmis'] = 106
        self.branch_85_highcut['muon_ene'] = 1000
        self.branch_85_highcut['muon_num'] = 2
        self.branch_85_highcut['muon_phi'] = 1000
        self.branch_85_highcut['muon_the'] = 1.674
        self.branch_85_highcut['mvis'] = 1000
        self.branch_85_highcut['mvissc'] = 1000
        self.branch_85_highcut['phj1'] = 1000
        self.branch_85_highcut['phj2'] = 1000
        self.branch_85_highcut['pho_ene'] = 10.2
        self.branch_85_highcut['pho_num'] = 2
        self.branch_85_highcut['pho_phi'] = 1000
        self.branch_85_highcut['pho_the'] = 1000
        self.branch_85_highcut['thj1'] = 2.4
        self.branch_85_highcut['thj2'] = 2.4
        self.branch_85_highcut['ucsdbt0'] = 10
        self.branch_85_highcut['xmj1'] = 40
        self.branch_85_highcut['xmj2'] = 24
        # self.branch_85_highcut['invmassH'] = 28

        self.branch_90_lowcut = {}
        self.branch_90_lowcut['acop'] = 1.4
        self.branch_90_lowcut['acthm'] = 0
        self.branch_90_lowcut['btag1'] = 0.3
        self.branch_90_lowcut['btag2'] = 0.3
        self.branch_90_lowcut['ele_ene'] = 0
        self.branch_90_lowcut['ele_num'] = 0
        self.branch_90_lowcut['ele_phi'] = 0
        self.branch_90_lowcut['ele_the'] = 0
        self.branch_90_lowcut['encm'] = 0
        self.branch_90_lowcut['enj1'] = 36
        self.branch_90_lowcut['enj2'] = 30
        self.branch_90_lowcut['fmvis'] = -1
        self.branch_90_lowcut['ievt'] = -1
        self.branch_90_lowcut['irun'] = -1
        self.branch_90_lowcut['maxcthj'] = 0.04
        self.branch_90_lowcut['maxxov'] = 0.12
        self.branch_90_lowcut['mmis'] = 80
        self.branch_90_lowcut['muon_ene'] = 0
        self.branch_90_lowcut['muon_num'] = 0
        self.branch_90_lowcut['muon_phi'] = 0
        self.branch_90_lowcut['muon_the'] = 0.94
        self.branch_90_lowcut['mvis'] = -1
        self.branch_90_lowcut['mvissc'] = -1
        self.branch_90_lowcut['phj1'] = 0
        self.branch_90_lowcut['phj2'] = 0
        self.branch_90_lowcut['pho_ene'] = 1.2
        self.branch_90_lowcut['pho_num'] = 0
        self.branch_90_lowcut['pho_phi'] = 0
        self.branch_90_lowcut['pho_the'] = 0
        self.branch_90_lowcut['thj1'] = 0.9
        self.branch_90_lowcut['thj2'] = 0.9
        self.branch_90_lowcut['ucsdbt0'] = 2
        self.branch_90_lowcut['xmj1'] = 1
        self.branch_90_lowcut['xmj2'] = 1
        # self.branch_90_lowcut['invmassH'] = 28

        self.branch_90_highcut = {}
        self.branch_90_highcut['acop'] = 2.8
        self.branch_90_highcut['acthm'] = 0.68
        self.branch_90_highcut['btag1'] = 1
        self.branch_90_highcut['btag2'] = 1
        self.branch_90_highcut['ele_ene'] = 1000
        self.branch_90_highcut['ele_num'] = 2
        self.branch_90_highcut['ele_phi'] = 1000
        self.branch_90_highcut['ele_the'] = 1000
        self.branch_90_highcut['encm'] = 1000
        self.branch_90_highcut['enj1'] = 68
        self.branch_90_highcut['enj2'] = 53
        self.branch_90_highcut['fmvis'] = 1000
        self.branch_90_highcut['ievt'] = 100000
        self.branch_90_highcut['irun'] = 100000
        self.branch_90_highcut['maxcthj'] = 0.84
        self.branch_90_highcut['maxxov'] = 0.44
        self.branch_90_highcut['mmis'] = 106
        self.branch_90_highcut['muon_ene'] = 1000
        self.branch_90_highcut['muon_num'] = 2
        self.branch_90_highcut['muon_phi'] = 1000
        self.branch_90_highcut['muon_the'] = 1.98
        self.branch_90_highcut['mvis'] = 1000
        self.branch_90_highcut['mvissc'] = 1000
        self.branch_90_highcut['phj1'] = 1000
        self.branch_90_highcut['phj2'] = 1000
        self.branch_90_highcut['pho_ene'] = 9.8
        self.branch_90_highcut['pho_num'] = 2
        self.branch_90_highcut['pho_phi'] = 1000
        self.branch_90_highcut['pho_the'] = 1000
        self.branch_90_highcut['thj1'] = 2.4
        self.branch_90_highcut['thj2'] = 2.4
        self.branch_90_highcut['ucsdbt0'] = 10
        self.branch_90_highcut['xmj1'] = 40
        self.branch_90_highcut['xmj2'] = 30
        # self.branch_90_highcut['invmassH'] = 28

        self.branch_95_lowcut = {}
        self.branch_95_lowcut['acop'] = 1.4
        self.branch_95_lowcut['acthm'] = 0
        self.branch_95_lowcut['btag1'] = 0.3
        self.branch_95_lowcut['btag2'] = 0.3
        self.branch_95_lowcut['ele_ene'] = 0
        self.branch_95_lowcut['ele_num'] = 0
        self.branch_95_lowcut['ele_phi'] = 0
        self.branch_95_lowcut['ele_the'] = 0
        self.branch_95_lowcut['encm'] = -1
        self.branch_95_lowcut['enj1'] = 36
        self.branch_95_lowcut['enj2'] = 20
        self.branch_95_lowcut['fmvis'] = -1
        self.branch_95_lowcut['ievt'] = -1
        self.branch_95_lowcut['irun'] = -1
        self.branch_95_lowcut['maxcthj'] = 0.04
        self.branch_95_lowcut['maxxov'] = 0.12
        self.branch_95_lowcut['mmis'] = 80
        self.branch_95_lowcut['muon_ene'] = 0
        self.branch_95_lowcut['muon_num'] = 0
        self.branch_95_lowcut['muon_phi'] = 0
        self.branch_95_lowcut['muon_the'] = 0.92
        self.branch_95_lowcut['mvis'] = -1
        self.branch_95_lowcut['mvissc'] = -1
        self.branch_95_lowcut['phj1'] = 0
        self.branch_95_lowcut['phj2'] = 0
        self.branch_95_lowcut['pho_ene'] = 1
        self.branch_95_lowcut['pho_num'] = 0
        self.branch_95_lowcut['pho_phi'] = 0
        self.branch_95_lowcut['pho_the'] = 0
        self.branch_95_lowcut['thj1'] = 0.9
        self.branch_95_lowcut['thj2'] = 0.9
        self.branch_95_lowcut['ucsdbt0'] = 2
        self.branch_95_lowcut['xmj1'] = 1
        self.branch_95_lowcut['xmj2'] = 1
        # self.branch_95_lowcut['invmassH'] = 28

        self.branch_95_highcut = {}
        self.branch_95_highcut['acop'] = 2.8
        self.branch_95_highcut['acthm'] = 0.71
        self.branch_95_highcut['btag1'] = 1
        self.branch_95_highcut['btag2'] = 1
        self.branch_95_highcut['ele_ene'] = 1000
        self.branch_95_highcut['ele_num'] = 2
        self.branch_95_highcut['ele_phi'] = 1000
        self.branch_95_highcut['ele_the'] = 1000
        self.branch_95_highcut['encm'] = 1000
        self.branch_95_highcut['enj1'] = 68
        self.branch_95_highcut['enj2'] = 52
        self.branch_95_highcut['fmvis'] = 1000
        self.branch_95_highcut['ievt'] = 100000
        self.branch_95_highcut['irun'] = 100000
        self.branch_95_highcut['maxcthj'] = 0.84
        self.branch_95_highcut['maxxov'] = 0.44
        self.branch_95_highcut['mmis'] = 104
        self.branch_95_highcut['muon_ene'] = 1000
        self.branch_95_highcut['muon_num'] = 2
        self.branch_95_highcut['muon_phi'] = 1000
        self.branch_95_highcut['muon_the'] = 1.67
        self.branch_95_highcut['mvis'] = 1000
        self.branch_95_highcut['mvissc'] = 1000
        self.branch_95_highcut['phj1'] = 1000
        self.branch_95_highcut['phj2'] = 1000
        self.branch_95_highcut['pho_ene'] = 10.2
        self.branch_95_highcut['pho_num'] = 2
        self.branch_95_highcut['pho_phi'] = 1000
        self.branch_95_highcut['pho_the'] = 1000
        self.branch_95_highcut['thj1'] = 2.4
        self.branch_95_highcut['thj2'] = 2.4
        self.branch_95_highcut['ucsdbt0'] = 10
        self.branch_95_highcut['xmj1'] = 40
        self.branch_95_highcut['xmj2'] = 30
        # self.branch_95_highcut['invmassH'] = 28

        self.toggle_cuts = {}
        self.toggle_cuts['acop'] = 1
        self.toggle_cuts['acthm'] = 0
        self.toggle_cuts['btag1'] = 1
        self.toggle_cuts['btag2'] = 1
        self.toggle_cuts['ele_ene'] = 0
        self.toggle_cuts['ele_num'] = 0
        self.toggle_cuts['ele_phi'] = 0
        self.toggle_cuts['ele_the'] = 0
        self.toggle_cuts['encm'] = 0
        self.toggle_cuts['enj1'] = 1
        self.toggle_cuts['enj2'] = 1
        self.toggle_cuts['fmvis'] = 0
        self.toggle_cuts['ievt'] = 0
        self.toggle_cuts['irun'] = 0
        self.toggle_cuts['maxcthj'] = 0
        self.toggle_cuts['maxxov'] = 0
        self.toggle_cuts['mmis'] = 0
        self.toggle_cuts['muon_ene'] = 0
        self.toggle_cuts['muon_num'] = 0
        self.toggle_cuts['muon_phi'] = 0
        self.toggle_cuts['muon_the'] = 0
        self.toggle_cuts['mvis'] = 0
        self.toggle_cuts['mvissc'] = 0
        self.toggle_cuts['phj1'] = 0
        self.toggle_cuts['phj2'] = 0
        self.toggle_cuts['pho_ene'] = 0
        self.toggle_cuts['pho_num'] = 0
        self.toggle_cuts['pho_phi'] = 0
        self.toggle_cuts['pho_the'] = 0
        self.toggle_cuts['thj1'] = 1
        self.toggle_cuts['thj2'] = 1
        self.toggle_cuts['ucsdbt0'] = 1
        self.toggle_cuts['xmj1'] = 1
        self.toggle_cuts['xmj2'] = 1
        # self.toggle_cuts['invmassH'] = 28

        self.monte_carlo_to_analyse = '85'
        self.test_statistics_branch = 'mvissc'
        self.number_toys = 10
        self.bins_q_histos = 100
        self.silent_analysis = 0

    def change_cut_low(self, branch, value):
        self.branch_85_lowcut[branch] = value
        self.branch_90_lowcut[branch] = value
        self.branch_95_lowcut[branch] = value

    def change_cut_high(self, branch, value):
        self.branch_85_highcut[branch] = value
        self.branch_90_highcut[branch] = value
        self.branch_95_highcut[branch] = value

    def change_montecarlo_to_analyse(self, mc):
        self.monte_carlo_to_analyse = mc

    def change_test_statistics_branch(self, teststat):
        self.test_statistics_branch = teststat

    def change_toggle_cuts(self, branch, value):
        self.toggle_cuts[branch] = value

    def switch_off_all_cuts(self):
        for branch in self.branch_names:
            self.change_toggle_cuts(branch, 0)

    def change_silent_analysis(self, value):
        self.silent_analysis = value

    def change_number_toys(self, number):
        self.number_toys = number