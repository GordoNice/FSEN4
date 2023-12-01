#!/usr/bin/env python3

import subprocess
from subprocess import PIPE
import glob
import os

# from time import sleep
import argparse

# from functions import file_exists
from natsort import natsorted as ns
# from pprint import pprint


# ------------------------------------------------------------------------------
def get_args():
	"""
	Get command-line arguments
	"""
	descrp = 'Tool for FLUKA output fort files processing'
	parser = argparse.ArgumentParser(
		description=descrp,
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	parser.add_argument(
		'input',
		metavar='example.inp',
		help='FLUKA input file name (for result name)')

	parser.add_argument(
		'-fp',
		'--fortpath',
		help=f'Path to the directory with FLUKA fort files',
		metavar='path_to_fort',
		type=str,
		default='autores')

	try:
		parser.add_argument(
			'-bp',
			'--binpath',
			help=f'Path to the bin FLUKA directory with tools for processing',
			metavar='path_to_bin',
			type=str,
			default=f'{os.environ["FLUKA"]}/bin')
	except KeyError:
		info = 'Please export path to FLUKA:'
		info += '\n"export FLUKA=~/path_to_fluka" in .bashrc'
		exit(info)

	parser.add_argument(
		'-trk',
		'--usrtrack',
		help='Units of output FLUKA fort files with usrtrack type scoring',
		metavar='usrtrack',
		type=int,
		nargs='+',
		default=None)

	parser.add_argument(
		'-yie',
		'--usryield',
		help='Units of output FLUKA fort files with usryield type scoring',
		metavar='usryield',
		type=int,
		nargs='+',
		default=None)

	# TODO USRBDX and RESNUCLEi scorings
	# TODO maybe refactor code
	parser.add_argument(
		'-dtc',
		'--detect',
		help='Process DETECT scoring files (*.17 fort files)',
		action='store_true')

	parser.add_argument(
		'-bnn',
		'--usrbin',
		help='Units of output FLUKA fort files with usrbin type scoring',
		metavar='usrbin',
		type=int,
		nargs='+',
		default=None)

	parser.add_argument(
		'-rnc',
		'--rnc',
		help='Units of output FLUKA fort files with resnuclei type scoring',
		metavar='rnc',
		type=int,
		nargs='+',
		default=None)

	# TODO noprint version
	# parser.add_argument(
	# 	'-nh',
	# 	'--nohup',
	# 	help='No information while execution',
	# 	action='store_true')

	args = parser.parse_args()

	# If no args except input file
	if args.usrtrack is None\
			and args.usryield is None and args.usrbin is None and args.rnc is None:
		if not args.detect:
			parser.error(f'Please provide at least one unit!')

	args.input = args.input.split(".")[0]  # Get rid of extension

	# Check if directory with FLUKA bins exists, rise error if not
	if not os.path.isdir(args.binpath):
		parser.error(f'Directory "{args.binpath}" does not exist!')
	else:
		print(f'Directory {args.binpath} will be used for processing...')

	for score in ['ustsuw', 'usysuw', 'usbsuw', 'detsuw', 'usrsuw']:
		if not os.path.isfile(f'{args.binpath}/{score}'):
			parser.error(
				f'Tool "{score}" does not exist under {args.binpath}!')

	# Check if directory with FLUKA fort files exists, rise error if not
	if not os.path.isdir(args.fortpath):
		parser.error(f'Directory "{args.fortpath}" does not exist!')
	else:
		print(
			f'FLUKA fort files from {args.fortpath} directory will be used for processing...')

	for arg in [args.usrtrack, args.usryield, args.usrbin, args.rnc]:
		if arg is not None:
			arg.sort()  # sort units
			for unit in arg:
				if 20 < unit < 100:
					if get_pathnames(f'{args.fortpath}/*.{unit}'):
						pass
					else:
						parser.error(
							f'Unit number {unit} is not in the specified folder!')
				else:
					parser.error(
						f'Some of provided units are not correct! (20 < unit < 100)')

	return args


def get_pathnames(path: str):
	"""
	Find all pathnames matching a specified pattern, return False if no matches

	:param path: pattern
	:return: list or False
	"""
	paths = ns(glob.glob(path), key=lambda y: y.lower())
	if paths:
		return paths
	else:
		return False


# TODO process fort files from FLUKA
def ProcessFLUKA(
		inp: str,
		binpath: str, fortpath: str, unit: int, score: str, noprint=True):

	ext = {
		'ustsuw': 'trk',
		'usysuw': 'yie',
		'usbsuw': 'bnn',
		'detsuw': 'dtc',
		'usrsuw': 'rnc'
	}

	paths = get_pathnames(f'{fortpath}/*.{unit}')
	paths.append('')  # need to press enter
	paths.append(f'{inp}_{unit}.{ext[score]}')  # need to provide out file name

	cmd = f'{binpath}/{score}'
	print(f'Data for unit {unit} is merging...')
	result = subprocess.run(
		[cmd], stderr=PIPE, stdout=PIPE, input="\n".join(paths).encode())

	# print("stdout:", result.stdout)
	if not result.stderr:
		print(f'File {inp}_{unit}.{ext[score]} is created\n')
	elif result.stderr:
		print(result.stderr)
		print('Something went wrong! Please check units and their scoring types!')


def main():

	args = get_args()  # receive args
	print()

	score = {
		'ustsuw': args.usrtrack,
		'usysuw': args.usryield,
		'usbsuw': args.usrbin,
		'usrsuw': args.rnc
	}

	for item in score.keys():
		if score[item] is not None:
			for unit in score[item]:
				ProcessFLUKA(
					args.input, args.binpath, args.fortpath, unit, item)

	# Special treat for the DETECT scoring
	if args.detect:
		ProcessFLUKA(
					args.input, args.binpath, args.fortpath, 17, 'detsuw')

if __name__ == '__main__':
	main()
