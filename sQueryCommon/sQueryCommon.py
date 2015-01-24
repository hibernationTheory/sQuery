import fnmatch

class SQueryCommon(object):
    def __init__(self, initValue=None, data=[]):
        self._data = data

    """
    def __str__(self):
        for i in self._data:
            if i:
                print i
    """

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
            if isinstance(method, dict):
                result = getattr(node, method["name"])
                if method.get("args", None) is None:
                    method["args"] = ()
                if method.get("kwargs", None) is None:
                    method["kwargs"] = {}

                if isinstance(method["args"], list):
                    #wrong data type, it should have been a tuple, convert
                    method["args"] = tuple(method["args"])
                if not isinstance(method["args"], tuple):
                    #you are forgetting to provide tuples for single arg, compansate for
                    #convenience
                    method["args"] = (method["args"],)
                type = "dict"

            else:
                result = getattr(node, method)
                type = "nonDict"
            if result is None:
                return None

            if lenMethods != 1:
                remainingMethods = methods[1:]
                if type == "dict":
                    result = self._getAttr(result(*method["args"], **method["kwargs"]), **{"methods":remainingMethods})
                else:
                    result = self._getAttr(result(), **{"methods":remainingMethods})
                if result is None:
                    return None
                break
            else:
                if type=="dict":
                    return result(*method["args"], **method["kwargs"])
                else:
                    return result()

        return result

    def _filterDataMultiple(self, data, filterMultipleOptions):
        for option in filterMultipleOptions:
            result = self._filterData(data, **option)
            if result != None:
                return result
        return None

    def _filterData(self, data, **kwargs):
        # filters the given scene object using the kwargs parameters
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})
        filterValue = kwargs.get("filterValue", None)
        filterFunction = kwargs.get("filterFunction", None)
        filterFunctionKwargs = kwargs.get("filterFunctionKwargs", {})
        postFilterFunction = kwargs.get("postFilterFunction", None)
        postFilterFunctionKwargs = kwargs.get("postFilterFunctionKwargs", None)

        if callback:
            result = callback(data, **callbackKwargs)
        else:
            result = data

        if filterFunction and filterValue:
            filterResult = filterFunction(data, **filterFunctionKwargs)
            if postFilterFunction:
                postResult = postFilterFunction(filterResult, **postFilterFunctionKwargs)
                if postResult:
                    return data
            if filterResult == filterValue:
                return data

        elif filterFunction and not filterValue:
            filterResult = filterFunction(data, **filterFunctionKwargs)
            if postFilterFunction:
                postResult = postFilterFunction(filterResult, **postFilterFunctionKwargs)
                if postResult:
                    return data
            if filterResult:
                return data

        else: # if no filter function action happening
            return result

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