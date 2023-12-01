#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Look at README.md for info

import os
import shutil
import subprocess
import argparse
# from pprint import pprint

import time
from datetime import datetime

import functions  # all functionality here

from settings import PATH_TO_CUSTOM


# ------------------------------------------------------------------------------
def get_args():
	"""
	Get command-line arguments
	"""
	descrp = 'Spawn Execute and Notify (SEN) tool for FLUKA 4 input files'
	descrp += ' (cli edition)'
	parser = argparse.ArgumentParser(
		description=descrp,
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	parser.add_argument(
		'input',
		metavar='example.inp',
		help='FLUKA input file')

	parser.add_argument(
		'-e',
		'--exe',
		help=f'Custom executable from {PATH_TO_CUSTOM} directory',
		metavar='exe',
		type=str,
		default='flukadpm')

	parser.add_argument(
		'-cn',
		'--copyn',
		help='Number of input files to spawn and run',
		metavar='copyn',
		type=int,
		default=1)

	parser.add_argument(
		'-sn',
		'--skipn',
		help='Number of input files to skip',
		metavar='skipn',
		type=int,
		default=0)

	parser.add_argument(
		'-nb',
		'--notifybot',
		help='Use telegram bot for notifications',
		action='store_true')

	parser.add_argument(
		'-t',
		'--token',
		help='Token for telegram bot',
		metavar='token',
		type=str,
		default=None)

	parser.add_argument(
		'-nm',
		'--notifymail',
		help='Use email noytifications',
		action='store_true')

	parser.add_argument(
		'-p',
		'--password',
		help='Provide password for email notification option',
		metavar='password',
		type=str,
		default=None)

	parser.add_argument(
		'-nh',
		'--nohup',
		help='No information while execution',
		action='store_true')

	args = parser.parse_args()

	# Check if input file exists, rise error if not
	if os.path.isfile(args.input):
		if not args.nohup:
			print(f'Input file "{args.input}" exists!')
	else:
		parser.error(f'Input file "{args.input}" does not exist!')

	# Check for custom executable existence
	if args.exe == 'flukadpm':
		pass
	elif args.exe != 'flukadpm' and os.path.isfile(f'{PATH_TO_CUSTOM}/{args.exe}'):
		if not args.nohup:
			print(f'Custom executable file "{args.exe}" exists!')
	else:
		parser.error(f'Custom executable file "{args.exe}" does not exist!')

	# Check numbers
	if args.copyn < 1:
		parser.error(f'Number of input files to spawn must be greater than 0!')
	if args.skipn < 0:
		parser.error(f'Number of input files to skip must be non negative!')

	# Rise error if two options are requested
	if args.notifybot and args.notifymail:
		parser.error(f'You can use only one notification option at a time!')

	# Rise error if -nb provided but no token
	if args.notifybot and args.token is None:
		parser.error(f'You must provide token for notification via telegram bot!')

	# Rise error if -nm provided but no password
	if args.notifymail and args.password is None:
		parser.error(f'You must provide password for notification via email!')

	return args


def main():

	args = get_args()  # receive args

	str_date = datetime.today().strftime("%H:%M:%S %d/%m/%Y")
	if not args.nohup:
		print('\n'+str_date)
		d = '--- Spawn Execute and Notify (SEN) tool'
		d += ' for FLUKA 4 input files ---\n'
		d += '\t\t(cli edition)\n'
		print(d)

	inp_name = args.input[:-4]
	exe = args.exe

	if exe != "flukadpm":
		if not args.nohup:
			print(f'Custom executable {PATH_TO_CUSTOM}/{exe} will be used...')
		cmd_exe = f"-e {PATH_TO_CUSTOM}/{exe}"
		command = f"{PATH_TO_CUSTOM}/{exe}"
	# elif EXE == "":  # TODO simple fluka exe
	# 	cmd_EXE = ""
	# 	command = f"{os.environ['FLUKA']}/bin/fluka"
	else:
		if not args.nohup:
			print(f'Default executable "flukadpm" will be used...')
		cmd_exe = "-d"
		command = f"{os.environ['FLUKA']}/bin/flukadpm"

	copy_n = args.copyn
	skip_n = args.skipn
	if not args.nohup:
		print(f'Number of input files to spawn = {copy_n}')
		print(f'Number of input files to skip = {skip_n}')

	save_seed = open("Random.seed", "+w")
	save_seed.write(
		f"------ Start of Run {str_date} {inp_name}.inp" +
		f" number of copies: {copy_n} ------\n\n")

	save_total_seed = open("RandomTotal.seed", "+a")
	save_total_seed.write(
		f"------ Start of Run {str_date} {inp_name}.inp" +
		f" number of copies: {copy_n} ------\n\n")

	executive = []

	print()
	i = 1 + skip_n
	while i <= (copy_n + skip_n):

		cur_name = f"{inp_name}_{i:02d}.inp"

		shutil.copy(f"{inp_name}.inp", cur_name)

		# TODO maybe better algo for seed generation
		# Seed = "".join(['0'*(10-len(str(i))), str(i)])  № ???
		# Seed = "".join([str(i), '0'*(10-len(str(i)))])  # Seems ok
		seed = f'{1234567890+i}'

		with open(cur_name) as file_in:
			text = file_in.read()

		# search for string with random seed
		random_lst = functions.search_string_in_file(
			f'{inp_name}.inp',
			'RANDOMIZ')

		for rndm in random_lst:
			initial_str = rndm[1]

			text = text.replace(
				initial_str,
				f"RANDOMIZ          1.{seed}")

		with open(cur_name, "w") as file_out:
			file_out.write(text)

		if not args.nohup:
			print(f"Seed for: {cur_name} is {seed}")
		save_seed.write(f"Seed for: {cur_name} is {seed}\n")
		save_total_seed.write(f"{seed}\n")

		executive.append(
			f"/usr/bin/nohup $FLUKA/bin/rfluka -M 1 {cmd_exe} {cur_name} &")

		i += 1

	for file in [save_seed, save_total_seed]:
		file.write(
			f"\n------ End of Run {str_date} {inp_name}.inp" +
			f" number of copies: {copy_n} ------\n\n\n")
		file.close()

	# !!!Run files!!!
	for x in range(len(executive)):
		subprocess.call(executive[x], shell=True)
	# !!!Run files!!!

	time.sleep(3)  # Need delay to get PID of processes

	size_pids, pids, max_pid = functions.get_pids(command)

	if size_pids == 1:
		if pids[0] == 0:
			exit("Something went wrong! Check your input file correctness!")
		else:
			pass

	if not args.nohup:
		print(f"Number of processes in run is: {size_pids}\n")
		for i in pids:
			print(i)

	functions.create_bomb()  # create script to stop all jobs

	if args.notifymail:

		functions.send_mail(pids, size_pids, f'{inp_name}.inp', args.password)

		while not functions.check_pids_state(pids, size_pids):  # while False
			time.sleep(600)

		functions.send_mail(
			pids, size_pids, f'{inp_name}.inp', args.password, m_type='finish')

		subprocess.call('rm bomb.sh', shell=True)

	exit('\n--- Made by GN ---\n---- Goodbye! ----\n')


# --------------------------------------------------
if __name__ == '__main__':
	main()
