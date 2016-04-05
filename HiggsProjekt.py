# ---------------------------------------------------
#           HIGGS PROJECT for SMATEP
#   author: Michael Reichmann
# ---------------------------------------------------

from ROOT import TFile
from glob import glob
from copy import deepcopy



class Analsis:
    def __init__(self):

        self.DataFolder = 'l3higgs189/'
        self.trees = self.load_trees()

    def load_trees(self):
        files = [TFile(f) for f in glob('{dir}*.root'.format(dir=self.DataFolder))]
        trees = [f.Get('h20') for f in files]
        return deepcopy(trees)

if __name__ == "__main__":
    z = Analsis()