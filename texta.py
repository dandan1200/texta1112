import sys
import re
import string

# short function that will take a 2d list and flatten it so all elements are in a single list
def flatten_list(in_list):
    out_list = []
    for element in in_list:
        if type(element) == list:
            for item in element:
                out_list.append(item)
        else:
            out_list.append(element)
    return out_list

# Function to error check all files - run before executing commands
def error_handling_file_check():
	#initialise return items
	workingcmds = []
	workingfiles = []
	error_flag = False
	valid_commands = ['filter','fields','replace','count']


	#File open and error handing
	files = [x for x in sys.argv[1:]]
	cmdsf = open(files[0],'r')
	cmds = cmdsf.readlines() 
	cmdsf.close()

	#Iterate through each command in the cmd file and check each cmd for errors
	for cmd_index,cmd in enumerate(cmds):
		line = cmd.split(" ")

		comment_index = 0
		while comment_index < len(line):
			if '#' == line[comment_index]:
				line = line[:comment_index]
				break
			comment_index+=1

		# Remove empty spaces and newline characters in lines
		empty_elems = []
		for line_index,line_elem in enumerate(line):
			line[line_index] = line[line_index].strip("\n")
			if not line_elem:
				empty_elems.append(line_index)
		for line_elem in empty_elems[::-1]:
			line.pop(line_elem)


		if line[0] not in valid_commands:
			sys.stderr.write("Error: command line {}: not a valid command\n".format(cmd_index+1))
			error_flag = True
		
		# error check for filter command
		elif line[0] == 'filter':
			if len(line) < 2:
				sys.stderr.write("Error: command line {}: no regexp in filter\n".format(cmd_index+1))
				error_flag = True
			elif line[1][0] and line[1][-1] != '"':
				sys.stderr.write('Error: command line {}: regexp format incorrect. Missing double quotations ("")\n'.format(cmd_index+1))
				error_flag = True
			elif len(line[1]) < 3:
				sys.stderr.write('Error: command line {}: regexp empty\n'.format(cmd_index+1))
				error_flag = True
			
		
		# error check for fields command
		elif line[0] == 'fields':
			if line[1] == '"' and line[2] == '"':
				line.pop(2)
				line[1] = '""'
			workingFields = []
			if len(line) < 3:
				sys.stderr.write('Error: command line {}: not enough arguments for fields\n'.format(cmd_index+1))
				error_flag = True
			elif line[1][0] and line[1][-1] != '"':
				sys.stderr.write('Error: command line {}: delimiter-string foramt incorrectt. Missing double quotations ("")\n'.format(cmd_index+1))
				error_flag = True
			
			workingFields = line[2:]
	
			for field in line[2:]:

				if field.isdigit() == False:
					sys.stderr.write('Error: command line {}: bad field number\n'.format(cmd_index+1))
					
					workingFields.pop(workingFields.index(field))

				elif int(field) < 0:
					sys.stderr.write('Error: command line {}: negative field number\n'.format(cmd_index+1))
					workingFields.pop(workingFields.index(field))
			
			line = line[:2] + workingFields
			
		#error check for replace command
		if line[0] == 'replace':
			if len(line) < 3:
				sys.stderr.write('Error: command line {}: incorrect number of strings in replace\n'.format(cmd_index+1))
				error_flag = True
			elif (line[1][0] and line[1][-1] != '"') or (line[2][0] and line[2][-1] != '"'):
				sys.stderr.write('Error: command line {}: string format incorrect. Missing double quotations ("")\n'.format(cmd_index+1))
				error_flag = True
		
		#error check for count
		if line[0] == 'count':
			if len(line) != 1:
				sys.stderr.write('Error: command line {}: too many arguments for count command\n'.format(cmd_index+1))
				error_flag = True
			else:
				error_flag = False		
		if error_flag == False:
			workingcmds.append(" ".join(line))

	# testing file names
	for fname in files:
		try:
			f = open(fname,'r')
			workingfiles.append(fname)
		except FileNotFoundError:
			sys.stderr.write("Error: file {} not found\n".format(fname))
			error_flag = True
		except Exception:
			sys.stderr.write("Error: file {} not readable\n".format(fname))
			error_flag = True


	return [error_flag, workingcmds, workingfiles]
	

def main():
	#Fatal error check
	if len(sys.argv) < 3:
		sys.stderr.write("Error: not enough arguments\n")
		exit()
	try:
		f = open(sys.argv[1],'r')
	except FileNotFoundError:
		sys.stderr.write("Error: cmd file not found\n")
		exit()
	

	#Go to error check and recieve working commands and files
	error_handling = error_handling_file_check()
	files = error_handling[2]
	cmds = error_handling[1]

	for filename in files[1:]:

		# Open files
		textf = open(filename,'r')
		text = textf.readlines()
		textf.close()

		# Strip newline characters from data
		for counter,ln in enumerate(text):
			text[counter] = text[counter].strip("\n")

		#Initiate count output variable
		count = -1

		# Iterate through commands and apply to data
		for cmd in cmds:
			cmdstr = cmd.split(" ")
			
			# Execute filter command
			if cmdstr[0] == 'filter':
				text = cfilter(cmdstr[1],text)
			
			# Execute fields command
			elif cmdstr[0] == 'fields':
				text = cfields(cmdstr[1:],text,cmds.index(cmd))
			
			# Execute replace command
			elif cmdstr[0] == 'replace':
				text = creplace(cmdstr[1],cmdstr[2],text)
			
			# Execute count command
			elif cmdstr[0].strip("\n") == 'count':
				count = ccount(text)
		
		# Format data and output.
		for line in text:
			print("".join(line))

		# Write count of output lines to stderr	
		if count > 0:
			sys.stderr.write(str(count)+"\n")
		

# Filter command function
def cfilter(regexp,text):
	filtered = []
	regexp = regexp.strip('"')
	
	
	for line in text:
		if type(line) == list:
			line = "".join(line)
		if re.search(regexp,line)!= None:
			filtered.append(line)
	return filtered

# Fileds command function
def cfields(cmdstr,text,cmdline):
	fields_ret = []
	dlm_str = cmdstr[0].strip('"')
	# Account for empty delimiter
	if dlm_str == "":
		dlm_str = " "

	# List of fields to be taken from text
	fields = [int(x) for x in cmdstr[1:] if x != '']
	
	for line_index,line in enumerate(text):
		# temp_line = ''.join(line)
		fields_ret.insert(line_index, line.split(dlm_str))
		try:
			fields_ret[line_index] = list(fields_ret[line_index][field] + " " for field in fields)
			fields_ret[line_index][-1] = fields_ret[line_index][-1][:-1]
		except IndexError:
			sys.stderr.write("Error: command line {}: bad field number\n".format(cmdline+1))
			break
		
	return fields_ret

# Replace command function
def creplace(str1,str2,text):
	# Format function parameters
	replaced = []
	str1 = str1.strip('"')
	str2 = str2.strip('"')

	for line in text:
		if type(line) == list:
			line = "".join(line)
		temp_line =[]
		for word in line.split(","):
			if str1 in word:
				temp_line.append(word.replace(str1,str2))
			else:
				temp_line.append(word)
		replaced.append(temp_line)

	return replaced

# Count command function
def ccount(text):
	return len(text)

if __name__ == '__main__':
	main()







    
