import math
import re
import json
from typing import NamedTuple, List

# import TouchDesigner
import td

# active widget types are ones which will need custom parameters on a Base COMP.
ACTIVE_WIDGET_TYPES = ['button', 'checkbox', 'nentry', 'hslider', 'vslider']
PASSIVE_WIDGET_TYPES = ['hbargraph', 'vbargraph']
CONTAINER_WIDGET_TYPES = ['hgroup', 'vgroup', 'tgroup']

class Widget(NamedTuple):
    type: str
    address: str
    par: td.Par = None
    meta: List = []
    min: float = 0
    max: float = 0
    step: float = 0


def legal_chan_name(name: str):

	# NB: The steps in this method must match the steps in the C++ FaustCHOPUI::addParameter

	# Remove parentheses.
	# Note that this regex must be done exactly the same in C++ in the FaustCHOP_UI addParameter method.

	name = re.sub(r"[\(\)]*", "", name)

	# Replace groups of white space with a single underscore
	name = re.sub(r"\s+", "_", name)
	
	return name


def setup_par_float(par: td.Par, item):

	par.min = par.normMin = item['min']
	par.max = par.normMax = item['max']
	par.clampMin = par.clampMax = True
	
	par.default = par.val = item['init']


def setup_par_menu(par: td.Par, item):

	init = item['init']
	theMin = item['min']
	theMax = item['max']
	step = item['step']
	
	numItems = math.floor((theMax-theMin)/step) + 1
	
	items = [min((theMin + step*i), theMax) for i in range(numItems)]
	
	par.menuNames = ['i' + str(i) for i in items]
	par.menuLabels = [str(i) for i in items]


