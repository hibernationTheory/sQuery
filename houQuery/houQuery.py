import os
import sys

import hou

CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.insert(0, PARENT_DIR)

from sQueryCommon import sQueryCommon as sq
from lib.houdini.eyevex.takes import takes

reload(sq)
SQueryCommon = sq.SQueryCommon

class HouQuery(SQueryCommon):
    def __init__(self, initValue=None, data=[], prevData = []):
        SQueryCommon.__init__(self, data, initValue)
        self._data = data
        self._prevData = prevData
        self._printContent(self._data)

        if initValue:
            self._init(initValue)

    def _init(self, initValue):
        contexts = ["obj", "shop", "out"]
        msg = "sQuery is initialized in: "
        if isinstance(initValue, str) and initValue.lower() in contexts:
            self._data = [hou.node("/" + initValue)]
            print(msg + initValue.title() + " Context")
        elif isinstance(initValue, hou.Node):
            self._data = [initValue]
            print(msg + initValue.path())
        elif initValue == None:
            self._data = [hou.node("/obj")]
            print(msg + "Obj Context")

    def _printContent(self, content):
        divider = "*"*72
        print divider
        print "CURRENT SELECTION IS:"
        if content:
            print content
        else:
            print "EMPTY"
        print divider

    def get(self, index=None):
        """
        Retrieve the elements matched by the sQuery object.
        """
        if index != None:
            return self._data[index]
        return self._data

    def _parseAttributeFilterSyntax(self, filterData):
        if not filterData.startswith("[") and not filterData.endswith("]"):
            return None
        if filterData.count("=") > 1:
            print "This object doesn't handle parameter expressions that has more than 1 '='"
            return None
        if filterData.find("=") != -1:
            if filterData.find("~=") != -1:
                return "attrContains"
            if filterData.find("$=") != -1:
                return "attrEnds"
            if filterData.find("!=") != -1:
                return "attrNot"
            if filterData.find("^=") != -1:
                return "attrStarts"
            else:
                return "attrValue"
        else:
            return "attr"

    def _parseAttributeFilterData(self, filterData, filterKind):
        if not filterData.startswith("[") and not filterData.endswith("]"):
            return None
        if filterData.count("=") > 1:
            print "This object doesn't handle parameter expressions that has more than 1 '='"
            return None

        filterDataContent = filterData[1:-1]
        filterTypes = ["attrContains", "attrEnds", "attrNot", "attrStarts"]
        eqSignLoc = filterDataContent.find("=")

        filterParmName = ""
        filterParmValue = None

        if filterKind == "attrValue":
            filterParmName = filterDataContent[:eqSignLoc]
            filterParmValue = filterDataContent[eqSignLoc+1:]
        elif filterKind == "attr":
            filterParmName = filterDataContent
        elif filterKind in filterTypes:
            filterParmName = filterDataContent[:eqSignLoc-1]
            filterParmValue = filterDataContent[eqSignLoc+1:]

        return {"filterParmName":filterParmName, "filterParmValue":filterParmValue}

    def _generateFilterOptions(self, filterDataInput=None):
        """
        Generates the options that are going to be required by filtering operations based on given data
        """

        filterName = ""
        filterFunction = None
        filterFunctionKwargs = {}
        callback = None
        callbackKwargs = {}
        filterKind = None
        filterValue = None
        postFilterFunction = None
        postFilterFunctionKwargs = {}
        filters = []

        filterReturnData = {
            "filterName":filterName,
            "filterFunction":filterFunction,
            "filterFunctionKwargs":filterFunctionKwargs,
            "postFilterFunction":postFilterFunction,
            "postFilterFunctionKwargs":postFilterFunctionKwargs,
            "callback":callback,
            "callbackKwargs":callbackKwargs,
            "filterValue":filterValue,
        }

        if filterDataInput == None:
            filters.append(filterReturnData)
            return filters

        if filterDataInput and isinstance(filterDataInput, str):
            filterDataInput = filterDataInput.split(" ")
            for filterData in filterDataInput:
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
                    attrFilterData = self._parseAttributeFilterData(filterData, filterKind)
                    filterName = attrFilterData.get("filterParmName")
                    filterValue = attrFilterData.get("filterParmValue")
                else: # will be considered a plain name
                    filterKind = "name"
                    filterName = filterData
                    filterValue = filterName

                if filterKind:
                    if filterKind == "type":
                        filterFunction = self._getAttr
                        filterFunctionKwargs = {"methods":["type", "name"]}
                    elif filterKind == "name":
                        filterFunctionKwargs = {"methods":["name"]}
                        filterFunction = self._getAttr
                    #attribute related filters
                    elif filterKind == "attr":
                        filterFunction = self._getAttr
                        filterFunctionKwargs =  {"methods":[{"name":"parm", "args":filterName}]}
                    elif filterKind == "attrValue":
                        targetValue = filterValue
                        filterValue = None
                        filterFunction = self._attrIs
                        filterFunctionKwargs = {"methods":[{"name":"parm", "args":filterName}, {"name":"evalAsString"}], "targetValue":targetValue, "targetParm":filterName}
                    elif filterKind == "attrContains":
                        targetValue = filterValue
                        filterValue = None
                        filterFunction = self._attrContains
                        filterFunctionKwargs = {"methods":[{"name":"parm", "args":filterName}, {"name":"evalAsString"}], "targetValue":targetValue, "targetParm":filterName}
                    elif filterKind == "attrStarts":
                        targetValue = filterValue
                        filterValue = None
                        filterFunction = self._attrStarts
                        filterFunctionKwargs = {"methods":[{"name":"parm", "args":filterName}, {"name":"evalAsString"}], "targetValue":targetValue, "targetParm":filterName}
                    elif filterKind == "attrEnds":
                        targetValue = filterValue
                        filterValue = None
                        filterFunction = self._attrEnds
                        filterFunctionKwargs = {"methods":[{"name":"parm", "args":filterName}, {"name":"evalAsString"}], "targetValue":targetValue, "targetParm":filterName}
                    elif filterKind == "attrNot":
                        targetValue = filterValue
                        filterValue = None
                        filterFunction = self._attrNot
                        filterFunctionKwargs = {"methods":[{"name":"parm", "args":filterName}, {"name":"evalAsString"}], "targetValue":targetValue, "targetParm":filterName}

                if filterKind =="name" or filterKind =="type":
                    if filterName.find("*") != -1:
                        postFilterFunction = self._fnMatch
                        postFilterFunctionKwargs = {"pattern":filterName}
                        filterValue = True

                filterReturnData = {
                    "filterName":filterName,
                    "filterFunction":filterFunction,
                    "filterFunctionKwargs":filterFunctionKwargs,
                    "postFilterFunction":postFilterFunction,
                    "postFilterFunctionKwargs":postFilterFunctionKwargs,
                    "callback":callback,
                    "callbackKwargs":callbackKwargs,
                    "filterValue":filterValue,
                }

                filters.append(filterReturnData)

        return filters

    def addBack(self, filterData=None):
        """
        Add the previous set of elements on the stack to the current set, optionally filtered by a selector.
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._prevData:
            filteredData = self._filterDataMultiple(data, filterOptions)
            if filteredData:
                if filteredData not in self._data:
                    returnData.append(filteredData)

        combinedData = self._data + returnData

        return HouQuery(data=combinedData, prevData=self._data)

    def remove(self, filterData=None):
        """
        Remove elements from set of matched elements
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            filteredData = self._filterDataMultiple(data, filterOptions)
            if not filteredData:
                returnData.append(data)

        return HouQuery(data=returnData, prevData=self._data)


    def children(self, filterData=None):
        """
        Get the children of each element in the set of matched elements, optionally filtered by a selector.
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)
        print filterOptions

        for data in self._data:
            for child in data.children():
                filteredData = self._filterDataMultiple(child, filterOptions)
                if filteredData:
                    returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def hasChildren(self, filterData=None):
        """
        Reduce the set of matched elements to those that have a direct descendant that matches the selector.
        """ # or DOM element
        returnData = set()

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            for child in data.children():
                filteredData = self._filterDataMultiple(child, filterOptions)
                if filteredData:
                    returnData.add(data)

        return HouQuery(data=list(returnData), prevData=self._data)

    def hasSubChildren(self, filterData=None):
        """
        Reduce the set of matched elements to those that have a descendant that matches the selector.
        """ # or DOM element
        returnData = set()

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            for child in data.allSubChildren():
                filteredData = self._filterDataMultiple(child, filterOptions)
                if filteredData:
                    returnData.add(data)

        return HouQuery(data=list(returnData), prevData=self._data)

    def find(self, filterData=None):
        """
        Get the all the children (including sub) of each element in the set of matched elements, 
        optionally filtered by a selector.
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            for child in data.allSubChildren():
                filteredData = self._filterDataMultiple(child, filterOptions)
                if filteredData:
                    returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def filter(self, filterData=None):
        """
        Reduce the set of matched elements to those that match the selector.
        """
        # documentation continues: or pass the function's test.

        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            filteredData = self._filterDataMultiple(data, filterOptions)
            if filteredData:
                returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def prev(self, filterData=None, index=0):
        """
        Get the immediately prior sibling of each element in the set of matched elements. 
        If a selector is provided, it retrieves the prior sibling only if it matches that selector.
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            connection = self._connection(data, **{"index":index, "mode":"inputs"})
            if connection:
                filteredData = self._filterDataMultiple(connection, filterOptions)
                if filteredData:
                    returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def next(self, filterData=None, index=0):
        """
        Get the immediately following sibling of each element in the set of matched elements. 
        If a selector is provided, it retrieves the next sibling only if it matches that selector.
        """
        returnData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            connection = self._connection(data, **{"index":index, "mode":"outputs"})
            if connection:
                filteredData = self._filterDataMultiple(connection, filterOptions)
                if filteredData:
                    returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def parent(self, filterData=None):
        """
        Get the parent of each element in the current set of matched elements, optionally filtered by a selector.
        """
        returnData = []
        pathData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            parent = data.parent()
            filteredData = self._filterDataMultiple(parent, filterOptions)
            if filteredData and filteredData.path() not in pathData: 
            #! do I need to perform this check for other methods as well to prevent data duplication? 
                returnData.append(filteredData)
                pathData.append(filteredData.path())

        return HouQuery(data=returnData, prevData=self._data)

    def siblings(self, filterData=None):
        """
        Get the siblings of each element in the set of matched elements, optionally filtered by a selector.
        """
        returnData = []
        pathData = []

        filterOptions = self._generateFilterOptions(filterData)

        for data in self._data:
            parent = data.parent()
            siblings = parent.children()
            for sibling in siblings:
                filteredData = self._filterDataMultiple(sibling, filterOptions)
                if filteredData and filteredData.path() not in pathData: 
                    #! do I need to perform this check for other methods as well to prevent data duplication? 
                    returnData.append(filteredData)
                    pathData.append(filteredData.path())

        return HouQuery(data=returnData, prevData=self._data)

    def selection(self):
        """
        EXPERIMENTAL - Get the current selection
        """
        returnData = [i for i in hou.selectedNodes()]
        return HouQuery(data=returnData, prevData=self._data)

    def bundle(self, bundleName):
        """
        EXPERIMENTAL - Get the contents of the given bundle.
        """
        returnData = self._returnBundleContent(bundleName)
        return HouQuery(data=returnData, prevData=self._data)

    def _connection(self, node, **kwargs):
        """
        Given the node gets the previous or next connected node (at the given index)
        """
        mode = kwargs.get("mode", None)
        if not mode:
            return None
        index = kwargs.get("index", 0)
        result = None

        connections = self._getAttr(node, **{"methods":[mode]})
        if connections and index < len(connections):
            result = connections[index]
        return result


    #################
    # ATTRIBUTE FILTERS
    #################

    def _attrContains(self, givenValue, **kwargs):
        targetValue = kwargs["targetValue"]
        targetParm = kwargs["targetParm"]

        parmValue = self._getAttr(givenValue, **kwargs)
        if parmValue != None:
            if parmValue.find(targetValue) != -1:
                return True
        return False

    def _attrStarts(self, givenValue, **kwargs):
        targetValue = kwargs["targetValue"]
        targetParm = kwargs["targetParm"]

        parmValue = self._getAttr(givenValue, **kwargs)
        if parmValue != None:
            if parmValue.startswith(targetValue):
                return True
        return False

    def _attrEnds(self, givenValue, **kwargs):
        targetValue = kwargs["targetValue"]
        targetParm = kwargs["targetParm"]

        parmValue = self._getAttr(givenValue, **kwargs)
        if parmValue != None:
            if parmValue.endswith(targetValue):
                return True
        return False

    def _attrNot(self, givenValue, **kwargs):
        targetValue = kwargs["targetValue"]
        targetParm = kwargs["targetParm"]

        parmValue = self._getAttr(givenValue, **kwargs)
        if parmValue != None:
            if parmValue != targetValue:
                return True
        return False

    def _attrIs(self, givenValue, **kwargs):
        targetValue = kwargs["targetValue"]
        targetParm = kwargs["targetParm"]

        parmValue = self._getAttr(givenValue, **kwargs)
        if parmValue != None:
            if parmValue == targetValue:
                return True
        return False

    #################
    # PARM STUFF
    #################

    def toggle(self, parmName):
        """
        Given a parameter, toggle method sets it to 0 if it is 1 or vice versa
        """
        for i in self._data:
            parmCurrentValue = self._getAttr(i, **{"methods":[
                     {"name":"parm", "args":parmName},
                     {"name":"eval"}
                     ]})
            if parmCurrentValue == False:
                parmValue = True
            elif parmCurrentValue == True:
                parmValue = False
            self._getAttr(i, **{"methods":[
                     {"name":"parm", "args":parmName}, 
                     {"name":"set", "args":parmValue}
                    ]})
        return HouQuery(data=self._data)

    def setAttr(self, parmName, parmValue, force=False):
        """
        Given a parameter and a value, setAttr sets the given parameter to given value
        """
        if force: #! need to implement a proper force method that would override
            # locked, parameter referenced, keyframed, etc.. parms.
            take = takes.curTake()
        for i in self._data:
            if force: #! temp implementation
                take.addParm(i.parm(parmName))
            self._getAttr(i, **{"methods":[
                     {"name":"parm", "args":parmName}, 
                     {"name":"set", "args":parmValue}
                    ]})
        return HouQuery(data=self._data)

    def replaceAttrValue(self, parmName, parmValue, parmTargetValue):
        """
        Given a parameter and a value to change and a value to change to, 
        replaceAttrValue sets the given value in the given parameter to value to change to
        """
        for i in self._data:
            parmObject = self._getAttr(i, **{"methods":[
                {"name":"parm", "args":parmName}
                ]})
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

    def _returnBundleContent(self, value):
        """given the string value, returns the contents of the bundle with the corresponding name"""
        targetBundle = hou.nodeBundle(value)
        if targetBundle:
            nodes = targetBundle.nodes()
            return nodes
        else:
            return []

    def addToBundle(self, bundleName):
        for data in self._data:
            filteredData = self._filterDataMultiple(data, **{
                "callback":self._addNodeToBundle,
                "callbackKwargs":{"bundleName":bundleName},
                })

        return HouQuery(data=self._data)

    def removeFromBundle(self, bundleName):
        for data in self._data:
            filteredData = self._filterDataMultiple(data, **{
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

    def select(self):
        """
        Convenience method for the setSelected(True)
        """
        self.setSelected(True)

    def deselect(self):
        """
        Convenience method for the setSelected(False)
        """
        self.setSelected(False)

    def show(self):
        """
        Convenience method for setDisplayFlag(True)
        """
        self.setDisplayFlag(True)

    def hide(self):
        """
        Convenience method for setDisplayFlag(False)
        """
        self.setDisplayFlag(False)

    def _callAttrWithMethodName(self, *args, **kwargs):
        # deleting the _sQueryMethodName that comes from the decorator
        # to have it not passed to underlying Hou objects
        methodName = kwargs.get("_sQueryMethodName")
        del kwargs["_sQueryMethodName"]

        self._getAttrMultiple(self._data, **{"methods":
                [{"name":methodName, "args":args, "kwargs":kwargs}]})
        return HouQuery(data=self._data)

    @sq.methodName
    def allowEditingOfContents(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def setName(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def setDisplayFlag(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def setRenderFlag(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def setSelected(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def setUserData(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def destroyUserData(self, *args, **kwargs):
        return self._callAttrWithMethodName(*args, **kwargs)

    @sq.methodName
    def destroy(self, *args, **kwargs):
        self._callAttrWithMethodName(*args, **kwargs)
        return HouQuery(data=None)

    #################
    # NODE CREATION / DELETION
    #################

    def createNodeInside(self, typeName, nodeParms=None):

        returnData = []
        for i in self._data:
            filteredData = self._filterDataMultiple(i, **{
            "callback":self._createNodeInsideParent,
            "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
            })
            if filteredData:
                returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def createNodeAfter(self, typeName, nodeParms=None):

        returnData = []
        for i in self._data:
            filteredData = self._filterDataMultiple(i, **{
                "callback":self._createNodeAfterGivenNode,
                "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
                })
            if filteredData:
                returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

    def createNodeBefore(self, typeName, nodeParms=None):

        returnData = []
        for i in self._data:
            filteredData = self._filterDataMultiple(i, **{
                "callback":self._createNodeBeforeGivenNode,
                "callbackKwargs":{"typeName":typeName, "parms":nodeParms},
                })
            if filteredData:
                returnData.append(filteredData)

        return HouQuery(data=returnData, prevData=self._data)

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

    ################################
    # Misc
    ################################

    ################################
    # Below are from the jQuery API
    ################################

    def _add(self):
        """
        NOT YET IMPLEMENTED - Create a new jQuery object with elements added to the set of matched elements.
        """
        pass

    def _addAttr(self):
        """
        NOT YET IMPLEMENTED - Adds the specified class(es) to each of the set of matched elements.
        """
        pass

    def _after(self):
        """
        NOT YET IMPLEMENTED - Insert content, specified by the parameter, after each element in the set of matched elements.
        """
        pass

    def _attr(self):
        """
        NOT YET IMPLEMENTED - Get the value of an attribute for the first element in the set of matched elements or set one or more attributes for every matched element.
        """
        pass

    def _clone(self):
        """
        NOT YET IMPLEMENTED - Create a deep copy of the set of matched elements.
        """
        pass

    def _empty(self):
        """
        NOT YET IMPLEMENTED - Remove all child nodes of the set of matched elements from the DOM.
        """
        pass

    def _first(self):
        """
        NOT YET IMPLEMENTED - Reduce the set of matched elements to the first in the set.
        """
        pass

    def _has(self):
        """
        Reduce the set of matched elements to those that have a descendant that matches the selector or DOM element.
        """
        pass

    def _hide(self):
        """
        NOT YET IMPLEMENTED - Hide the matched elements.
        """
        pass

    def _is(self):
        """
        NOT YET IMPLEMENTED - Check the current matched set of elements against a selector, element, or jQuery object and return true 
        if at least one of these elements matches the given arguments
        """
        pass

    def _nextAll(self):
        """
        NOT YET IMPLEMENTED - Get all following siblings of each element in the set of matched elements, optionally filtered by a selector.
        """
        pass