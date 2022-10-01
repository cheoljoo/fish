

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
	python3 runCommand.py list
	python3 runCommand.py list simple
