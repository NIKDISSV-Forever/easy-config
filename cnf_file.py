from configparser import *
from os import listdir as ld

def listdir(formats=['ini', 'cnf']):
	files = []
	formats = list(formats)
	for i in ld():
		for j in formats:
			if j[0] != '.':
				j = '.' + j
			if i[-(len(j)):] == j:
				files.append(i)
	return files

def parsers(fn=None):
	files = []
	for i in ld():
		if i[-4:] == '.ini':
			files.append(i)
		if i[-4:] == '.cnf':
			files.append(i)
	
	if fn == None:
		return ConfigParser()
	else:
		return parse(fn)

	if fn == None:
		return ConfigParser()
	else:
		return parse(fn)
def is_section(sn):
	if not sn.isspace():
		result_section = sn.partition('[')[-1].partition(']')[0].split()
		if result_section == []:
			sn = f"[{sn}]"
			return (False, sn)
		else:
			return (True, '[' + result_section[0] + ']')
	else:
		return (False, sn)

def is_option(op, sep='='):
	if sep.isspace():
		sep = '='
	if len(op) > 0:
		if op[0].isspace():
			return (False, op.split(sep), op)
	else:
		return (False, op, op)
	if isinstance(op, list) or isinstance(op, tuple):
		opsplit = op
	else:
		sep = sep.split()[0]
		opsplit = op.split(sep)
	if len(opsplit) > 1:
		isbool = True
	elif len(opsplit) == 1:
		isbool = False
	else:
		isbool = False
	return (isbool, f"{opsplit[0].split()[0]}{sep}{opsplit[-1].split()[0]}".split(sep), f"{opsplit[0].split()[0]}{sep}{opsplit[-1].split()[0]}")

def is_comment(string, seps=[';', '#']):
	seps = list(seps)
	for sep in seps:
		if sep.isspace() or sep == '':
			seps.remove(sep)
	if seps == []:
		return (False, dict())
	if string.isspace() or string == '':
		return (False, dict())
	
	coms_dict = dict()
	for sep in seps:
		coms_dict[sep] = string.split(sep)[1:]
	isbool = False
	for sep in seps:
		if coms_dict[sep] != [] and isbool == False:
			isbool = True
	return (isbool, coms_dict)

class parse():
	def __init__(self, fn):
		try:
			self.file = open(str(fn), 'r')
			self.file_name = fn
			self.text = self.file.read()
		except Exception as FErr:
			return FErr
	
	def read(self):
		config_dict = dict()
		for line in self.text.split('\n'):
			section = is_section(line)
			option = is_option(line)
			if section[0]:
				section_now = section[1]
				config_dict[section_now] = dict()
			if option[0]:
				try:
					config_dict[section_now][option[1][0]] = option[1][1]
				except UnboundLocalError:
					config_dict['Without_Section'] = dict()
					config_dict['Without_Section'][option[1][0]] = option[1][1]
		
		self.dict = config_dict
	
	def comments(self, sep=[';', '#']):
		comments_dict = dict()
		for line in self.text.split('\n'):
			comments_dict[line] = is_comment(line, sep)
		
		return comments_dict
	
	def find_value(self, value):
		res = []
		for line in self.text.split('\n'):
			op = is_option(line)
			if op[0] == True:
				if op[1][1] == value:
					res.append((op[1][0]))
		return res

	def find_option(self, option):
		res = []
		for line in self.text.split('\n'):
			op = is_option(line)
			if op[0] == True:
				if op[1][0] == option:
					res.append((op[1][1]))
		return res


