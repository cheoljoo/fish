

# change user and passwd if you use it

all: work

work : work1 
work1:
	python3 fish.py

d:
	python3 fish.py --debug

m:
	python3 make_tar_ball.py
