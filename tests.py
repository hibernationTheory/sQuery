import unittest
from sQuery import sQuery
import hou

class HouTests(unittest.TestCase):
	def test_is_obj_context_selected(self):
		sq = sQuery.sQuery("obj")
		self.assertEqual(sq._data[0], hou.node("/obj"))

	def test_is_shop_context_selected(self):
		sq = sQuery.sQuery("shop")
		self.assertEqual(sq._data[0], hou.node("/shop"))

	def test_is_out_context_selected(self):
		sq = sQuery.sQuery("out")
		self.assertEqual(sq._data[0], hou.node("/out"))

	"""
	def test_isBoxSelected(self): #! TO BE IMPLEMENTED
		boxPath = "/obj/box"
		box = hou.node(boxPath)
		sq = sQuery.sQuery(box)
		self.assertEqual(sq._data[0], box)
	"""

	def test_is_child_with_name_box_selected(self):
		boxPath = "/obj/box"
		box = hou.node(boxPath)

		sq = sQuery.sQuery()
		sel = sq.children("box")

		self.assertListEqual(sel._data, [box])

	def test_is_all_children_with_matching_name_box_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.name().find("box") != -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*box*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_box_and_type_geo_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.name().find("box") != -1 and i.type().name() == "geo":
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*box*").filter("t#geo")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_box_and_type_name_has_light_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.name().find("box") != -1 and i.type().name().find("light") != -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*box*").filter("t#*light*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_type_name_has_ge_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.type().name().find("ge") != -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("t#*ge*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_attribute_light_intensity_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.parm("light_intensity"):
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("[light_intensity]")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_attribute_scale_3_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			parm = i.parm("scale")
			if parm:
				if parm.eval() == 3:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("[scale=3]")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_tx_10_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			parm = i.parm("tx")
			if parm:
				if parm.eval() == 10:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("[tx=10]")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_type_name_has_light_and_tx_10_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			parm = i.parm("tx")
			if parm and i.type().name().find("light") != -1:
				if parm.eval() == 10:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("[tx=10]").filter("t#*light*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_type_name_has_light_and_tx_not_10_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			parm = i.parm("tx")
			if parm and i.type().name().find("light") != -1:
				if parm.eval() != 10:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("[tx!=10]").filter("t#*light*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_box_and_shoppath_has_est(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			parm = i.parm("shop_materialpath")
			if parm and i.name().find("box") != -1:
				if parm.evalAsString().find("est") != -1:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*box*").filter("[shop_materialpath~=est]")

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_sphere_and_shoppath_not(self):
		selData = []
		objPath = "/obj"
		shop_path = "/shop/mantrasurface_unique"
		for i in hou.node(objPath).children():
			parm = i.parm("shop_materialpath")
			if parm and i.name().find("sphere") != -1:
				if parm.evalAsString() != shop_path:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*sphere*").filter("[shop_materialpath!=%s]" %shop_path)

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_sphere_and_shoppath_startswith_ran(self):
		# sq selection doesn't contain empty shop_materialpath attrs when it should
		selData = []
		objPath = "/obj"
		shop_path = "ran"
		for i in hou.node(objPath).children():
			parm = i.parm("shop_materialpath")
			if parm:
				if parm.evalAsString().startswith(shop_path) and i.name().find("sphere") != -1:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*sphere*").filter("[shop_materialpath^=%s]" %shop_path)

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_name_has_sphere_and_shoppath_endswith_dom(self):
		# sq selection doesn't contain empty shop_materialpath attrs when it should
		selData = []
		objPath = "/obj"
		shop_path = "dom"
		for i in hou.node(objPath).children():
			parm = i.parm("shop_materialpath")
			if parm:
				if parm.evalAsString().endswith(shop_path) and i.name().find("sphere") != -1:
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("*sphere*").filter("[shop_materialpath$=%s]" %shop_path)

		self.assertListEqual(sel._data, selData)

	def test_is_all_children_with_type_name_has_light_but_name_not_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.type().name().find("light") != -1 and i.name().find("box") == -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("t#*light*").remove("*box*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_subchildren_with_type_name_has_light_but_name_not_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("light") != -1 and i.name().find("box") == -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.find("t#*light*").remove("*box*")

		self.assertListEqual(sel._data, selData)

	def test_is_all_subchildren_with_type_name_facet_with_parent_name_has_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("facet") != -1 and i.parent().name().find("box") != -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.find("t#*facet*").parent("*box*").children("t#facet")

		self.assertListEqual(sel._data, selData)

	def test_is_all_subchildren_with_siblings_to_facet_with_type_name_switch(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("facet") != -1:
				parent = i.parent()
				children = parent.children()
				for j in children:
					if j.type().name().find("switch") != -1:
						selData.append(j)

		sq = sQuery.sQuery()
		sel = sq.find("t#*facet*").siblings("t#switch")
		self.assertListEqual(sel._data, selData)

	def test_next_node_to_all_subchildren_that_are_type_facet_at_index_zero(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("facet") != -1:
				next = i.outputs()[0]
				selData.append(next)

		sq = sQuery.sQuery()
		sel = sq.find("t#*facet*").next()
		self.assertListEqual(sel._data, selData)

	def test_prev_node_to_all_subchildren_that_are_switch_at_index_zero(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("switch") != -1:
				prev = i.inputs()[0]
				selData.append(prev)

		sq = sQuery.sQuery()
		sel = sq.find("t#*switch*").prev()
		self.assertListEqual(sel._data, selData)

	def test_prev_node_to_all_subchildren_that_are_switch_at_index_one(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("switch") != -1:
				prev = i.inputs()[1]
				selData.append(prev)

		sq = sQuery.sQuery()
		sel = sq.find("t#*switch*").prev(index=1)
		self.assertListEqual(sel._data, selData)

	def test_select_all_children_remove_all_type_name_light_add_back_light_with_name_has_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.type().name().find("light") == -1:
				selData.append(i)
			else:
				if i.name().find("box"):
					selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children().remove("t#light").addBack("*box*")
		self.assertListEqual(sel._data, selData)

	def test_select_all_children_with_name_grid_set_keeppos_to_true(self):
		selData = []
		parmData = []
		parmDataSq = []
		objPath = "/obj"

		for i in hou.node(objPath).children():
			if i.name().find("grid") != -1:
				selData.append(i)
				p = i.parm("keeppos")
				if p:
					p.set(1)
					if p.eval() == 1:
						parmData.append(i)
					p.set(0)

		sq = sQuery.sQuery()
		sel = sq.children("*grid*")
		sel.setAttr("keeppos", 1)

		for i in sel._data:
			p = i.parm("keeppos")
			if p:
				if p.eval() == 1:
					parmDataSq.append(i)
				p.set(0)

		self.assertListEqual(parmDataSq, parmData)

	def test_select_all_children_with_name_grid_keeppos_set_keeppos_to_false(self):
		selData = []
		parmData = []
		parmDataSq = []
		objPath = "/obj"
		
		for i in hou.node(objPath).children():
			if i.name().find("grid_keeppos") != -1:
				selData.append(i)
				p = i.parm("keeppos")
				if p:
					p.set(0)
					if p.eval() == 0:
						parmData.append(i)
					p.set(1)

		sq = sQuery.sQuery()
		sel = sq.children("*grid_keeppos*")
		sel.setAttr("keeppos", 0)

		for i in sel._data:
			p = i.parm("keeppos")
			if p:
				if p.eval() == 0:
					parmDataSq.append(i)
				p.set(1)

		self.assertListEqual(parmDataSq, parmData)

	def test_initialization_in_an_object(self):
		selData = []
		objPath = "/obj"
		pointlight4Address = objPath + "/pointlight4"
		pointlight4 = hou.node(pointlight4Address)
		selData.append(pointlight4)

		sel = sQuery.sQuery(pointlight4)
		self.assertListEqual(sel._data, selData)

	def test_set_selected_for_all_subchildren_with_type_name_light_and_name_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("light") != -1 and i.name().find("box") != -1:
				i.setSelected(True)

		getSelected = list(hou.selectedNodes())
		for i in getSelected:
			i.setSelected(False)

		sq = sQuery.sQuery()
		sel = sq.find("t#*light*").filter("*box*").setSelected(True)
		getSelectedSq = list(hou.selectedNodes())
		for i in getSelectedSq:
			i.setSelected(False)

		self.assertListEqual(getSelectedSq, getSelected)

	def test_select_for_all_subchildren_with_type_name_light_and_name_box(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).allSubChildren():
			if i.type().name().find("light") != -1 and i.name().find("box") != -1:
				i.setSelected(True)

		getSelected = list(hou.selectedNodes())
		for i in getSelected:
			i.setSelected(False)

		sq = sQuery.sQuery()
		sel = sq.find("t#*light*").filter("*box*").select()
		getSelectedSq = list(hou.selectedNodes())
		for i in getSelectedSq:
			i.setSelected(False)

		self.assertListEqual(getSelectedSq, getSelected)


	""" yet to be implemented - multiple selections
	def test_is_all_children_with_type_name_has_ge_and_type_name_has_li_selected(self):
		selData = []
		objPath = "/obj"
		for i in hou.node(objPath).children():
			if i.type().name().find("ge") != -1 and i.type().name().find("li") != -1:
				selData.append(i)

		sq = sQuery.sQuery()
		sel = sq.children("t#*ge*")

		self.assertListEqual(sel._data, selData)
	"""

def main(): #! unittest.main() doesn't work for some reason
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(HouTests)
	unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
	main()