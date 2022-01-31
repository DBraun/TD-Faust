import math
import re
import xml.etree.ElementTree as ET


def legal_parname(name: str):

	"""
	Make strings that can be used as custom parameters in TouchDesigner.
	See https://docs.derivative.ca/Custom_Parameters#Naming_Conventions
	"""
	name = re.sub(r"\W*", "", name, count=0, flags=0).replace('_', '')

	firstChar = name[0].upper()

	# If the first char is a digit, precede it by a capital P
	firstChar = re.sub(r"\d", "P" + firstChar, firstChar)

	name = firstChar + name.lower()[1:]

	return name


def legal_chan_name(name: str):

	# NB: The steps in this method must match the steps in the C++ FaustCHOPUI::addParameter

	# Remove parentheses.
	# Note that this regex must be done exactly the same in C++ in the FaustCHOP_UI addParameter method.

	name = re.sub(r"[\(\)]*", "", name)

	# Replace groups of white space with a single underscore
	name = re.sub(r"\s+", "_", name)
	
	return name


def text_to_num(text: str):

	"""
	Convert strings like "440.0f" to float numbers. Leave integers as ints.
	"""

	if text[-1] == 'f':
		return float(text[:-1])
	else:
		return int(text)


def setup_par_float(par, widget):

	par.min = par.normMin = text_to_num(widget.find('min').text)
	par.max = par.normMax = text_to_num(widget.find('max').text)
	par.clampMin = par.clampMax = True
	
	par.default = par.val = text_to_num(widget.find('init').text)


def setup_par_menu(par, widget):

	init = text_to_num(widget.find('init').text)
	theMin = text_to_num(widget.find('min').text)
	theMax = text_to_num(widget.find('max').text)
	step = text_to_num(widget.find('step').text)
	
	numItems = math.floor((theMax-theMin)/step) + 1
	
	items = [min((theMin + step*i), theMax) for i in range(numItems)]
	
	par.menuNames = ['i' + str(i) for i in items]
	par.menuLabels = [str(i) for i in items]


