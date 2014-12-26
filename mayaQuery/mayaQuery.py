import os
import sys

import pymel.core as pc

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(os.pardir, CURRENT_DIR))
sys.path.insert(0, PARENT_DIR)

from sQueryCommon import sQueryCommon as sq
SQueryCommon = sq.SQueryCommon

class MayaQuery(SQueryCommon):
    def __init__(self, initValue=None, data=[]):
        SQueryCommon.__init__(self, data, initValue)

        self._data = data
        print self._data

        if initValue:
            self._init(initValue)

    def _init(self, initValue):
        #print "\nfunc _init"

        if initValue == "root":
            self._data = pc.ls()