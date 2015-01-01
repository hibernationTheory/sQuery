import os
import sys

import hou

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)

from sQueryCommon import sQueryCommon as sq
reload(sq)
SQueryCommon = sq.SQueryCommon

class HouQuery(SQueryCommon):
    def __init__(self, initValue=None, data=[], prevData = []):
        SQueryCommon.__init__(self, data, initValue)
        self._data = data
        self._prevData = prevData
        print self._data

        if initValue:
            self._init(initValue)

    def _init(self, initValue):
        #print "\nfunc _init"

        contexts = ["obj", "shop", "out"]
        if initValue in contexts:
            self._data = [hou.node("/" + initValue)]

    def _parseAttributeFilterSyntax(self, filterData):
        if not filterData.startswith("[") and not filterData.endswith("]"):
            return None
        if filterData.count("=") > 1:
            print "This object doesn't handle parameter expressions that has more than 1 '='"
            return None
        if filterData.find("=") != -1:
            return "attrValue"
        else:
            return "attr"

    def _parseAttributeFilterData(self, filterData):
        if not filterData.startswith("[") and not filterData.endswith("]"):
            return None
        if filterData.count("=") > 1:
            print "This object doesn't handle parameter expressions that has more than 1 '='"
            return None

        filterDataContent = filterData[1:-1]
        eqSignLoc = filterDataContent.find("=")
        if eqSignLoc == -1:
            filterParmName = filterDataContent
            filterParmValue = None
        else:
            filterParmName = filterDataContent[:eqSignLoc]
            filterParmValue = filterDataContent[eqSignLoc+1:]

        return {"filterParmName":filterParmName, "filterParmValue":filterParmValue}

    def _generateFilterOptions(self, filterData=None):
        """
        Generates the options that are going to be required by filtering operations based on given data
        """

        callbackKwargsValue = None
        filterName = ""
        filterFunction = None
        filterFunctionKwargs = {}
        callback = None
        callbackKwargs = None
        filterKind = None
        filterValue = None

        if filterData:
            if isinstance(filterData, dict):
                if filterData.get("type", None):
                    filterKind = "type"
                    filterName = filterData[filterKind]
                    filterValue = filterName
                elif filterData.get("name", None):
                    filterKind = "name"
                    filterName = filterData[filterKind]
                    filterValue = filterName
                else:
                    filterKind = None
                    callbackKwargsValue = None
                    filterValue = filterName
            elif isinstance(filterData, str):
                if filterData.startswith("t#"):
                    filterKind = "type"
                    filterName = filterData[2:]
                    filterValue = filterName
                elif filterData.startswith("n#"):
                    filterKind = "name"
                    filterName = filterData[2:]
                    filterValue = filterName
                elif filterData.startswith("[") and filterData.endswith("]"):
                    filterKind = self._parseAttributeFilterSyntax(filterData)
                    attrFilterData = self._parseAttributeFilterData(filterData)
                    filterName = attrFilterData.get("filterParmName")
                    filterValue = attrFilterData.get("filterParmValue")
                else: # will be considered a plain name
                    filterKind = "name"
                    filterName = filterData
                    filterValue = filterName

            if filterKind:
                if filterKind == "type":
                    callbackKwargsValue = ["type", "name"]
                    callback = self._getAttr
                    callbackKwargs = {"methods":callbackKwargsValue}
                elif filterKind == "name":
                    callbackKwargsValue = ["name"]
                    callback = self._getAttr
                    callbackKwargs = {"methods":callbackKwargsValue}
                elif filterKind == "attr":
                    callbackKwargsValue = [("parm", "scale")]
                    filterFunction = self._getAttr
                    filterFunctionKwargs = {"methods":callbackKwargsValue}
                elif filterKind == "attrValue":
                    callbackKwargsValue = [("parm", filterName), "evalAsString"]
                    callback = self._getAttr
                    callbackKwargs = {"methods":callbackKwargsValue}

        if filterName.find("*") != -1:
            filterFunction = self._fnMatch
            filterFunctionKwargs = {"pattern":filterName, "callback":self._getAttr, "callbackKwargs":{"methods":callbackKwargsValue}}
            filterValue = True

        filterReturnData = {
            "filterName":filterName,
            "filterFunction":filterFunction,
            "filterFunctionKwargs":filterFunctionKwargs,
            "callback":callback,
            "callbackKwargs":callbackKwargs,
            "filterValue":filterValue,
        }

        return filterReturnData

    def addBack(self, filterData=None):
        """
        Add the previous set of elements on the stack to the current set, optionally filtered by a selector.
        """

        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._prevData:
            filteredData = self._filterData(data, **filterOptions)
            if filteredData:
                if filteredData not in self._data:
                    returnData.append(filteredData)

        combinedData = self._data + returnData

        return HouQuery(data=combinedData, prevData=self._data)
        

    def children(self, filterData=None):
        #print "\nfunc children"
        """
        Get the children of each element in the set of matched elements, optionally filtered by a selector.
        """

        returnData = []

        filterOptions = self._generateFilterOptions(filterData)
        print filterOptions

        for data in self._data:
            for child in data.children():
                filteredData = self._filterData(child, **filterOptions)
                if filteredData:
                    returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def filter(self, filterData=None):
        """
        Reduce the set of matched elements to those that match the selector or pass the function's test.
        """
        pass

        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            filteredData = self._filterData(data, **filterOptions)
            if filteredData:
                returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)


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

        return HouQuery(data=returnData, prevData=self._data)

    def parmContains(self, targetValue):
        #print "\nfunc parmContains"
        returnData = []
        for i in self._data:
            value = i.eval()
            if isinstance(value, str):
                if value.find(targetValue) != -1:
                    returnData.append(i)

        return HouQuery(data=returnData, prevData=self._data)

    #################
    # PARM STUFF
    #################

    def setAttr(self, parmName, parmValue):
        self._getAttrMultiple(self._data, **{"methods":
                [("parm", parmName), ("set", parmValue)]})
        return HouQuery(data=self._data)

    def replaceAttrValue(self, parmName, parmValue, parmTargetValue):
        for i in self._data:
            parmObject = self._getAttr(i, **{"methods":
                [("parm", parmName)]})
            parmObjectValue = parmObject.eval()
            if isinstance(parmObjectValue, str):
                newValue = parmObjectValue.replace(parmValue, parmTargetValue)
                parmObject.set(newValue)
            else:
                break
        return HouQuery(data=self._data)

    #################
    # BUNDLE STUFF
    #################

    def _checkBundle(self, value):
        """given the string value, checks if a bundle exists with the name"""
        bundles = hou.nodeBundles()
        bundleNames = [bundle.name() for bundle in bundles]

        if value in bundleNames:
            return True
        else: return False

    def addToBundle(self, bundleName):
        for data in self._data:
            filteredData = self._filterData(data, **{
                "callback":self._addNodeToBundle,
                "callbackKwargs":{"bundleName":bundleName},
                })

        return HouQuery(data=self._data)

    def removeFromBundle(self, bundleName):
        for data in self._data:
            filteredData = self._filterData(data, **{
                "callback":self._removeNodeFromBundle,
                "callbackKwargs":{"bundleName":bundleName},
                })

        return HouQuery(data=self._data)

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

    def _callAttr(self, **kwargs):
        self._getAttrMultiple(self._data, **{"methods":
                [kwargs["methodName"]]})
        return HouQuery(data=self._data)

    def _callAttrSingleValue(self, *args, **kwargs):
        self._getAttrMultiple(self._data, **{"methods":
                [(kwargs["methodName"], args[0])]})
        return HouQuery(data=self._data)

    @sq.methodName
    def setDisplayFlag(self, *args, **kwargs):
        return self._callAttrSingleValue(*args, **kwargs)

    @sq.methodName
    def setRenderFlag(self, *args, **kwargs):
        return self._callAttrSingleValue(*args, **kwargs)

    @sq.methodName
    def setSelected(self, *args, **kwargs):
        return self._callAttrSingleValue(*args, **kwargs)

    @sq.methodName
    def setUserData(self, *args, **kwargs):
        return self._callAttrSingleValue(*args, **kwargs)

    @sq.methodName
    def destroy(self, **kwargs):
        self._callAttr(**kwargs)

    ################################
    # Below are from the jQuery API
    ################################

    def add(self):
        """
        Create a new jQuery object with elements added to the set of matched elements.
        """
        pass

    def addAttr(self):
        """
        Adds the specified class(es) to each of the set of matched elements.
        """
        pass

    def after(self):
        """
        Insert content, specified by the parameter, after each element in the set of matched elements.
        """
        pass

    def attr(self):
        """
        Get the value of an attribute for the first element in the set of matched elements or set one or more attributes for every matched element.
        """
        pass

    def clone(self):
        """
        Create a deep copy of the set of matched elements.
        """
        pass

    def empty(self):
        """
        Remove all child nodes of the set of matched elements from the DOM.
        """
        pass

    def find(self):
        """!
        Get the descendants of each element in the current set of matched elements, filtered by a selector, jQuery object, or element.
        """
        pass

    def first(self):
        """
        Reduce the set of matched elements to the first in the set.
        """
        pass

    def has(self):
        """
        Reduce the set of matched elements to those that have a descendant that matches the selector or DOM element.
        """
        pass

    def hide(self):
        """!
        Hide the matched elements.
        """
        pass

    def _is(self):
        """
        Check the current matched set of elements against a selector, element, or jQuery object and return true 
        if at least one of these elements matches the given arguments
        """
        pass

    def next(self):
        """
        Get the immediately following sibling of each element in the set of matched elements. 
        If a selector is provided, it retrieves the next sibling only if it matches that selector.
        """
        pass

    def nextAll(self):
        """
        Get all following siblings of each element in the set of matched elements, optionally filtered by a selector.
        """
        pass

    def _not(self):
        """
        Remove elements from the set of matched elements.
        """
        pass

    def parent(self):
        """!
        Get the parent of each element in the current set of matched elements, optionally filtered by a selector.
        """
        pass

"""



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
"""