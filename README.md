**FSEN4 tools**
==============

Python tools for **F**LUKA input files with **S**pawn, **E**xecute and **N**otify features (FSEN). 
Allows to spawn [FLUKA](https://fluka.cern/) input files, execute them and notify by e-mail (or via telegram bot) about run
state. After completion have a structure like it was done using [Flair](http://flair.web.cern.ch/flair/), so user can easily process data using Flair.

Made with Python 3

Author: [_Gordeev Ivan <GN\>_](https://www.researchgate.net/profile/Ivan-Gordeev) (gordeev@jinr.ru), Dubna, JINR, 2021

Prerequisites
--------------

Python 3 (tested on 3.6 and 3.7) and dependencies: **numpy** and **pyTelegramBotAPI** (for telegram notifications).

One need to add this line in _.bashrc_ file of home directory:

> export FLUKA=~/path_to_bin_directory

where _path\_to\_bin\_directory_ is the path to FLUKA _bin_ folder. Another option is to execute this command in terminal directly every time just before script launching.

Also, by default, script will search custom user executable under _PATH\_TO\_CUSTOM_ (look at the _settings.py_ file).
If one has custom executables in another directory, _PATH\_TO\_CUSTOM_ must be changed accordingly.

Info for notify option
----------------------

*FSEN4cli* tool supports 2 types of notification:

1. Via email
2. Via telegram bot

You need to change _settings.py_ file according to your settings, to use first and second feature. 

For telegram bot one need to create his own [bot](https://core.telegram.org/bots) and change _USER\_ID_ and _USERNAME_ accordingly. This gives permission to sent commands to only one user with specific _USER\_ID_ and _USERNAME_.

There are 3 commands for telegram bot available:

> /help

This one shows available commands.

> /status

This one sent status about current run.

> /bomb

This one stops calculations by executing _bomb.sh_ script (generates _fluka.stop_ files in _fluka\_*_ directories)

Usage examples
--------------

### FSEN4cli tool

FSEN4cli tool executes FLUKA input files via cli and notifies about run status (optional).

To show help in command line type:

> ./FSEN4cli.py -h

Default run, without any arguments (1 positional argument required):

> ./FSEN4cli.py example.inp

This will execute 1 copy of given input file without any notifications.

Simple run with 6 parallel jobs:

> ./FSEN4cli.py example.inp -cn 6

This will launch 6 copy of given input file without any notifications.

Simple run with 4 parallel jobs, skipping previous 6:

> ./FSEN4cli.py example.inp -cn 4 -sn 6

This will launch 6 copy of given input file without any notifications and first 6 files will be skipped (to avoid runs with the same seeds).

Run with 6 parallel jobs with notification via email (make sure to provide password and necessary settings in _settings.py_ file):

> ./FSEN4cli.py example.inp -cn 6 -nm -p '*\*\*password\*\*\*'

Run with 6 parallel jobs with notification via telegram bot (make sure to provide API token for your telegram bot):

> ./FSEN4cli.py example.inp -cn 6 -nb -t '\*\*\*token\*\*\*'

**IMPORTANT**: for notifications, one need to be sure that script will last in background processes, to run script in background do:

> nohup ./FSEN4cli.py example.inp -cn 6 -nb -t '\*\*\*token\*\*\*' &

nohup command will add all output to _nohup.out_ file and _&_ sign will run script in background. Also, one could press "CTRL + Z" and do: bg (to force program run in background). After that terminal can be closed.

Otherwise, one should not close the terminal while the script is running.

### bomb feature

During every execution, script creates so-called _bomb.sh_ shell script. Execution of this script creates _fluka.stop_ files in every 'fluka_*' directory this way, jobs can be finished correctly earlier.

### automate tool

This tool automates new launches with _FSEN4cli_ tool.

For example, if one started N parallel jobs of FLUKA via _FSEN4cli_ tool, and he wants to improve statistics by running more jobs just after these N jobs will be done, this tool will be helpful.

To show usage help in command line type:

> ./automate.py -h

Suppose, 6 jobs are already running via _FSEN4cli_ tool. If one wants to perform 5 more launches after that with 6 parallel jobs:

> nohup ./automate.py -sn 6 -cn 6 -bn 5 example.inp &

Where '-sn 6' tells skipping 6 jobs (which are handled by _FSEN4cli_ tool), '-cn 6' - number of parallel jobs in the next batches, '-bn 5' - number of batches. One need to pay attention, that this should be executed in background.

All results will be automatically saved in 'autores' directory.

### harvest tool

To process all the results from the terminal:

> ./harvest.py example.inp -trk 21 -yie 22

Here we suppose that all our *fort* files are in the 'autores' folder. We have one usrtrack scorer on the unit 21 and one usryield scorer on the unit 22.

**Not all the scorers are currently available!**
Use --help to list all the options.

**IMPORTANT**: All the tools should be in the same directory! But it can be called from any path.
