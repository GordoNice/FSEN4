#!/usr/bin/env python3

import subprocess
import glob
import os

from time import sleep
import argparse

from functions import dir_exists, file_exists
from settings import PATH_TO_CUSTOM


# ------------------------------------------------------------------------------
def get_args():
	"""
	Get command-line arguments
	"""
	descrp = 'Tool for automatic call of FSEN4 tool'
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
		help='Number of input files to skip at first batch',
		metavar='skipn',
		type=int,
		default=0)

	parser.add_argument(
		'-bn',
		'--batchn',
		help='Number of batches to generate',
		metavar='batchn',
		type=int,
		default=1)

	parser.add_argument(
		'-nh',
		'--nohup',
		help='No information while execution',
		action='store_true')

	args = parser.parse_args()

	# Check if input file exists, rise error if not
	if not os.path.isfile(args.input):
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
	if args.batchn < 1:
		parser.error(f'Number of batches to generate must be greater than 0!')

	return args


def check_state():
	"""
	Returns current state of FLUKA runs if no fluka_* directories then False

	:return: true or False
	:rtype: bool
	"""
	if glob.glob("fluka_*"):
		return True
	else:
		return False


def main():

	args = get_args()  # receive args
	dir_exists(
		'autores', mkdir=True, noprint=not args.nohup)  # Check directory for results

	b = 1
	while True:
		if args.batchn == 0 and not check_state():
			# Harvest results from last batch
			subprocess.call('mv *fort* autores', shell=True)
			exit()

		if check_state():
			sleep(60)
		elif not check_state() and args.batchn > 0:
			if b == 1:
				skip = args.skipn
			else:
				skip = args.skipn + args.copyn*(b-1)

			# Harvest results from previous batch
			subprocess.call('mv *fort* autores', shell=True)

			# Execute new script
			# Script should be in the same directory with FSEN4cli!
			# maybe TODO better
			path_fsen = \
				f'{"/".join(os.path.realpath(__file__).split("/")[:-1])}/FSEN4cli.py'
			if file_exists(path_fsen, noprint=not args.nohup):
				cmd = f'nohup {path_fsen}'
				cmd += f' -e {args.exe} -cn {args.copyn} -sn {skip} -nh {args.input} &'
				subprocess.call(cmd, shell=True)
			else:
				exit('Cannot locate FSEN4cli.py!')

			args.batchn -= 1
			b += 1
			sleep(60)
		else:
			sleep(60)


if __name__ == '__main__':
	main()
