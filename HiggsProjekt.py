# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile
from glob import glob
from copy import deepcopy
<<<<<<< HEAD

__author__ = 'Pin-Jung & Diego Alejandro'
=======
from Utils import *

>>>>>>> cfe1aabcb60022fa961d7db9d25380a7a2aac6be

class Analsis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'

        # dictionary of the tree name and the tree
        self.trees = self.load_trees()

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        dic = {f.GetName().split('/')[-1].strip('.root'): t for f, t in zip(files, trees)}
        return deepcopy(dic)


__author__ = 'micha'

if __name__ == '__main__':
    print_banner('STARTING HIGGS ANALYSIS')
    z = Analsis()
