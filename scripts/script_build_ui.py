import math
import re

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
	
	numItems = math.floor((theMax-theMin)/init) + 1
	
	items = [min((theMin + step*i), theMax) for i in range(numItems)]
	
	par.menuNames = ['i' + str(i) for i in items]
	par.menuLabels = [str(i) for i in items]


def add_ui(path: str, node, container):

	global added_par_ids
	global activewidgets
	global page

	layout = node.get('type') # hgroup, vgroup
	if layout == 'hgroup':
		container.par.align = 'horizlr'
	else:
		container.par.align = 'verttb'
	
	label = node.find('label')
	
	if label is not None:
		label = label.text
		path += '/' + legal_chan_name(label)
	else:
		label = ''
	
	for i, widgetref in enumerate(node.findall('widgetref')):
		widgetid = widgetref.get('id')
		
		# check if we've haven't already added it to the base
		if widgetid not in added_par_ids:
			added_par_ids.add(widgetid)
			
			# find the exact widget
			widget = activewidgets[widgetid]['widget']
			
			# add the par to the base
			widgettype = widget.get('type')
			parlabel = widget.find('label').text + ' ' + widgetid
			parname = legal_parname(parlabel)
			
			if widgettype in ['vslider', 'hslider']:
				# it's a slider
				par = page.appendFloat(parname, label=parlabel, size=1)
				
				setup_par_float(par[0], widget)
								
			elif widgettype == 'button':
				
				par = page.appendPulse(parname, label=parlabel)
				
			elif widgettype == 'checkbox':
			
				par = page.appendToggle(parname, label=parlabel)
				
			elif widgettype == 'nentry':
			
				par = page.appendMenu(parname, label=parlabel)
				
				setup_par_menu(par[0], widget)
				
			activewidgets[widgetid]['par'] = par[0]
			activewidgets[widgetid]['parname'] = parname
			activewidgets[widgetid]['parlabel'] = parlabel
			activewidgets[widgetid]['faust_path'] = path + '/' + legal_chan_name(widget.find('label').text)

		else:
			# the par was already added to base_pars
			parname = activewidgets[widgetid]['parname']
			
		# add the widget to the UI container.
		widget = activewidgets[widgetid]['widget']
		widgettype = widget.get('type')
		if widgettype == 'vslider':
			widget_source = op('masterSlider_vert')
		elif widgettype == 'hslider':
			widget_source = op('masterSlider_horz')
		elif widgettype == 'button':
			widget_source = op('masterButton')
		elif widgettype == 'checkbox':
			widget_source = op('masterCheckbox')
		elif widgettype == 'nentry':
			widget_source = op('masterDropMenu')
		else:
			raise ValueError('Unexpected widget type: ' + widgettype)

		# Look for meta tags such as [style:knob]
		for meta in widget.findall('meta'):
			if meta.get('key') == 'style':
				if meta.text == 'knob':
					widget_source = op('masterKnob')

		new_widget = container.copy(widget_source, name=parname, includeDocked=True)
		
		new_widget.nodeX = i*250
		
		# add label to the widget
		if widgettype in ['hslider', 'vslider']:
			if widget_source == op('masterKnob'):
				new_widget.par.Knoblabel = activewidgets[widgetid]['parlabel']
			else:
				new_widget.par.Sliderlabelnames = activewidgets[widgetid]['parlabel']
		elif widgettype == 'button':
			new_widget.par.Buttonofflabel = new_widget.par.Buttononlabel = activewidgets[widgetid]['parlabel']
		elif widgettype == 'nentry':
			new_widget.par.Menunames = " ".join(["'{0}'".format(a) for a in activewidgets[widgetid]['par'].menuNames])
			new_widget.par.Menulabels = " ".join(["'{0}'".format(a) for a in  activewidgets[widgetid]['par'].menuLabels])
		
		# add binding to the widget
		new_widget.par.display = True
		new_widget.par.Value0.mode = ParMode.BIND
		new_widget.par.Value0.bindExpr = f'op("{basepars.path}").par.{parname}'
		new_widget.par.Value0.bindRange = True
	
	# For all groups inside, recursively add UI
	for i, group in enumerate(node.findall('group')):
	
		# create a new container for the group
		newContainer = container.create(containerCOMP, tdu.legalName(group.find('label').text))
		newContainer.nodeX = i*250
		newContainer.viewer = True
	
		# recursively add UI
		add_ui(path, group, newContainer)


import xml.etree.ElementTree as ET
root = ET.fromstring(op('faust_ui_xml').text)

ui = root.findall('ui')[0]

basepars = op('base_pars')

basepars.destroyCustomPars()

uic = op('ui_container')

for anOp in uic.ops('./*'):
	anOp.destroy()

page = basepars.appendCustomPage('Custom')

activewidgets = {}
for widget in ui.find('activewidgets').findall('widget'):
	activewidgets[widget.get('id')] = {'widget': widget, 'parname': None}

added_par_ids = set()

add_ui('', ui.find('layout'), uic)

dat = op('rename_pars_dat')
dat.clear()

for widget in activewidgets.values():
	dat.appendRow([
		widget['parname'], widget['faust_path']
		])
