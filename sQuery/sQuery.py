def sQuery(initValue=None):
    """
    Entry point for sQuery library, creates a suitable Query Object depending on the working environment (application)
    """
    def _callQueryObject(env, initValue):
        if env == "hou":
            if not initValue:
                initValue = "obj"
            from houQuery import houQuery as hq
            queryObject = hq.HouQuery(initValue=initValue)
            return queryObject
        if env == "maya":
            if not initValue:
                initValue = "root"
            from mayaQuery import mayaQuery as mq
            queryObject = mq.MayaQuery(initValue=initValue, module = None)
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