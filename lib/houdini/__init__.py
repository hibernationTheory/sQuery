# ==============================================================================
#           takes - pythonic acces to houdini takes via a wrapper
#
# mimics the anticipated behavior of the SideFX implentation best as possible
#  ----------------------------------------------------------------------------
# ver 0.1.0
# dowloaded from eyevex.com
# dan@dansportfolio.com
#
# ---------------------------- known issues -----------------------------------
#
# Unable to implent the XML export as the format can be aritrary
# It is impossible to know is the path would be returned in the presented format
#     It was needed for this implementation but may not be compatable
# It is not clear if insertTakeAbove and moveUnderTake will be returning parent
#    or child. I assume it to be child.
# EYEVEX_TAKE_PREFIX is a hscript env used to store the take prefix
#    when abscent value is assumed to be 'take' -done for retrieval ability
# asCode doesn't include the code for wrapping the take. Need to deal with
#    incremented names first.
# ==============================================================================


import hou
import sys

class TakeWrapper():
	
	def __init__(self,name): 
		self._name = name

	def __repr__(self):
		
		represnt = '<' + str(self.__class__) + ' ' +self._name+ ' at ' + self._solveFullPath() +'>'
		#represnt = '<hou_Take ' +self._name+ ' at ' + self._solveFullPath() +'>'
		return represnt

	def setName(self, name):
		
		'''Set this Takes name.'''

		# check if name is a duplicate
		# check for none and inc 1 from highest
		if name != self._name:
			
			hscript_cmd = 'takename ' + self._name + ' ' + name
			hscript_cmd_results = hou.hscript(hscript_cmd)
		
			if _takeErr(hscript_cmd_results[1]):
				result = None
			else:
				self._name = name
				result = name
		else:
			result = name
		
		return result

	def memoryUsageInBytes(self):
		
		'''Memory used by this Take in bytes'''
		
		hscript_cmd = 'takels -m ' + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = None
			
		# isolate the number portion as an interger
		else: result = int(hscript_cmd_results[0].split()[1].split('(')[1])

		return result

	def _solveFullPath(self):

		hscript_cmd = 'takels'
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		# test for errors
		if _takeErr(hscript_cmd_results[1]):
			return None
			
		# list of heirarchillly indented takes 
		indented_takes = hscript_cmd_results[0].split('\n')
		if indented_takes[-1]=='':
			del(indented_takes[-1])

		# main loop
		name_found    = False
		path_elements = []
		levels_deep   = None
		
		for i in range(len(indented_takes)):
			
			# work our way back from the end
			idx = (i+1)*-1
			
			# find the leaf path element
			path_element = indented_takes[idx].lstrip()
			if self._name == path_element:

				name_found = True
				path_elements.insert(0,path_element)
				levels_deep = indented_takes[idx].count(' ')
				continue
			
			# leaf node unfound we keep looking
			elif name_found == False:
				continue

			# skip over siblings and children
			elif levels_deep <= indented_takes[idx].count(' '):
				continue

			else:
				# found the parent
				path_elements.insert(0,path_element)
				levels_deep = indented_takes[idx].count(' ')

		# list is empty -- notify before leaving
		if len(path_elements)==0:
			take_error =_takeErr('There is no take named: '+ self._name)
			result = None
			
		else:
			# join and return the path
			take_path = '/' + '/'.join(path_elements)
			result = take_path

		return result

	def fullPath(self):
		
		'''Retrun the full path to this Take.'''
		
		return self._solveFullPath()
	
	def name(self):
		
		'''Return the name of this take'''
		
		return self._name
		
	def destroy(self, recursive=False):
		
		'''Destroy this Take.'''
		
		recursive_flag = ''
		if recursive == True:
			recursive_flag = '-R '
		
		hscript_cmd = 'takerm ' + recursive_flag + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None
		
		return result

	#------------------------------------
	#  I/O
	#------------------------------------
	def asCode(self):
	
		'''Returns the commands necessary to re-create this take.'''

		hscript_cmd = 'takescript ' + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else:
			recreate_hscript = hscript_cmd_results[0]

			#recreate_cmd = 'hou.hscript(\'\'\'' +recreate_hscript+ '\'\'\')'
			
			recreate_cmd = 'hou.hscript(\'\'\'' +recreate_hscript+ '\'\'\')'


			result = recreate_cmd
			
			return result
			

	def saveToFile(self, filename, recursive=False):
		
		'''Save child or children of this take to specified filename'''
		
		recursive_flag = ''
		if recursive == True:
			recursive_flag = ' -R '

		hscript_cmd = 'takesave -o ' + filename + recursive_flag + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None
		
		return result
		
		
	def loadChildTakeFromFile(self, filename):
		
		'''Load Take from the specified filename as a child of this Take''' 
		
		hscript_cmd = 'takeload -p ' + self._name + ' ' + filename
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None

		return result

	#------------------------------------
	#  child dealing methods
	#------------------------------------
	
	def addChildTake(self, name=''):
		
		'''Add a child Take under this Take'''
		
		hscript_cmd = 'takeadd -v -p ' + self._name + ' ' +  name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = None
		else: 
			name = hscript_cmd_results[0].rstrip()
			result = TakeWrapper(name)

		return result


	def children(self):
		
		'''Returns a tuple of Takes that are children of this Take.'''
		
		hscript_cmd = 'takels -i -p ' + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = None
		else: 
			take_names = hscript_cmd_results[0].split()
			result = tuple([TakeWrapper(take_name) for take_name in take_names ])

		return result

		
	#------------------------------------
	#   parm dealing methods
	#------------------------------------

	def _addRemoveParm(self, parm, add=True): ## does this expect a parm name obk or path?!
	
		node_path = parm.node().path()
		cur_take = curTake()
		cur_update_mode = hou.updateModeSetting()
		hou.setUpdateMode(hou.updateMode.Manual)
		setCurTake(self)
		
		remove_flag = ''
		if add != True:
			remove_flag = '-u '
		
		hscript_cmd = 'takeinclude ' + remove_flag + node_path + ' ' + parm.name()
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if  _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None

		setCurTake(cur_take)
		hou.setUpdateMode(cur_update_mode)
		
		return result


	def addParm(self, parm):
		
		'''Include the specified parm in this Take'''
		
		self._addRemoveParm(parm, add=True)
		return None
		
	def removeParm(self, parm):
		
		'''Remove the specified parm is from this take.'''

		
		self._addRemoveParm(parm, add=False)
		return None
		
	def hasParm(self, parm):
		
		'''Test if the specified parm is included in this take.'''
		
		result = False
		all_parms = self.parms()
		
		for all_parm in all_parms:
			
			if all_parm == parm:
				result = True
				break
			else:
				continue
			
		return result
		
	
	def parms(self):
		
		'''returns a tuple of hou.parms'''
		hscript_cmd = 'takels  -i -l ' + self._name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = None
		else: 
			parm_names_paths = hscript_cmd_results[0].split('\n')
			parm_names_paths = [x for x in parm_names_paths if x!='']
			parm_names_paths.remove(self._name)

			# make parm objects
			parms = []
			for parm_names_path in parm_names_paths:
				
				node_path = parm_names_path.split(' ',1)[0]
				parm_names = parm_names_path.split(' ',1)[1].split()
				
				for parm_name in parm_names:
					if '-flag' in parm_name:
						continue
					
					parm = hou.parm(node_path + '/' + parm_name)
					
					if parm == None:
						parm = hou.parmTuple(node_path + '/' + parm_name)
						if parm == None:
							msg = "unable to resolve parm object for: "+node_path + '/' + parm_name
							print >> sys.stderr, msg
							continue
						
						else: [parms.append(i) for i in parm]

					else: parms.append(parm)

			if len(parms) == 0:
				result = None
			else: result = tuple(parms)

		return result


	def removeAllParmsOfNode(self, node):
		
		'''Remove all parameters from specified Node from this Take'''

		all_parms = self.parms()
		for parm in all_parms:
			if parm.node() == node:
				self._addRemoveParm(parm, add=False)
				

	def addAllParmsOfNode(self, node):
		
		'''Include all parameters from specified Node in this Take'''
		
		node_path = node.path()
		cur_take = curTake()
		cur_update_mode = hou.updateModeSetting()
		hou.setUpdateMode(hou.updateMode.Manual)
		setCurTake(self)

		hscript_cmd = 'takeinclude ' + node_path + ' *'
		hscript_cmd_results = hou.hscript(hscript_cmd)

		if  _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None

		setCurTake(cur_take)
		hou.setUpdateMode(cur_update_mode)
		
		return result
		
		
	def addParmsFromTake(self, take, overwrite_existing=True):
		
		'''Include parameters from the specified Take in this Take.'''
		
		cur_take = curTake()
		cur_update_mode = hou.updateModeSetting()
		hou.setUpdateMode(hou.updateMode.Manual)
		setCurTake(self)
		
		force_flag = ''
		if overwrite_existing == True:
			force_flag = '-f '
			
		source = take.name()
			
		hscript_cmd = 'takemerge ' + force_flag + ' ' + self._name +  ' ' + source
		hscript_cmd_results = hou.hscript(hscript_cmd)
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else:
			result = None
			
		setCurTake(cur_take)
		hou.setUpdateMode(cur_update_mode)
		
		return result


	#------------------------------------
	#   including/discluding node flags
	#------------------------------------
		
	def _addRemoveFlag(self, node,flag, add=True):
		
		cur_take = curTake()
		cur_update_mode = hou.updateModeSetting()
		hou.setUpdateMode(hou.updateMode.Manual)
		setCurTake(self)
		
		remove_flag = ''
		if add != True:
			remove_flag = '-u '
		
		hscript_cmd = 'takeinclude ' + remove_flag + '-' + flag +  ' ' + node.path()
		hscript_cmd_results = hou.hscript(hscript_cmd)
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else:
			result = None
			
		setCurTake(cur_take)
		hou.setUpdateMode(cur_update_mode)
		
		return result
		
		
	def addNodeBypassFlag(self, node):
		
		'''Include the specified node's bypass flag in this Take.'''

		result = self._addRemoveFlag( node,'b', add=True)
		return result
		
	def addNodeDisplayFlag(self, node):
		
		'''Include the specified node's display flag in this Take.'''
	
		result = self._addRemoveFlag( node,'d', add=True)
		return result
		
	def addNodeRenderFlag(self, node):
		
		'''Include the specified node's render flag in this Take.'''
	
		result = self._addRemoveFlag( node,'r', add=True)
		return result

	def removeNodeBypassFlag(self, node):
		
		'''Remove the specified node's bypass flag from this Take.'''
	
		result = self._addRemoveFlag( node,'b', add=False)
		return result

	def removeNodeDisplayFlag(self, node):
		
		'''Remove the specified node's display flag from this Take.'''
	
		result = self._addRemoveFlag( node,'d', add=False)
		return result

	def removeNodeRenderFlag(self, node):
		
		'''Remove the specified node's render flag from this Take.'''
	
		result = self._addRemoveFlag( node,'r', add=False)
		return result

	#------------------------------------
	#   positioning methods
	#------------------------------------
	
	def moveUnderTake(self, take):
	
		'''Moves take and all its children under pecified parent Take.'''
		
		take_name = take.name()
		
		hscript_cmd = 'takemove ' + self._name +' '+ take_name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else: result = None
		
		return result
		
		
	def insertTakeAbove(self, name=''):
	
		'''Insert the take between the specified Take and its parent.
		   (becomes the new parent of the child takes)'''
		
		parent_name = self._solveFullPath().split('/')[-2]
	
		hscript_cmd = 'takeadd -i -v -p ' + parent_name +' '+ name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		
		if _takeErr(hscript_cmd_results[1]):
			result = hscript_cmd_results[1]
		else:
			name = hscript_cmd_results[0].rstrip()
			result = TakeWrapper(name)
		
		return result

	
