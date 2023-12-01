#!/usr/bin/env python3
import os
import subprocess
import glob

# from collections import Counter
from datetime import datetime

import numpy as np

import smtplib  # Work with e-mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import MAIL, MAILFROM, SERVERNAME, PORTNUMBER, USER_ID, USERNAME


def file_exists(path, noprint=False):
	"""
	Checks if file under path exists

	:param path: path to the file
	:type path: str
	:param noprint: print information while executing or not
	:type noprint: bool
	:return: bool
	"""
	if os.path.isfile(path):
		if not noprint:
			print(f'File "{path}" exists...')
		return True
	else:
		if not noprint:
			print(f'File "{path}" does not exist!')
		return False


def dir_exists(path: str, mkdir=False, noprint=False):
	"""
	Checks if directory under path exists, optionally creates directories in path

	:param path: path to the directory
	:param mkdir: True to create directory (directories tree) under path
	:param noprint: print information while executing or not
	:type noprint: bool
	:return: bool
	"""
	if os.path.isdir(path):
		if not noprint:
			print(f'Directory "{path}" exists...')
		return True
	else:
		if not noprint:
			print(f'Directory "{path}" does not exist!')
		if mkdir:
			if not noprint:
				print(f'Making "{path}" directory!')
			os.makedirs(path)
		return False


def send_mail(
		lst_pids: list, size_pids: int, input_name: str, password: str,
		addr=MAIL, me=MAILFROM, server=SERVERNAME, port_number=PORTNUMBER,
		m_type="start"):
	"""
	This function forms mail and sends to specified address with defined
	settings

	:param lst_pids: list with PID numbers
	:param size_pids: size of PID list (total number of PIDs)
	:param input_name: input name with .inp
	:param addr: address of email
	:param me: name for "from" field
	:param server: server name
	:param port_number: port number
	:param password: password for addr
	:param m_type: "start" or "finish"
	"""
	comp_name = os.uname().nodename
	os_version = os.uname().version

	# Forming letter header
	msg = MIMEMultipart("mixed")

	msg["From"] = me
	msg["To"] = addr

	if m_type == "start":
		msg["Subject"] = \
			f"<FLUKA {input_name} Start> " + \
			f" start of {size_pids} processes on {comp_name}"

		# Forming letter
		part = MIMEText(
			f"""{size_pids} process(es) with PID(s): {lst_pids} ({input_name}) started! 
\r\r\nMachine info: {os_version} 
\r\r\nComputer name: {comp_name} 
\r\r\nInfo for notify option: after you receive this e-mail press <ctrl+z> 
and then do: \"bg\" command in terminal (to force script run in background). 
After that terminal can be closed. Notification will be sent after more than a 
half of processes finish.\r\r\n""", "Plain email")

	else:
		msg["Subject"] = \
			f"<FLUKA {input_name} End>" + \
			f" finished more than half of {size_pids} processes on {comp_name}"

		part = MIMEText(
			f"""More than half of PIDs: {lst_pids} ({input_name}) are finished!
\r\r\nMachine info: {os_version}
\r\r\nComputer name: {comp_name}""", "Plain email")
	msg.attach(part)

	if m_type == "start":
		for file in [input_name, "Random.seed", "RandomTotal.seed"]:  # attach files
			with open(file) as f:
				attachment = MIMEText(f.read())

			attachment.add_header(
				"Content-Disposition", "attachment", filename=file)
			msg.attach(attachment)

	# Connection
	s = smtplib.SMTP(server, port_number)
	s.ehlo()
	s.starttls()
	s.ehlo()
	# Auth
	s.login(addr, password)
	# Sending mail
	s.sendmail(me, addr, msg.as_string())
	s.quit()


def get_pids(process):
	"""
	Returns size of list with PID's, its list and last PID
	TODO: better implementation needed

	:param process:
	:return:
	"""
	try:
		pid_list = list(
			map(int, subprocess.check_output(["pidof", process]).split()))
		pid_list.sort()

	except subprocess.CalledProcessError:
		print("Null PID's")
		pid_list = [0]

	return len(pid_list), pid_list, max(pid_list)


# Check if process is still running
def check_process(pid):
	try:
		os.kill(int(pid), 0)
		return True

	except OSError:
		return False


