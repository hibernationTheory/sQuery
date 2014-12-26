import fnmatch

class SQueryCommon(object):
    def __init__(self, initValue=None, data=[]):
        self._data = data

    def __str__(self):
        for i in self._data:
            print i

    def _callAttr(self, **kwargs):
        data = kwargs.get("data", None)
        attr = kwargs.get("attr", None)
        value = kwargs.get("value", None)

        returnData = None

        if not data or not attr:
            return None

        if value != None:
            result = getattr(data, attr)(value)
            if result != None: return result
        else:
            result = getattr(data, attr)()
            if result != None: return result

        return returnData

    def _callAttrOnMultiple(self, **kwargs):
        data = kwargs.get("data", None)
        returnData = []
        if not data:
            return returnData

        for i in data:
            newKwargs = kwargs.copy()
            newKwargs["data"] = i
            self._callAttr(**newKwargs)

    def _getAttrMultiple(self, node, **kwargs):
        #print "\nfunc _getAttrMultiple"
        
        methods = kwargs.get("methods", None)

        if not methods:
            return None

        lenMethods = len(methods)
        for method in methods:
            result = getattr(node, method)
            if lenMethods != 1:
                remainingMethods = methods[1:]
                result = self._getAttrMultiple(result(), **{"methods":remainingMethods})
                break
            else:
                return result()
        return result


    def _filterData(self, **kwargs):
        #print "\nfunc _filterData"
        data = kwargs.get("data", None)
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})
        filterValue = kwargs.get("filterValue", None)
        filterFunction = kwargs.get("filterFunction", None)
        filterFunctionKwargs = kwargs.get("filterFunctionKwargs", {})

        if not data:
            return None

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

        elif filterFunction and not filterValue: # this condition doesn't make sense actually
            if data:return data

        else: # if not filter function action happening
            if result:return result

    def _fnMatch(self, name, **kwargs):
        pattern = kwargs.get("pattern", None)
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})

        if not pattern:
            return None

        if callback:
            name = callback(name, **callbackKwargs)

        result = fnmatch.fnmatch(name, pattern)
        return result