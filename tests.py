import unittest
from sQuery import sQuery
import hou

class HouTests(unittest.TestCase):
	def test_isObjContext(self):
		sq = sQuery.sQuery("obj")
		self.assertEqual(sq._data[0], hou.node("/obj"))

	def test_isShopContext(self):
		sq = sQuery.sQuery("shop")
		self.assertEqual(sq._data[0], hou.node("/shop"))

	def test_isOutContext(self):
		sq = sQuery.sQuery("out")
		self.assertEqual(sq._data[0], hou.node("/out"))

	def test_isBoxSelected(self): #! TO BE IMPLEMENTED
		boxPath = "/obj/box"
		sq = sQuery.sQuery(hou.node(boxPath))
		self.assertEqual(sq._data[0], hou.node(boxPath)[0])

def main(): #! unittest.main() doesn't work for some reason
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(HouTests)
	unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
	main()