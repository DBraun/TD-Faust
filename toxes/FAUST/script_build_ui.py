import math
import re
import json
from typing import NamedTuple

# import TouchDesigner
import td

WIDGET_TYPES = ['button', 'checkbox', 'nentry', 'hslider', 'vslider']


class Widget(NamedTuple):
    type: str
    address: str
    par: td.Par = None


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

		for customPage in self.basecontrol.customPages:
			if customPage.name == 'Control':
				customPage.destroy()
		# Recreate page for Control
		self.page = self.basecontrol.appendCustomPage('Control')

		if uic is not None:
			for anOp in uic.ops('./*'):
				anOp.destroy()

		dat = basecontrol.op('./rename_pars_dat')
		dat.clear()

		if faust_json == '':
			return

		root = json.loads(faust_json)

		# root["name"]  # todo: use this?

		if root['ui']:
			item = root['ui'][0]
			self._add_ui(item, 0, uic)

		for widget in self.widgets.values():
			dat.appendRow([widget.par.name, widget.address])

	def _add_ui(self, item, i: int, container: td.COMP):

		FAUST = op.FAUST

		widgettype = item['type'] # hgroup, vgroup, tgroup, or other
		if container is not None:
			if widgettype == 'hgroup':
				container.par.align = 'horizlr'
			elif widgettype == 'vgroup':
				container.par.align = 'verttb'
		
		label = item['label']
			
		# is the item something that corresponds to a td.Par?
		if widgettype in WIDGET_TYPES:

			address = legal_chan_name(item['address'])

			polyphony = self.basecontrol.par.Polyphony.eval()
			if address.split('/')[-1].lower() in ["gate", "gain", "note", "freq"] and polyphony:
				# Skip these parameters when Polyphony is enabled.
				pass
			else:
				# check if we've haven't already added it to the base
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

					self.widgets[address] = widget = Widget(item['type'], address, par[0])
				
				# add the widget to the UI container.
				if widgettype == 'vslider':
					widget_source = FAUST.op('./masterSlider_vert')
				elif widgettype == 'hslider':
					widget_source = FAUST.op('./masterSlider_horz')
				elif widgettype == 'button':
					widget_source = FAUST.op('./masterButton')
				elif widgettype == 'checkbox':
					widget_source = FAUST.op('./masterCheckbox')
				elif widgettype == 'nentry':
					widget_source = FAUST.op('./masterDropMenu')
				else:
					raise ValueError(f'Unexpected widget type: {widget_source}')
					
				# Look for meta tags such as [style:knob]
				is_knob = False
				for meta in (item['meta'] if 'meta' in item else []):
					if 'style' in meta:
						if meta['style'] == 'knob':
							widget_source = FAUST.op('./masterKnob')
							is_knob = True
					if 'tooltip' in meta:
						tooltip = meta['tooltip']
						# todo: remove double white space in the tooltip
						widget.par.help = tooltip

				if container is not None and widgettype != 'soundfile':

					widget = self.widgets[address]

					new_widget = container.copy(widget_source, name=widget.par.name, includeDocked=True)
					
					new_widget.nodeX = i*250
					
					# add label to the widget
					if widgettype in ['hslider', 'vslider']:
						if is_knob:
							new_widget.par.Knoblabel = '"' + widget.par.label + '"'
						else:
							new_widget.par.Sliderlabelnames = '"' + widget.par.label + '"'
					elif widgettype == 'button':
						new_widget.par.Buttonofflabel = new_widget.par.Buttononlabel = widget.par.label
					elif widgettype == 'checkbox':
						# todo: don't print
						print('CHECKBOX: ' + str(widget.par.name))
					elif widgettype == 'nentry':
						new_widget.par.Menunames = " ".join(["'{0}'".format(a) for a in widget.par.menuNames])
						new_widget.par.Menulabels = " ".join(["'{0}'".format(a) for a in widget.par.menuLabels])
					
					# add binding to the widget
					new_widget.par.display = True
					new_widget.par.Value0.mode = ParMode.BIND
					new_widget.par.Value0.bindExpr = f'op("{self.basecontrol.path}").par.{widget.par.name}'
					new_widget.par.Value0.bindRange = True

		elif widgettype == 'soundfile':
			pass
		elif widgettype in ['tgroup', 'vgroup', 'hgroup']:
			pass
		else:
			raise ValueError('Unexpected widget type: ' + widgettype)
		
		# For all groups inside, recursively add UI
		other_items = item['items'] if 'items' in item else []
		for j, group in enumerate(other_items):
		
			if container is not None and group['type'] not in WIDGET_TYPES:
				# create a new container for the group
				legalName = group['label'].replace('/','_')
				legalName = tdu.legalName(legalName)
				newContainer = container.create(containerCOMP, legalName)
				newContainer.nodeX = j*250
				newContainer.viewer = True
			else:
				newContainer = container
		
			# recursively add UI
			self._add_ui(group, j, newContainer)
