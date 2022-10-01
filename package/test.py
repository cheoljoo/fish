from CiscoStyleCli import CiscoStyleCli

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli()

# make new rule
remoteCmd = {}
gethostCmd = csc.addCmd(remoteCmd,'gethost','command',"", "gethost help")
tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",additionalDict={'0':'tiger','1':'animal'})
tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",additionalDict={'0':'tiger','1':'animal'},additionalList=['list1','list2'])
tmp = csc.addCmd(gethostCmd,'choose2','command',"", "choose type2",additionalDict={'0':'tiger','1':'animal'})
tmp = csc.addArgument(tmp,'target',['cheetah','tiger','fish','turtle','tigiris'],"returnable", "type from the list",additionalList=['list1','list2'])
tmp = csc.addCmd(gethostCmd,'choose3','command',"", "choose type3",additionalDict={'0':'tiger','1':'animal'})
tmp = csc.addArgument(tmp,'shoot',{'0':'car','1':'tiger','2':'telematics'},"returnable", "type key from the dictionary")

# set new rule
csc.setCliRule(remoteCmd)

print(csc.__doc__)
csc.run()

