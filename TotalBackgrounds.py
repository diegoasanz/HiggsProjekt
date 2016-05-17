# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Pin-Jung Diego Alejandro
# ---------------------------------------------------

from ROOT import TFile
from ROOT import TTree
from ROOT import TH1F
from glob import glob
from copy import deepcopy

__author__ = 'Pin-Jung & Diego Alejandro'

from Utils import *

class TotalBrackgrounds:
    def __init__(self,names,data_trees,branches_nbins,branches_mins,branches_maxs):
        branchtemp='acop'

        