class FaustUIBuilder:

	def legal_parname(self, name: str):

		"""
		Make strings that can be used as custom parameters in TouchDesigner.
		See https://docs.derivative.ca/Custom_Parameters#Naming_Conventions
		"""
		name = re.sub(r"\W*", "", name, count=0, flags=0).replace('_', '')

		firstChar = name[0].upper()

		# If the first char is a digit, precede it by a capital P
		firstChar = re.sub(r"\d", "P" + firstChar, firstChar)

		prefix = firstChar + name.lower()[1:]

		i = 0
		parname = prefix
		while parname in self.added_parnames:
			i += 1
			parname = prefix + str(i)

		self.added_parnames.add(parname)

		return parname

	def build_ui(self, faust_json: str, basecontrol: td.COMP, uic: td.COMP):

		self.basecontrol = basecontrol  # Base COMP where the control parameters are
		self.uic = uic  # UI container

		self.widgets = dict()
		self.added_parnames = set()

		# todo: delete the pars on the Control page rather than the entire page
		for customPage in self.basecontrol.customPages:
			if customPage.name == 'Control':
				customPage.destroy()
		# Recreate page for Control
		self.page = self.basecontrol.appendCustomPage('Control')

		if uic is not None:
			for anOp in uic.ops('./*'):
				anOp.destroy()
			uic.par.align = 'verttb'

		dat = basecontrol.op('./rename_pars_dat')
		dat.clear()

		if faust_json == '':
			return

		root = json.loads(faust_json)

		# root["name"]  # todo: use this?

		for item in root['ui']:
			self._add_ui(item, 0, uic)

		for widget in self.widgets.values():
			if widget.par is not None:
				dat.appendRow([widget.par.name, widget.address])

	def _create_widget(self, item):

		"""add the widget if it's not already in self.widgets. Then return it."""

		address = legal_chan_name(item['address'])

		label = item['label']
		widgettype = item['type']

		if address not in self.widgets:

			# add the par to the base
			parname = self.legal_parname(label)
			
			if widgettype in ['vslider', 'hslider']:
				# it's a slider
				par = self.page.appendFloat(parname, label=label, size=1)
				setup_par_float(par[0], item)
								
			elif widgettype == 'button':
				
				par = self.page.appendPulse(parname, label=label)

			elif widgettype == 'checkbox':
			
				par = self.page.appendToggle(parname, label=label)

			elif widgettype == 'nentry':
			
				par = self.page.appendMenu(parname, label=label)
				setup_par_menu(par[0], item)

			elif widgettype in PASSIVE_WIDGET_TYPES:

				par = [None]

			meta = item['meta'] if 'meta' in item else []
			self.widgets[address] = Widget(item['type'], address, par[0], meta,
				item['min'] if 'min' in item else 0,
				item['max'] if 'max' in item else 0,
				item['step'] if 'step' in item else 0
				)

		return self.widgets[address]

	def _add_widget_ui(self, widget: Widget, i: int, container: td.COMP, children_items):

		if container is None:
			return None

		FAUST_WIDGETS = op.FAUST.op('./faust_widgets')

		widgettype = widget.type
					
		# add the widget to the UI container.
		if widgettype == 'vslider':
			widget_source = FAUST_WIDGETS.op('./masterSlider_vert')
		elif widgettype == 'hslider':
			widget_source = FAUST_WIDGETS.op('./masterSlider_horz')
		elif widgettype == 'button':
			widget_source = FAUST_WIDGETS.op('./masterButton')
		elif widgettype == 'checkbox':
			widget_source = FAUST_WIDGETS.op('./masterCheckbox')
		elif widgettype == 'nentry':
			widget_source = FAUST_WIDGETS.op('./masterDropMenu')
		elif widgettype == 'hbargraph':
			widget_source = FAUST_WIDGETS.op('./masterBarGraph')
		elif widgettype == 'vbargraph':
			widget_source = FAUST_WIDGETS.op('./masterBarGraph')
		elif widgettype in ['hgroup', 'vgroup']:
			widget_source = FAUST_WIDGETS.op('./masterHeader')
			# edge case where we don't want to create the header
			if widget.address == 'TD' or widget.address == '0x00':
				return None
		elif widgettype == 'tgroup':
			widget_source = FAUST_WIDGETS.op('./masterRadio')
		else:
			raise ValueError(f'Unexpected widget type: {widget_source}')
			
		# Look for meta tags such as [style:knob]
		is_knob = False
		for meta in widget.meta:
			if 'style' in meta:
				if meta['style'] == 'knob':
					widget_source = FAUST_WIDGETS.op('./masterKnob')
					is_knob = True
			if 'tooltip' in meta:
				tooltip = meta['tooltip']
				# remove double white space in the tooltip
				tooltip = re.sub("\s+"," ", tooltip)
				widget.par.help = tooltip

		name = widget.address.split('/')[-1]
		new_widget = container.copy(widget_source, name=name, includeDocked=True)
		
		new_widget.nodeX = i*250
		new_widget.nodeY =  -500
		
		# add label to the widget
		if widgettype in ['hslider', 'vslider']:
			if is_knob:
				new_widget.par.Knoblabel = widget.par.label
			else:
				new_widget.par.Sliderlabelnames = '"' + widget.par.label + '"'
		elif widgettype == 'button':
			new_widget.par.Buttonofflabel = new_widget.par.Buttononlabel = widget.par.label
		elif widgettype == 'checkbox':
			# todo: add a label to the checkbox somehow
			pass
		elif widgettype == 'nentry':
			new_widget.par.Menunames = " ".join(["'{0}'".format(a) for a in widget.par.menuNames])
			new_widget.par.Menulabels = " ".join(["'{0}'".format(a) for a in widget.par.menuLabels])
		elif widgettype == 'hbargraph':
			new_widget.par.Sliderorient = 'horz'
		elif widgettype == 'vbargraph':
			new_widget.par.Sliderorient = 'vert'
		elif widgettype in ['hgroup', 'vgroup']:
			if widget.address == 'DSP1':
				new_widget.par.Headerlabel = "Instrument"
			elif widget.address == 'DSP2':
				new_widget.par.Headerlabel = "Effect"
			else:
				new_widget.par.Headerlabel = widget.address
		elif widgettype == 'tgroup':
			new_widget.par.Widgetlabel = widget.address
			if container == self.uic and self.basecontrol.par.Polyphony.eval():
				new_widget.par.Radiolabels = "Instrument Effect"
			else:
				child_labels = [child['label'] for child in children_items]
				new_widget.par.Radiolabels = " ".join([f'"{label}"' for label in child_labels])
		else:
			raise ValueError(f'Unexpected widget type: {widgettype}')

		if widgettype in PASSIVE_WIDGET_TYPES:
			new_widget.par.Value0.mode = ParMode.EXPRESSION
			new_widget.par.Value0.expr = f'tdu.remap(  op("{self.basecontrol.path}").op("./info1")["bargraph_{name}"]  , {widget.min}, {widget.max}, 0, 1)'
		elif widgettype in ACTIVE_WIDGET_TYPES:
			# add binding to the widget
			new_widget.par.Value0.mode = ParMode.BIND
			new_widget.par.Value0.bindExpr = f'op("{self.basecontrol.path}").par.{widget.par.name}'
			new_widget.par.Value0.bindRange = True
		elif widgettype in CONTAINER_WIDGET_TYPES:
			pass
		else:
			raise ValueError(f'Unexpected widget type: {widgettype}')

		return new_widget

	def _add_ui(self, item, i: int, container: td.COMP):

		widgettype = item['type'] # hgroup, vgroup, tgroup, or other
		
		label = item['label']

		# For all groups inside, recursively add UI
		children_items = item['items'] if 'items' in item else []

		new_widget_ui = None

		# is the item something that corresponds to a td.Par?
		if widgettype in (ACTIVE_WIDGET_TYPES + PASSIVE_WIDGET_TYPES + CONTAINER_WIDGET_TYPES):

			if widgettype in (ACTIVE_WIDGET_TYPES + PASSIVE_WIDGET_TYPES):

				address = legal_chan_name(item['address'])

				polyphony = self.basecontrol.par.Polyphony.eval()
				name = address.split('/')[-1]
				if name.lower() in ["gate", "gain", "note", "freq"] and polyphony:
					# Skip these parameters when Polyphony is enabled.
					return

				widget = self._create_widget(item)
			else:
				widget = Widget(widgettype, label, None, [])

			new_widget_ui = self._add_widget_ui(widget, i, container, children_items)

		elif widgettype == 'soundfile':
			pass
		else:
			raise ValueError('Unexpected widget type: ' + widgettype)

		if children_items:

			legalName = label.replace('/','_')
			legalName = tdu.legalName(legalName)

			container = container.create(containerCOMP, legalName)
			container.nodeX = 0
			container.nodeY = 250
			container.viewer = True
			container.par.hmode = 'fill'
			container.par.vmode = 'fill'

			if widgettype == 'hgroup':
				container.par.align = 'horizlr'
			elif widgettype == 'vgroup':
				container.par.align = 'verttb'
			elif widgettype == 'tgroup':
				# todo: make this different
				container.par.align = 'horizlr'

		for j, group in enumerate(children_items):

			if container is not None and group['type'] in CONTAINER_WIDGET_TYPES:
				# create a new container for the group
				legalName = group['label'].replace('/','_')
				legalName = tdu.legalName(legalName)
				newContainer = container.create(containerCOMP, legalName)
				newContainer.nodeX = j*250
				newContainer.nodeY =   0
				newContainer.viewer = True
				newContainer.par.hmode = 'fill'
				newContainer.par.vmode = 'fill'
				newContainer.par.align = 'verttb'
				newContainer.par.alignorder = j

				if widgettype == 'tgroup':
					newContainer.par.display.mode = ParMode.EXPRESSION
					newContainer.par.display.expr = f'op("{new_widget_ui.path}").par.Value0 == me.par.alignorder'
			else:
				newContainer = container
		
			# recursively add UI
			self._add_ui(group, j, newContainer)