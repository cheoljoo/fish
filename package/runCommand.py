from CiscoStyleCli import CiscoStyleCli
import sys

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(debug=False)
#print(csc.__doc__)
print("argv:",sys.argv)
x = ' '.join(sys.argv[1:])
csc.runCommand(x)

