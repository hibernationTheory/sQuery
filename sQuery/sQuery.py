import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)


def sQuery(initValue=None):
    """
    Entry point for sQuery library, creates a suitable Query Object depending on the working environment (application)
    """
    def _callQueryObject(env, initValue):
        if env == "hou":
            if not initValue:
                initValue = "obj"
            from houQuery import houQuery as hq
            reload(hq)
            queryObject = hq.HouQuery(initValue=initValue)
            return queryObject
        if env == "maya":
            if not initValue:
                initValue = "root"
            from mayaQuery import mayaQuery as mq
            reload(mq)
            queryObject = mq.MayaQuery(initValue=initValue)
            return queryObject

    env = None
    try:
        import hou
        env = "hou"
    except ImportError:
        pass

    try:
        import nuke
        env = "nuke"
    except ImportError:
        pass

    try:
        import pymel.core as pc
        env = "maya"
    except ImportError:
        pass

    queryObject = _callQueryObject(env, initValue)

    return queryObject