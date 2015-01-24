#sQuery (Scene Query)

##Summary
**sQuery** (short for SceneQuery) is a **Python** library that provides an easy interface for making scene queries and modifications in 3D Animation Applications. It is inspired by the popular Javascript Web Development Library **jQuery**. Currently **Houdini** version is in development, **Maya** support is planned.

##Aims
- Provide intuitive and easy-to-use commands to make scene queries and modifications in 3d Applications.
- Help artists with minimal programming knowledge to perform rather complex operations.
- Help programmers to perform repetitive tasks easier.
- Create a platform that can provide a unified interface for similar operations across different applications.

##How to use it?
- **Warning:This is a work in progress and current API might break. Use only for testing purposes.**
Currently only Houdini version has useful functionality implemented. Maya version is implemented but functionality is lacking. 

- Launch the Houdini Shell, from the root folder of the sQuery library, import sQuery/sQuery.py
```python
from sQuery import sQuery
```
- initialize an sQuery object. It would be initialized for the "obj" context by default. 
```python
sq = sQuery.sQuery()
```
- if you wanted to initialize for a different context, like shop. you could do:
```python
sq = sQuery.sQuery("shop")
# or you can pass a houdini object
sq = sQuery.sQuery(hou.node("/shop"))
```
- Using sQuery, you will be using **selector** commands alongside with selection methods to perform and refine searches. (Each call to the sQuery object returns an sQuery object that contains the result of performed operations):

```python
sq.children() # gets all the children nodes in the current context.
sq.children("obj1") # gets all the children nodes in the current context with name obj1 (would be only one, since names are unique)
sq.children("*obj*") # gets all the children nodes with name that matches the given pattern in the brackets.
sq.children("t#geo") # gets all the children nodes with the 'type' geo.
sq.children("t#*light*") # gets all the children nodes with the type that matches the given pattern.
sq.children("[scale]") # gets all the children nodes with the attribute 'scale'.
sq.children("[scale=1]") # gets all the children nodes with the attribute scale equal to 1.
sq.children("[shop_materialpath~=constant]") # gets all the children nodes with the attribute shop_materialpath containing the word constant.
sq.children("[shop_materialpath$=constant]") # gets all the children nodes with the attribute shop_materialpath ends with the word constant.
sq.children("[shop_materialpath^=constant]") # gets all the children nodes with the attribute shop_materialpath starts with the word constant.
sq.children("[shop_materialpath!=constant]") # gets all the children nodes with the attribute shop_materialpath doesn't contain the word constant

# you can also do multiple selections by leaving a space in between selectors

sq.children("t#geo t#*light*") 
#get all children that are of type geo or those with type matching to *light*

```

- Here is an example to a more complex operation you can perform using various methods of the API.
```python
sq.children("*geo*").remove("*HOUSE*).filter("t#instanc*").children("t#alembic").replaceAttrValue("file_path", "v002", "v003")
.setUserData("is_altered", "true").addToBundle("alembics_inside_instances").next("t#switch").createNodeAfter("delete", {"group":"*_arms_"}).toggle("affectnumber").setSelected(True)
"""
selects all the children in obj context with name that matches to the *geo* pattern, from that selection removes those that have the word *HOUSE* in it, from that selection filters those whose type matches to the *instanc* pattern, 
chooses the alembic type children of the result, replaces the v002 attribute on the alembic nodes file_path parameter with v003, creates a user data on them called "is_altered" with the value "true" and adds those alembics to the bundle "alembics_inside_instances" and selects the next node if it is of type switch and creates a delete node after them with the 'group' parameter set to '*_arms_*', toggles the affect number parameter on this delete nodes (meaning if it is on, makes it off or vice versa) and then selects this 'delete' node that was created.
"""
```
##API
The full API is not yet documented but here are some of the commands that are currently available.

###Selectors
These are some of the selectors that you can use inside selection methods.
- "foo" : selects by name where it is "foo"
- "\*foo\*" : selects by name where it matches to the pattern \*foo\*
- "t#foo" : selects by type name where it is "foo"
- "t#\*foo\*" : selects by type name where it matches to the pattern "\*foo\*"
- "[foo]" : selects by attribute name where attribute "foo" exists
- "[foo=bar]" : selects by attribute name where attribute "foo" is equal to "bar"
- "[foo!=bar]" : selects by attribute name where attribute "foo" is not equal to "bar"
- "[foo~=bar]" : selects by attribute name where attribute "foo" has the word "bar" in it
- "[foo^=bar]" : selects by attribute name where attribute "foo" starts with the word "bar"
- "[foo$=bar]" : selects by attribute name where attribute "foo" ends with the word "bar"

###Selection Methods
These are the methods that you can use to perform various operations optionally using the selectors above as arguments
- addBack
- remove
- children
- find
- filter
- prev
- next
- parent
- siblings
- hasChildren
- hasSubChildren

###Selection Methods that don't work with selectors
- selection
- bundle

###Attribute Related Methods
- setAttr
- replaceAttrValue
- toggle

###Supported Houdini Native Methods
- allowEditingOfContents
- cook
- coolapseIntoSubnet
- destroy
- destroyUserData
- matchCurrentDefinition
- move
- setColor
- setDisplayFlag
- setLayout
- setName
- setPosition
- setRenderFlag
- setSelected
- setUserData

###Other Scene Operations
- addToBundle
- removeFromBundle
- createNodeInside
- createNodeAfter
- createNodeBefore

###Operations on the sQuery object
- get
- each

###Known Issues
- seems like [attr!=value] is not working as expected
- Setting expressions using setAttr is problematic
- setAttr is not tested on locked, keyframed, etc... attributes.
