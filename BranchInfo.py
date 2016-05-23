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

class BranchInfo:
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

        # minimum values
        self.branch_min = {}
        self.branch_min['acop'] = TMath.Pi()/100
        self.branch_min['acthm'] = 0.01
        self.branch_min['btag1'] = 0
        self.branch_min['btag2'] = 0
        self.branch_min['ele_ene'] = 0
        self.branch_min['ele_num'] = 0
        self.branch_min['ele_phi'] = 2*TMath.Pi()/100 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['ele_the'] = TMath.Pi()/100
        self.branch_min['encm'] = 0
        self.branch_min['enj1'] = 0
        self.branch_min['enj2'] = 0
        self.branch_min['fmvis'] = 0
        self.branch_min['ievt'] = 0
        self.branch_min['irun'] = 0
        self.branch_min['maxcthj'] = 0
        self.branch_min['maxxov'] = 0
        self.branch_min['mmis'] = 0
        self.branch_min['muon_ene'] = 0
        self.branch_min['muon_num'] = 0
        self.branch_min['muon_phi'] = 2*TMath.Pi()/100 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['muon_the'] = TMath.Pi()/100
        self.branch_min['mvis'] = 0
        self.branch_min['mvissc'] = 0
        self.branch_min['phj1'] = 0 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['phj2'] = 0 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['pho_ene'] = 0
        self.branch_min['pho_num'] = 0
        self.branch_min['pho_phi'] = 2*TMath.Pi()/100 # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_min['pho_the'] = TMath.Pi()/100
        self.branch_min['thj1'] = 0
        self.branch_min['thj2'] = 0
        self.branch_min['ucsdbt0'] = 0
        self.branch_min['xmj1'] = 0 # there may be many 0 of events without jets
        self.branch_min['xmj2'] = 0 # there may be many 0 of events without jets
        
        # maximum values
        self.branch_max = {}
        self.branch_max['acop'] = TMath.Pi()
        self.branch_max['acthm'] = 1
        self.branch_max['btag1'] = 1
        self.branch_max['btag2'] = 1
        self.branch_max['ele_ene'] = 1000
        self.branch_max['ele_num'] = 4
        self.branch_max['ele_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['ele_the'] = TMath.Pi()
        self.branch_max['encm'] = 200
        self.branch_max['enj1'] = 1000
        self.branch_max['enj2'] = 1000
        self.branch_max['fmvis'] = 1000
        self.branch_max['ievt'] = 5000
        self.branch_max['irun'] = 1000000
        self.branch_max['maxcthj'] = 1
        self.branch_max['maxxov'] = 1
        self.branch_max['mmis'] = 150
        self.branch_max['muon_ene'] = 50
        self.branch_max['muon_num'] = 3
        self.branch_max['muon_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['muon_the'] = TMath.Pi()
        self.branch_max['mvis'] = 150
        self.branch_max['mvissc'] = 150
        self.branch_max['phj1'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['phj2'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['pho_ene'] = 1000
        self.branch_max['pho_num'] = 5
        self.branch_max['pho_phi'] = 2*TMath.Pi() # check if it starts from 0 to 2 Pi or if it is from -Pi to Pi
        self.branch_max['pho_the'] = TMath.Pi()
        self.branch_max['thj1'] = TMath.Pi()
        self.branch_max['thj2'] = TMath.Pi()
        self.branch_max['ucsdbt0'] = 16
        self.branch_max['xmj1'] = 90
        self.branch_max['xmj2'] = 150

        # number of bins
        self.branch_numbins = {}
        self.branch_numbins['acop'] = 100
        self.branch_numbins['acthm'] = 100
        self.branch_numbins['btag1'] = 100
        self.branch_numbins['btag2'] = 100
        self.branch_numbins['ele_ene'] = 100
        self.branch_numbins['ele_num'] = 4
        self.branch_numbins['ele_phi'] = 100
        self.branch_numbins['ele_the'] = 100
        self.branch_numbins['encm'] = 100
        self.branch_numbins['enj1'] = 100
        self.branch_numbins['enj2'] = 100
        self.branch_numbins['fmvis'] = 100
        self.branch_numbins['ievt'] = 100
        self.branch_numbins['irun'] = 100
        self.branch_numbins['maxcthj'] = 100
        self.branch_numbins['maxxov'] = 100
        self.branch_numbins['mmis'] = 150
        self.branch_numbins['muon_ene'] = 100
        self.branch_numbins['muon_num'] = 3
        self.branch_numbins['muon_phi'] = 100
        self.branch_numbins['muon_the'] = 100
        self.branch_numbins['mvis'] = 150
        self.branch_numbins['mvissc'] = 150
        self.branch_numbins['phj1'] = 100
        self.branch_numbins['phj2'] = 100
        self.branch_numbins['pho_ene'] = 100
        self.branch_numbins['pho_num'] = 5
        self.branch_numbins['pho_phi'] = 100
        self.branch_numbins['pho_the'] = 100
        self.branch_numbins['thj1'] = 100
        self.branch_numbins['thj2'] = 100
        self.branch_numbins['ucsdbt0'] = 16
        self.branch_numbins['xmj1'] = 150
        self.branch_numbins['xmj2'] = 150