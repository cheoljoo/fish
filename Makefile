

# change user and passwd if you use it

all:
	python3 fish.py

debug:
	python3 fish.py --debug

tcmd:
	python3 fish.py --prompt="TCMD>" --tcmd

infinite:
	python3 fish.py --infinite

list:
	python3 fish.py list

cpu:
	python3 cpu.py

modified-file:
	python3 make_tar_ball.py

test-cmd: 
	python3 test.py

test-debug:
	python3 debug.py

test-tcmd:
	python3 tcmd.py

test-infinite:
	python3 infinite.py

test-runCommand:
	@echo " python3 runCommand.py list"
	python3 runCommand.py list
	@echo " "
	@echo " python3 runCommand.py list simple"
	python3 runCommand.py list simple
	@echo " "
	@echo " python3 runCommand.py src bmw_icon_nad_release"
	python3 runCommand.py src bmw_icon_nad_release 

test-tcmd2:
	@echo " python3 tcmd2.py list"
	python3 tcmd2.py list
	@echo " ===="
	@echo " python3 tcmd2.py list simple"
	python3 tcmd2.py list simple
	@echo " ===="
	@echo " python3 tcmd2.py src bmw_icon_nad_release"
	python3 tcmd2.py src bmw_icon_nad_release 

test-tcmd3:
	@echo " python3 tcmd3.py"
	python3 tcmd3.py

doc:
	@echo "python3 help.py > CiscoStyleCli.help.txt"
	python3 help.py > CiscoStyleCli.help.txt