def check_pids_state(lst_pids: list, size_pids: int):
	"""
	Function returns True if half is finished, otherwise False

	:param lst_pids: list with PIDs
	:param size_pids: number of PIDs in list
	:return: True if finished more than 2, otherwise False
	"""

	pids_state = []
	for i in lst_pids:
		pids_state.append(check_process(i))

	pids_fin = pids_state.count(False)  # Number of finished processes

	if pids_fin > size_pids/2:  # If number of finished more than half of total
		return True
	else:
		return False


def create_bomb():
	"""
	Function creates script 'bomb.sh' to stop all FLUKA jobs
	"""
	text = """#!/bin/bash

# Fluka bomb generates fluka.stop in all fluka* directories

DIRLIST=($(ls -d fluka*)) # Create array from list of fluka dirs
TOTAL=${#DIRLIST[@]} # Length of array

echo "Bombing $TOTAL fluka jobs:" # Print size

for ((number = 0; number <= $TOTAL-1; number++)); do
	touch ${DIRLIST[number]}/fluka.stop
	echo ${DIRLIST[number]}/fluka.stop
done
echo done!"""
	with open("bomb.sh", "w") as bomb:
		bomb.write(text)

	subprocess.call("chmod +x bomb.sh", shell=True)


def search_string_in_file(file_name, string_to_search):
	"""Search for the given string in file and return lines containing that string,
	along with line numbers"""
	line_number = 0
	list_of_results = []
	# Open the file in read only mode
	with open(file_name, 'r') as read_obj:
		# Read all lines in the file one by one
		for line in read_obj:
			# For each line, check if line contains the string
			line_number += 1
			if string_to_search in line:
				# If yes, then add the line number & line as a tuple in the list
				list_of_results.append((line_number, line.rstrip()))
	# Return list of tuples containing line numbers and lines where string is found
	return list_of_results


def check_state(input_name: str, start_time):
	"""
	Function information about run status

	:param input_name: Name of FLUKA input file
	:param start_time: Start time of calculation in datetime format
	:return: status text
	"""
	comp_name = os.uname().nodename
	os_version = os.uname().version

	lst_runs = glob.glob("fluka_*")
	runs_n = len(lst_runs)

	if runs_n < 1:
		subprocess.call("rm bomb.sh", shell=True)
		return 'Nothing is running!'

	total_handled = []
	total_left = []
	total_timepp = []
	for run in lst_runs:

		match = search_string_in_file(
			glob.glob(f"{run}/*.out")[0], 'NEXT SEEDS:')

		with open(glob.glob(f"{run}/*.out")[0], 'r') as f:
			status_line = f.readlines()[match[-1][0]-2]

		lst_status = status_line.split()
		if len(lst_status) == 6:
			pass
		else:
			return 'Cannot parse status line!'

		p_handled = int(lst_status[0])
		p_left = int(lst_status[1])
		timepp = float(lst_status[3])

		total_handled.append(p_handled)
		total_left.append(p_left)
		total_timepp.append(timepp)

	sum_handled = np.sum(total_handled)
	sum_left = np.sum(total_left)
	sum_total = sum_handled + sum_left

	progress = int((sum_handled/sum_total)*100)
	progress = 0 if progress < 1 else progress
	remain_time = np.mean(total_timepp) * np.mean(total_left)

	elapsed_time = datetime.now() - start_time
	elapsed_time = int(elapsed_time.total_seconds())

	text = f'\n\nMachine info: {os_version}\n'
	text += f'Computer name: {comp_name}\n'

	text += f'\nFLUKA input name: {input_name}\n'
	text += f'Completed:\t{progress}%\n'
	text += f'[{sum_handled}/{sum_total}] in total\n'
	text += f'[{int(sum_handled/runs_n)}/{int(sum_total/runs_n)}] per job\n\n'
	text += f'Elapsed time is {time_convert(elapsed_time)}\n'
	text += f'Mean remaining time is {time_convert(int(remain_time))}\n'
	text += f'Number of remaining jobs is {runs_n}\n\n'
	text += 'List of remaining directories:\n'
	text += f'[{", ".join(lst_runs)}]'

	return text


def time_convert(s: int):
	days, remainder = divmod(s, 60*60*24)
	hours, remainder = divmod(remainder, 60*60)
	minutes, seconds = divmod(remainder, 60)

	return \
		f'{int(days):02}d-{int(hours):02}h:{int(minutes):02}m:{int(seconds):02}s'