class Take(TakeWrapper):

	def __init__(self,name=''): 

		hscript_cmd = 'takeadd -v ' + name
		hscript_cmd_results = hou.hscript(hscript_cmd)
		if _takeErr(hscript_cmd_results[1]):
			return None
		name = hscript_cmd_results[0].rstrip()
			
		self._name = name
		self.setName(name)


# ============================================================================

def _takeErr(cmd_err_output):
	
	if cmd_err_output != '':
		
		print >> sys.stderr, "TAKE ERROR: " + cmd_err_output
		result = cmd_err_output
	else:
		result = False

	return result


def allTakes():
	
	'''returns a tuple of all Take objects'''

	hscript_cmd = 'takels -i'
	hscript_cmd_results = hou.hscript(hscript_cmd)
	
	if _takeErr(hscript_cmd_results[1]):
		result = None
	else: 
		take_names = hscript_cmd_results[0].split('\n')
		if take_names[-1]=='':del(take_names[-1])
		
		takes = [ TakeWrapper(i) for i in take_names ]
		result = tuple(takes)
		
	return result
	
	
def curTake():
	
	'''returns the current Take object'''
	
	current_take_name = hou.expandString("$ACTIVETAKE")
	current_take = TakeWrapper(current_take_name)
	result = current_take
	return result

	