class add():
	
	def __init__(self, fn, invert=False):
		try:
			self.file = open(str(fn), 'a')
			self.file_name = str(fn)
			self.invert = invert
		except Exception as FErr:
			return FErr
	
	def section(self, sN):
		if not self.invert:
			self.file.write('\n' + is_section(sN)[-1])
		else:
			with open(self.file_name, 'r') as inif:
				text = inif.read()
			with open(self.file_name, 'w') as inif:
				inif.write(is_section(sN)[-1] + '\n' + text)

	def option(self, value, separator='='):
		option = is_option(value, separator)
		if not self.invert:
			self.file.write('\n' + option[-1])
		else:
			with open(self.file_name, 'r') as inif:
				text = inif.read()
			with open(self.file_name, 'w') as inif:
				inif.write(option[-1] + '\n' + text)
		return option[-2]

class edit():
	def __init__(self, fn):
		try:
			self.file = open(str(fn), 'r')
			self.file_name = str(fn)
		except Exception as FErr:
			return FErr
	
	def section(self, sNbefore, sNafter):
		result_text = ""
		sNbefore = is_section(sNbefore)[-1]
			
		sNafter = is_section(sNafter)[-1]
		for line in self.file.read().split('\n'):
			section = is_section(line)
			if (section[0] == True) and (section[-1] == sNbefore):
				result_text += '\n' + sNafter
			else:
				result_text += '\n' + line
		
		with open(self.file_name, 'w') as inif:
			inif.write(result_text)

	def option(self, option, value=None, section=False):
		result_text = ""
		op = option
		if (isinstance(op, list) or isinstance(op, tuple)) and len(op) > 1:
			option1 = is_option(op[0])[1][0]
			option2 = is_option(op[-1])[1][0]
			for line in self.file:
				option = is_option(line)
				if option[0]:
					if option[1][0] == option1:
						result_text += '\n' + is_option([option2, option[1][1]])[-1]
					else:
						result_text += '\n' + line
				else:
					result_text += '\n' + line
		else:
			use=True
			
			option = is_option(option)[1][0]
			value = is_option(value)[1][1]
			if section != False:
				section = is_section(section)[-1]
			for line in self.file:
				op = is_option(line)
				if section != False: 
					sec = is_section(line)
					if sec[0]:
						if sec[-1] == section:
							use = True
						else:
							use = False
				else:
					use = True
				if (op[0] == True) and (op[1][0] == option) and use:
					result_text += is_option([option, value])[-1]
				else:
					result_text += '\n' + line
		
		with open(self.file_name, 'w') as inif:
			inif.write(result_text)

class delete():
	def __init__(self, fn):
		try:
			self.file = open(str(fn), 'r')
			self.file_name = str(fn)
			with open(str(fn), 'r') as inif:
				self.text = inif.read()
		except Exception as FErr:
			return FErr
			
	def section(self, section, only=True):
		result_text = ''
		
		section = is_section(section)[-1]
		for line in self.text.split('\n'):
			sec = is_section(line)
			passels = False
			if sec[0]:
				
				if sec[-1] == section:
					if not only:
						passels = True
					else:
						passels = False
				else:
					result_text += '\n' + line
					passels = False
			else:
				if not passels:
					result_text += '\n' + line
		
		with open(self.file_name, 'w') as inif:
			inif.write(result_text)
	
	def option(self, option):
		result_text = ''
		option = is_option(option)[1][0]
		for line in self.text.split('\n'):
			op = is_option(line)
			if op[0]:
				if op[1][0] == option:
					pass
				else:
					result_text += '\n' + line
		with open(self.file_name, 'w') as inif:
			inif.write(result_text)
			
	def clear(self):
		with open(self.file_name, 'w') as inif:
			inif.write('')
	
	def comments(self):
		result_text = ''
		
		for line in self.text.split('\n'):
			if is_comment(line)[0]:
				pass
			else:
				result_text += '\n' + line
		
		with open(self.file_name, 'w') as inif:
			inif.write(result_text)
	
	def reestablish(self):
		with open(self.file_name, 'r') as inif:
			textBefore = inif.read()
		with open(self.file_name, 'w') as inif:
			inif.write(self.text)
		return (textBefore, self.text)
