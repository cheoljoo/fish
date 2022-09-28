

# change user and passwd if you use it

all: work

work : work1 
work1:
	python3 fish.py

d:
	python3 fish.py --debug

tcmd:
	python3 fish.py --prompt="TCMD>" --tcmd

infinite:
	python3 fish.py --infinite
