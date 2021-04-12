import xml.etree.ElementTree as ET
root = ET.fromstring(op('faust_ui_xml').text)
# tree = tree
#print(root)

ui = root.findall('ui')[0]
#print(ui)

basepars = op('base_pars')

basepars.destroyCustomPars()

uic = op('ui_container')

for anOp in uic.ops('./*'):
	anOp.destroy()

page = basepars.appendCustomPage('Custom')


# masterSlider_horz

layout = ui.find('layout')

activewidgets = {}
for widget in ui.find('activewidgets').findall('widget'):
	activewidgets[widget.get('id')] = {'widget': widget, 'parname': None}


added_par_ids = set()

def legal_parname(name):

	name = name.strip().replace('_', '').replace(' ', '').replace('.', '')

	name = name.lower()
	name = name[0].upper() + name[1:]
	return name
	
def text_to_num(text):

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
	
	import math
	numItems = math.floor((theMax-theMin)/init) + 1
	
	items = [min((theMin + step*i), theMax) for i in range(numItems)]
	
	par.menuNames = ['i' + str(i) for i in items]
	par.menuLabels = [str(i) for i in items]



def add_ui(path, node, container):

	global added_par_ids
	global activewidgets

	layout = node.get('type') # hgroup, vgroup
	if layout == 'hgroup':
		container.par.align = 'horizlr'
	else:
		container.par.align = 'verttb'
	
	label = node.find('label')
	
	if label is not None:
		label = label.text
		path += '/' + label
	else:
		label = ''
		
	#print('path: ', path, ' label: ', label)
	
	for i, widgetref in enumerate(node.findall('widgetref')):
		widgetid = widgetref.get('id')
		#print('widget: ', widgetref.get('id'))
		
		# check if we've already add it to the base
		if widgetid not in added_par_ids:
			added_par_ids.add(widgetid)
			
			#print('id: ', widgetid)

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
				
				activewidgets[widgetid][par] = par
				activewidgets[widgetid]['parname'] = parname
				activewidgets[widgetid]['parlabel'] = parlabel
				activewidgets[widgetid]['faust_path'] = path + '/' + widget.find('label').text
				
			elif widgettype == 'button':
				
				par = page.appendPulse(parname, label=parlabel)
				
				activewidgets[widgetid][par] = par
				activewidgets[widgetid]['parname'] = parname
				activewidgets[widgetid]['parlabel'] = parlabel
				activewidgets[widgetid]['faust_path'] = path + '/' + widget.find('label').text
				
			elif widgettype == 'checkbox':
			
				par = page.appendToggle(parname, label=parlabel)
				
				activewidgets[widgetid][par] = par
				activewidgets[widgetid]['parname'] = parname
				activewidgets[widgetid]['parlabel'] = parlabel
				activewidgets[widgetid]['faust_path'] = path + '/' + widget.find('label').text
				
				
			elif widgettype == 'nentry':
			
				par = page.appendMenu(parname, label=parlabel)
				
				setup_par_menu(par[0], widget)
				
				activewidgets[widgetid][par] = par[0]
				activewidgets[widgetid]['parname'] = parname
				activewidgets[widgetid]['parlabel'] = parlabel
				activewidgets[widgetid]['faust_path'] = path + '/' + widget.find('label').text
			
				
		else:
			parname = activewidgets[id]['parname']
			
		# add the widget to the UI container. todo: duplicates are allowed?
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

		new_widget = container.copy(widget_source, name=parname, includeDocked=True)
		
		new_widget.nodeX = i*250
		
		# add label to the widget
		if widgettype in ['hslider', 'vslider']:
			new_widget.par.Sliderlabelnames = '"' + activewidgets[widgetid]['parlabel'] + '"'
		elif widgettype == 'button':
			new_widget.par.Buttonofflabel = new_widget.par.Buttononlabel = activewidgets[widgetid]['parlabel']
		elif widgettype == 'nentry':
			new_widget.par.Menunames = " ".join(["'{0}'".format(a) for a in activewidgets[widgetid][par].menuNames])
			new_widget.par.Menulabels = " ".join(["'{0}'".format(a) for a in  activewidgets[widgetid][par].menuLabels])
		
		# add binding to the widget
		new_widget.par.display = True
		new_widget.par.Value0.mode = ParMode.BIND
		new_widget.par.Value0.bindExpr = f'op("{basepars.path}").par.{parname}'
		new_widget.par.Value0.bindRange = True
		
		
	for i, group in enumerate(node.findall('group')):
	
		# create a new container for the group
		newContainer = container.create(containerCOMP, group.find('label').text)
		newContainer.nodeX = i*250
		newContainer.viewer = True
	
		add_ui(path, group, newContainer)


add_ui('', layout, uic)

dat = op('rename_pars_dat')
dat.clear()

for widget in activewidgets.values():
	dat.appendRow([
		widget['parname'], widget['faust_path']
		])
	
