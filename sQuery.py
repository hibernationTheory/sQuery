########## houCommon v002 #################
import hou
import fnmatch

class SceneQuery(object):
    def __init__(self,data=[], context=None):
        self._data = data
        self._main(self._data)
        print self._data

    def __str__(self):
        for i in self._data:
            print i

    def _main(self, data):
        self._env = self._getEnv()
        if self._env == "hou":
            self._initHoudini(data)

    def _getEnv(self):
        #print "\nfunc _getEnv"

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

        return env

    def _cleanupData(self):
        pass

    def _initHoudini(self, context):
        #print "\nfunc _initHoudini"

        contexts = ["obj", "shop", "out"]
        if self._data in contexts:
            self._data = [hou.node("/" + self._data)]

    def selectByType(self, filterName):
        #print "\nfunc selectByType"

        if not filterName:
            return None

        filterFunction = None
        filterFunctionKwargs = {}
        filterValue = filterName

        if filterName.find("*") != -1:
            filterFunction = self._fnmatchHouObj
            filterFunctionKwargs = {"pattern":filterName}
            filterValue = True

        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._getAttrMultiple,
            "callbackKwargs":{"methods":["type", "name"]},
            "filterValue":filterName,
            "filterFunction":filterFunction,
            "filterFunctionKwargs":filterFunctionKwargs,
            "filterValue":filterValue
            })

        return SceneQuery(data=returnData)

    def selectByName(self, filterName):
        #print "\nfunc selectByName"

        if not filterName:
            return None

        filterFunction = None
        filterFunctionKwargs = {}
        filterValue = filterName

        if filterName.find("*") != -1:
            filterFunction = self._fnmatchHouObj
            filterFunctionKwargs = {"pattern":filterName}
            filterValue = True

        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._getAttrMultiple,
            "callbackKwargs":{"methods":["name"]},
            "filterValue":filterName,
            "filterFunction":filterFunction,
            "filterFunctionKwargs":filterFunctionKwargs,
            "filterValue":filterValue
            })

        return SceneQuery(data=returnData)

    def children(self):
        #print "\nfunc children"

        returnData = []
        for data in self._data:
            for child in data.children():
                returnData.append(child)

        return SceneQuery(data=returnData)

    #################
    # CONTENT FILTERS
    #################

    def parmEqualTo(self, targetValue):
        #print "\nfunc parmEqualTo"
        returnData = []
        for i in self._data:
            value = i.eval()
            if value == targetValue:
                returnData.append(i)

        return SceneQuery(data=returnData)

    def parmContains(self, targetValue):
        #print "\nfunc parmContains"
        returnData = []
        for i in self._data:
            value = i.eval()
            if isinstance(value, str):
                if value.find(targetValue) != -1:
                    returnData.append(i)

        return SceneQuery(data=returnData)

    #################
    # PARM STUFF
    #################

    def parm(self, parmName, parmValue = None):
        #print "\nfunc parm"

        returnData = []
        for i in self._data:
            parm = i.parm(parmName)
            if parmValue:
                parm.set(parmValue)
            returnData.append(parm)

        return SceneQuery(data=returnData)

    def setParmValue(self, parmValue):
        self._callAttr(**{
            "data":self._data,
             "attr":"set",
             "value":parmValue
            })
        return SceneQuery(data=self._data)

    def replaceParmValue(self, parmValue, targetValue):
        for i in self._data:
            value = i.eval()
            newValue = value.replace(parmValue, targetValue)
            i.set(newValue)
        return SceneQuery(data=self._data)

    def evalParm(self):
        values = self._callAttr(**{
            "data":self._data,
             "attr":"eval",
            })
        return SceneQuery(data=values)

    #################
    # BUNDLE STUFF
    #################

    def checkBundle(self, value):
        """given the string value, checks if a bundle exists with the name"""
        bundles = hou.nodeBundles()
        bundleNames = [bundle.name() for bundle in bundles]

        if value in bundleNames:
            return True
        else: return False

    def addToBundle(self, bundleName):
        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._addNodeToBundle,
            "callbackKwargs":{"bundleName":bundleName},
            })

        return SceneQuery(data=returnData)

    def removeFromBundle(self, bundleName):
        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._removeNodeFromBundle,
            "callbackKwargs":{"bundleName":bundleName},
            })

        return SceneQuery(data=returnData)

    def _addNodeToBundle(self, node, **kwargs):
        bundleName = kwargs.get("bundleName", None)
        if not bundleName:
            return None

        bundle = hou.nodeBundle(bundleName)
        if not bundle:
            hou.hscript('opbadd "%s"' % bundleName)
            bundle = hou.nodeBundle(bundleName)
        if not bundle.containsNode(node):
            bundle.addNode(node)

    def _removeNodeFromBundle(self, node, **kwargs):
        bundleName = kwargs.get("bundleName", None)
        if not bundleName:
            return None

        bundle = hou.nodeBundle(bundleName)
        if not bundle or not bundle.containsNode(node):
            return None
        bundle.removeNode(node)

    #################
    # NODE STATE
    #################

    def layoutChildren(self):
        self._callAttr(**{
            "data":self._data,
             "attr":"layoutChildren",
            })
        return SceneQuery(data=self._data)

    def setDisplayFlag(self, value):
        self._callAttr(**{
            "data":self._data,
             "attr":"setDisplayFlag",
             "value":value
            })
        return SceneQuery(data=self._data)

    def setRenderFlag(self, value):
        self._callAttr(**{
            "data":self._data,
             "attr":"setRenderFlag",
             "value":value
            })
        return SceneQuery(data=self._data)

    def setSelected(self, value):
        self._callAttr(**{
            "data":self._data,
             "attr":"setSelected",
             "value":value
            })
        return SceneQuery(data=self._data)

    #################
    # NODE CREATION / DELETION
    #################

    def createNodeInside(self, typeName, nodeParms=None):
        #print "\nfunc createNodeInside"

        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._createNodeInsideParent,
            "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
            })

        return SceneQuery(data=returnData)

    def createNodeAfter(self, typeName, nodeParms=None):
        #print "\nfunc createNodeAfter"

        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._createNodeAfterGivenNode,
            "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
            })

        return SceneQuery(data=returnData)

    def createNodeBefore(self, typeName, nodeParms=None):
        #print "\nfunc createNodeBefore"

        returnData = self._filterData(**{
            "data":self._data,
            "callback":self._createNodeBeforeGivenNode,
            "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
            })

        return SceneQuery(data=returnData)

    def _createNodeInsideParent(self, parent, **kwargs):
        typeName = kwargs.get("typeName", None)
        nodeName = kwargs.get("nodeName", None)
        parms = kwargs.get("parms", None)

        if not parent or not typeName:
            return None

        node = parent.createNode(typeName)
        if nodeName:
            print nodeName, node
            node.setName(nodeName)
        if parms:
            node.setParms(parms)

        return node

    def _createNodeBeforeGivenNode(self, givenNode, **kwargs):
        nodeCreated = self._createNodeInsideParent(givenNode.parent(), **kwargs)
        self._insertNode(**{
            "nodeToInsert":nodeCreated,
            "targetNode":givenNode,
            "location":"before",
            "layoutChildren":True
        })

        return nodeCreated

    def _createNodeAfterGivenNode(self, givenNode, **kwargs):
        nodeCreated = self._createNodeInsideParent(givenNode.parent(), **kwargs)
        self._insertNode(**{
            "nodeToInsert":nodeCreated,
            "targetNode":givenNode,
            "location":"after",
            "layoutChildren":True
        })

        return nodeCreated

    def _insertNode(self, **kwargs):
        nodeToInsert = kwargs.get("nodeToInsert", None)
        targetNode = kwargs.get("targetNode", None)
        location = kwargs.get("location", "before")
        targetInsertIndex = kwargs.get("targetInsertIndex", 0)
        nodeInsertIndex = kwargs.get("nodeInsertIndex", 0)
        layoutChildren = kwargs.get("layoutChildren", False)

        if not nodeToInsert or not targetNode:
            return None

        targetNodeInput = None
        targetNodeOutput = None

        if location == "before":
            targetNodeInputs = targetNode.inputs()
            if targetNodeInputs:
                targetNodeInput = targetNodeInputs[targetInsertIndex]

            targetNode.setInput(targetInsertIndex, nodeToInsert)
            if targetNodeInput:
                nodeToInsert.setInput(nodeInsertIndex, targetNodeInput)
                

        if location == "after":
            targetNodeOutputs = targetNode.outputs()
            if targetNodeOutputs:
                targetNodeOutput = targetNodeOutputs[targetInsertIndex]

            nodeToInsert.setInput(nodeInsertIndex, targetNode)
            if targetNodeOutput:
                targetNodeOutput.setInput(targetInsertIndex, nodeToInsert)

        if layoutChildren:
            parent = targetNode.parent()
            parent.layoutChildren()

        return False

    def destroy(self):
        self._callAttr(**{
            "data":self._data,
            "attr":"destroy"
            })
        return SceneQuery(data=[])


    #################
    # HELPERS
    #################

    def _fnmatchHouObj(self, name, **kwargs):
        pattern = kwargs.get("pattern", None)
        if not pattern:
            return None

        name = name.name()
        result = fnmatch.fnmatch(name, pattern)
        return result

    def _callAttr(self, **kwargs):
        data = kwargs.get("data", None)
        attr = kwargs.get("attr", None)
        value = kwargs.get("value", None)

        returnData = []

        if not data or not attr:
            return returnData

        for i in data:
            if value != None:
                result = getattr(i, attr)(value)
                if result != None: returnData.append(result)
            else:
                result = getattr(i, attr)()
                if result != None: returnData.append(result)

        return returnData


    def _filterData(self, **kwargs):
        #print "\nfunc _filterData"

        data = kwargs.get("data", None)
        callback = kwargs.get("callback", None)
        callbackKwargs = kwargs.get("callbackKwargs", {})
        filterValue = kwargs.get("filterValue", None)
        filterFunction = kwargs.get("filterFunction", None)
        filterFunctionKwargs = kwargs.get("filterFunctionKwargs", {})

        if not data:
            return []

        returnData = []

        for i in data:
            if callback:
                result = callback(i, **callbackKwargs)
            else:
                result = i

            if filterFunction and filterValue:
                filterResult = filterFunction(i, **filterFunctionKwargs)
                if filterResult == filterValue:
                    if i:returnData.append(i)

            elif not filterFunction and filterValue:
                if result == filterValue:
                    if i:returnData.append(i)

            elif filterFunction and not filterValue: # this condition doesn't make sense actually
                if i:returnData.append(i) 

            else: # if not filter function action happening
                if result:returnData.append(result)

        return returnData

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