class FaustUIBuilder:

	def build_ui(self, faust_xml: str, basecontrol, uic):

		self.basecontrol = basecontrol  # Base COMP where the control parameters are
		self.uic = uic  # UI container, but it may be None

		self.added_par_ids = set()
		self.activewidgets = {}
		self.passivewidgets = {}

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

		if faust_xml == '':
			return

		root = ET.fromstring(faust_xml)

		ui = root.findall('ui')[0]

		instrument_name = root.findall('name')
		if instrument_name is not None:
			self.instrument_name = instrument_name[0].text
		else:
			self.instrument_name = None

		for widget in ui.find('activewidgets').findall('widget'):
			self.activewidgets[widget.get('id')] = {'widget': widget, 'parname': None}
		for widget in ui.find('passivewidgets').findall('widget'):
			self.passivewidgets[widget.get('id')] = {'widget': widget}		

		self._add_ui('', ui.find('layout'), uic)

		for widget in self.activewidgets.values():
			dat.appendRow([
				widget['parname'], widget['faust_path']
				])

	def _add_ui(self, path: str, node, container):

		# Note: container might be None

		FAUST = op.FAUST

		layout = node.get('type') # hgroup, vgroup
		if container is not None:
			if layout == 'hgroup':
				container.par.align = 'horizlr'
			else:
				container.par.align = 'verttb'
		
		label = node.find('label')
		
		if label is not None:
			label = label.text
			if label == '0x00':  # weird necessary step?
				# In faust you should have code like `declare name "MyInstrument";`
				# When this code is missing, `0x00` might show up here.
				# We replace it with the default `my_dsp` which is used in the FaustCHOP C++ code.
				if self.basecontrol.par.Polyphony.eval():
					if self.instrument_name is not None:
						label = 'Sequencer/DSP1/Polyphonic/Voices/' + self.instrument_name
					else:
						label = 'Sequencer/DSP1/Polyphonic/Voices/' + 'my_dsp'
				elif path == '' and self.instrument_name is not None:
					label = self.instrument_name
			path += '/' + legal_chan_name(label)
		else:
			label = ''

		for i, widgetref in enumerate(node.findall('widgetref')):
			widgetid = widgetref.get('id')

			if widgetid in self.passivewidgets:
				continue
			
			# check if we've haven't already added it to the base
			if widgetid not in self.added_par_ids:
				self.added_par_ids.add(widgetid)
				
				# find the exact widget
				widget = self.activewidgets[widgetid]['widget']
				
				# add the par to the base
				widgettype = widget.get('type')
				parlabel = widget.find('label').text
				parname = legal_parname(parlabel + ' ' + widgetid)
				
				if widgettype in ['vslider', 'hslider']:
					# it's a slider
					par = self.page.appendFloat(parname, label=parlabel, size=1)
					
					setup_par_float(par[0], widget)
									
				elif widgettype == 'button':
					
					par = self.page.appendPulse(parname, label=parlabel)
					
				elif widgettype == 'checkbox':
				
					par = self.page.appendToggle(parname, label=parlabel)
					
				elif widgettype == 'nentry':
				
					par = self.page.appendMenu(parname, label=parlabel)
					
					setup_par_menu(par[0], widget)
					
				self.activewidgets[widgetid]['par'] = par[0]
				self.activewidgets[widgetid]['parname'] = parname
				self.activewidgets[widgetid]['parlabel'] = parlabel

				self.activewidgets[widgetid]['faust_path'] = path + '/' + legal_chan_name(widget.find('label').text)

			else:
				# the par was already added to base_pars
				parname = self.activewidgets[widgetid]['parname']
				
			# add the widget to the UI container.
			widget = self.activewidgets[widgetid]['widget']
			widgettype = widget.get('type')
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
			elif widgettype == 'soundfile':
				continue
			else:
				raise ValueError('Unexpected widget type: ' + widgettype)

			# Look for meta tags such as [style:knob]
			for meta in widget.findall('meta'):
				if meta.get('key') == 'style':
					if meta.text == 'knob':
						widget_source = FAUST.op('./masterKnob')

			if container is not None:

				new_widget = container.copy(widget_source, name=parname, includeDocked=True)
				
				new_widget.nodeX = i*250
				
				# add label to the widget
				if widgettype in ['hslider', 'vslider']:
					if widget_source == FAUST.op('./masterKnob'):
						new_widget.par.Knoblabel = '"' + self.activewidgets[widgetid]['parlabel'] + '"'
					else:
						new_widget.par.Sliderlabelnames = '"' + self.activewidgets[widgetid]['parlabel'] + '"'
				elif widgettype == 'button':
					new_widget.par.Buttonofflabel = new_widget.par.Buttononlabel = self.activewidgets[widgetid]['parlabel']
				elif widgettype == 'nentry':
					new_widget.par.Menunames = " ".join(["'{0}'".format(a) for a in self.activewidgets[widgetid]['par'].menuNames])
					new_widget.par.Menulabels = " ".join(["'{0}'".format(a) for a in  self.activewidgets[widgetid]['par'].menuLabels])
				
				# add binding to the widget
				new_widget.par.display = True
				new_widget.par.Value0.mode = ParMode.BIND
				new_widget.par.Value0.bindExpr = f'op("{self.basecontrol.path}").par.{parname}'
				new_widget.par.Value0.bindRange = True
		
		# For all groups inside, recursively add UI
		for i, group in enumerate(node.findall('group')):
		
			if container is not None:
				# create a new container for the group
				newContainer = container.create(containerCOMP, tdu.legalName(group.find('label').text))
				newContainer.nodeX = i*250
				newContainer.viewer = True
			else:
				newContainer = None
		
			# recursively add UI
			self._add_ui(path, group, newContainer)
