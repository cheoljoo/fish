from CiscoStyleCli import CiscoStyleCli

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(infinite=True)
print(csc.__doc__)
csc.run()

