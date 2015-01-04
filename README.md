#sQuery (Scene Query)

##Summary
**sQuery** (short for SceneQuery) is a **Python** library for providing an easy interface for making Scene Queries and modifications in 3D Animation Applications. It is inspired by the ever popular Javascript Web Development Library **jQuery**. Currently only **Houdini** is supported **Maya** support is in works.

##Aims
- Provides intuitive and easy-to-use commands to make scene queries and modifications in 3d Applications.
- Help artists with minimal programming knowledge to perform rather complex operations.
- Help programmers to perform repetitive tasks easier.
- Create a platform that can provide a unified interface for similar operatations accross different applications.

##How to use it?
- **Warning:This is a work in progress and current API might break. Use only for testing purposes.**
Currently only Houdini version has useful functionality implemented. Maya version is implemented but functionality is lacking. 

- From the root folder of the library, import sQuery/sQuery.py
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
- Here are some of the **selector** commands you can run at this point:
```python
sq.children() # returns all the children nodes in the current context.
sq.children("obj") # returns all the children nodes in the current context with name obj
sq.children("*obj*") # returns all the children nodes with name that matches the given pattern in the brackets.
sq.children("t#geo") # returns all the children nodes with the type geo.
sq.children("t#*light*") # returns all the children nodes with the type that matches the given pattern.
sq.children("[scale]") # returns all the children nodes with the attribute 'scale'.
sq.children("[scale=1]") # returns all the children nodes with the attribute scale equal to 1.
#sQuery commands return an sQuery object.
```

- Here is an example to a more complex operation you can perform.
```python
sq.children("*geo*").filter("t#instanc*").children("t#alembic").replaceAttrValue("file_path", "v002", "v003")
.setUserData("is_altered", "true").addToBundle("alembics_inside_instances").setSelected(True)
"""
selects all the children in obj context that matches to the *geo* pattern, 
from the selection filters that are those whose type matches to the pattern *instanc*, 
chooses their alembic type children, replaces the v002 attribute on the alembic nodes file_path parameter with v003, 
creates a user data on them called "is_altered" with the value "true" 
and adds those alembics to the bundle "alembics_inside_instances" and sets them selected.
"""
```
##API
The full API is not yet documented but here is some of the commands that are available.
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

