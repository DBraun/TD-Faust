"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

class FaustGlobal:
	"""
	FaustGlobal description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

	def SetupUI(self, faust_xml, basecontrol, ui_comp):

		ui_builder = mod.ui_building.FaustUIBuilder()
		ui_builder.build_ui(faust_xml, basecontrol, ui_comp)
