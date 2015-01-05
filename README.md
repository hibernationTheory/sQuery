#sQuery (Scene Query)

##Summary
**sQuery** (short for SceneQuery) is a **Python** library that provides an easy interface for making scene queries and modifications in 3D Animation Applications. It is inspired by the popular Javascript Web Development Library **jQuery**. Currently only **Houdini** is supported, **Maya** support is in works.

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
- to initialize it for a different context, provide the context name inside the brackets.
```python
sq = sQuery.sQuery("shop")
```
- Here are some of the **selector** commands you can run at this point (Each call to the sQuery object returns an sQuery object that contains the result of performed operations):

```python
sq.children() # gets all the children nodes in the current context.
sq.children("obj") # gets all the children nodes in the current context with name obj
sq.children("*obj*") # gets all the children nodes with name that matches the given pattern in the brackets.
sq.children("t#geo") # gets all the children nodes with the type geo.
sq.children("t#*light*") # gets all the children nodes with the type that matches the given pattern.
sq.children("[scale]") # gets all the children nodes with the attribute 'scale'.
sq.children("[scale=1]") # gets all the children nodes with the attribute scale equal to 1.
```

- Here is an example to a more complex operation you can perform.
```python
sq.children("*geo*").filter("t#instanc*").children("t#alembic").replaceAttrValue("file_path", "v002", "v003")
.setUserData("is_altered", "true").addToBundle("alembics_inside_instances").createNodeAfter("delete", {"group":"*_arms_"}).setSelected(True)
"""
selects all the children in obj context with name that matches to the *geo* pattern, 
from the selection filters that are those whose type matches to the pattern *instanc* pattern, 
chooses the alembic type children of the result, replaces the v002 attribute on the alembic nodes file_path parameter with v003, 
creates a user data on them called "is_altered" with the value "true" 
and adds those alembics to the bundle "alembics_inside_instances" and creates a delete node after them with the 'group' parameter set to '*_arms_*' and selects this 'delete' node that was created.
"""
```
##API
The full API is not yet documented but here are some of the commands that are currently available.

- addBack
- children
- filter
- setAttr
- replaceAttrValue
- addToBundle
- removeFromBundle
- setName
- setDisplayFlag
- setRenderFlag
- setSelected
- setUserData
- destroyUserData
- destroy
- createNodeInside
- createNodeAfter
- createNodeBefore