def findTake(take_name):
	
	'''returnsTake object or None'''
		
	hscript_cmd = 'takels -q -i ' + take_name
	hscript_cmd_results = hou.hscript(hscript_cmd)
	
	if hscript_cmd_results[0] == '':
		result = None
	else:
		take_name = hscript_cmd_results[0].split()[0]
		result = TakeWrapper(take_name)

	return result
	
	
def prefixForNewTakeNames():
	
	''' return the prefix used when creating new takes'''
	
	prefix_name = hou.hscript("echo $EYEVEXTOOLS_TAKE_PREFIX")[0].rstrip()

	if prefix_name == '':
		prefix_name = 'take'
	
	result = prefix_name
	return result

	
def rootTake():
	
	'''returns the root Take object'''

	result = allTakes()[0]
	return result

	
def setCurTake(take):
	
	'''sets the active Take'''
	
	take_name = take.name()
	hscript_cmd = 'takeset ' + take_name
	hscript_cmd_results = hou.hscript(hscript_cmd)
	
	if _takeErr(hscript_cmd_results[1]):
		result = None
	else: result = take
	
	return None

	
def setPrefixForNewTakeNames(prefix_name='take'):
	
	''' set the prefix used when vreating new takes'''
	
	hscript_cmd = 'takename -g' + prefix_name
	hou.hscript(hscript_cmd)
	
	hscript_cmd = 'setenv EYEVEXTOOLS_TAKE_PREFIX=' + prefix_name
	hou.hscript(hscript_cmd)
	
	result = prefix_name
	return None