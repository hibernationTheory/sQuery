import fnmatch

def methodName(fn):
    def inner(*args, **kwargs):
        """
        feeds the name of the method as an argument to the method itself
        """
        kwargs["methodName"] = fn.func_name
        fn(*args, **kwargs)
    return inner

class SQueryCommon(object):
    def __init__(self, initValue=None, data=[]):
        self._data = data

    def __str__(self):
        for i in self._data:
            print i

    def _getAttrMultiple(self, data, **kwargs):
        """
        runs the _getAttr method on a given set of data
        """
        returnData = []
        if not data:
            return returnData

        for i in data:
            result = self._getAttr(i, **kwargs)
            if result:
                returnData.append(result)
        return returnData

    def _getAttr(self, node, **kwargs):
        """
        makes calls to the given list of attributes on an object
        """
        
        methods = kwargs.get("methods", None)

        if not methods or not node:
            return None

        lenMethods = len(methods)
        for method in methods:
            if isinstance(method, tuple):
                result = getattr(node, method[0])
                type = "tuple"
            else:
                result = getattr(node, method)
                type = "nonTuple"
            if not result:
                return None
            if lenMethods != 1:
                remainingMethods = methods[1:]
                if type == "tuple":
                    result = self._getAttr(result(method[1]), **{"methods":remainingMethods})
                else:
                    result = self._getAttr(result(), **{"methods":remainingMethods})
                if not result:
                    return None
                break
            else:
                if type=="tuple":
                    return result(method[1])
                else:
                    return result()

        return result

    def _filterData(self, data, **kwargs):
        #print "\nfunc _filterData"
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})
        filterValue = kwargs.get("filterValue", None)
        filterFunction = kwargs.get("filterFunction", None)
        filterFunctionKwargs = kwargs.get("filterFunctionKwargs", {})

        if callback:
            result = callback(data, **callbackKwargs)
        else:
            result = data

        if filterFunction and filterValue:
            filterResult = filterFunction(data, **filterFunctionKwargs)
            if filterResult == filterValue:
                if data:return data

        elif not filterFunction and filterValue:
            if result == filterValue:
                if data:return data

        elif filterFunction and not filterValue: #!?
            filterResult = filterFunction(data, **filterFunctionKwargs)
            if filterResult:return data

        else: # if no filter function action happening
            if result:return result

    def _fnMatch(self, name, **kwargs):
        pattern = kwargs.get("pattern", None)
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})
        result = None

        if not pattern:
            return None

        if callback:
            name = callback(name, **callbackKwargs)

        if name:
            result = fnmatch.fnmatch(name, pattern)
        return result