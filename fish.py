# import requests
# import json
# import sys
# import time
# from jira import JIRA
# import jira.client
import datetime
import re
import argparse
# from collections import defaultdict
import os
import glob
import csv
print(os.sys.path)
#from atlassian import Jira

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

jira_rest_url = "http://vlm.lge.com/issue/rest/api/latest/"
issue_url = jira_rest_url + "issue/"
search_url = jira_rest_url + "search/"
tracker_url = jira_rest_url + "project/"
fieldList_url = jira_rest_url + "field/"
jsonHeaders = {'Content-Type': 'application/json'}

# - 특정 조건 : 그 사람 (최근 일주일)
#- 모든 ticket중에서 "그 사람"이 comments를 남긴 내용중에 tiger_weekly_report 이 comments의 첫줄에 적은 ticket들에 적은 comments를 출력한다.
#- status 상관없고, 

dateRe = re.compile('^\s*(?P<date>(?P<year>20[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+))')
intRe = re.compile('^\s*(?P<ans>[0-9\-\+]+)')
floatRe = re.compile('^\s*(?P<ans>[0-9\-\+\.]+)')
wordRe = re.compile('^\s*(?P<ans>[^ \n]+)')

class CiscoStyleCli:
    """ 
    This Class get the string based on cisco style command line interface.
    c = CiscoStyleCli(...)
    lineStr = c.getStr()
    wordStr = c.getWord()
    ch = c.getCh()
    bool = c.setCliRule()
    """
    def __init__(self,rule=None,debug=False):
        """ 
        초기화 self.remoteCmd
        """
        self.debug = debug
        self.c = ''
        if rule and os.path.isfile(rule):
            remoteCmd = {}
            f = open(rule, 'r')
            lines = f.readlines()
            for line in lines:
                # print(line.strip())
                exec(line.strip())
            f.close()
            print("__init__():remoteCmd:",remoteCmd)
            self.remoteCmd = remoteCmd
            return
        self.funcTable = {}
        self.remoteCmd = {}
        # register CL cheoljoo.lee lotto645.com akstp! ./desktop/image cheoljoo.lee@gmail.com [return]
        registerCmd = self.addCmd(self.remoteCmd,'register','command',"","registration command (id , host , passwd , etc)")
        tmp = self.addArgument(registerCmd,'name','str' , "", "system nickname ")
        tmp = self.addArgument(tmp,'id','str',"", "login id")
        tmp = self.addArgument(tmp,'host','str',"", "hostname")
        tmp = self.addArgument(tmp,'passwd','str',"", "password")
        tmp = self.addArgument(tmp,'directory','str',"", "output directory")
        tmp = self.addArgument(tmp,'email','str',"", "email address")
        enableCmd = self.addCmd(self.remoteCmd,'enable','command',"", "change to enable status : you can use this system")
        tmp = self.addArgument(enableCmd,'choose','int',"returnable", "choose number from the list","listTable")
        disableCmd = self.addCmd(self.remoteCmd,'disable','command',"", "change to disable status : you can not use this system")
        tmp = self.addArgument(disableCmd,'choose','int',"", "choose number from the list")
        # list [return] : no arguments
        listCmd = self.addCmd(self.remoteCmd,'list','command',"returnable", "show system list")
        # cmd "ls -al \"*.sh\" ; ls "
        runCmd = self.addCmd(self.remoteCmd,'run','command',"", "execute command with quoted string")
        tmp = self.addArgument(runCmd,'run','quotestr',"returnable", "execution string ex) \"cd HOME; ls -al\"")
        # test [return]
        # test sldd hmi 4 5 [return]
        testCmd = self.addCmd(self.remoteCmd,'test','command',"", "test command example")
        twoskipCmd = self.addCmd(testCmd ,'twoskip','command',"", "twoskip follows test")
        threeCmd = self.addCmd(twoskipCmd ,'three','command',"", "three follows test")
        slddCmd = self.addCmd(testCmd ,'sldd','command',"", "sldd follows test")
        stopCmd = self.addCmd(slddCmd ,'stop','command',"returnable", "stop follows sldd")
        helpCmd = self.addCmd(slddCmd ,'help','command',"returnable", "help follows sldd")
        hmiCmd = self.addCmd(slddCmd ,'hmi','command',"", "hmi follows sldd")
        tmp = self.addArgument(hmiCmd,'first','int',"", "need to input with first integer")
        tmp = self.addArgument(tmp,'second','int',"", "need to input with second integer")
        quitCmd = self.addCmd(self.remoteCmd ,'quit','command',"returnable", "exit")
        tmp = self.addCmd(quitCmd ,'','command',"", "exit","quit")
        
        if self.debug :
            print("remoteCmd:",self.remoteCmd)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
        
    def addCmd(self,root,command,type,returnable,desc,funcname=""):
        """ 
        root['cmd'][command]['type'] = type
        root['cmd'][command]['cmd'] = {} # if you need more command
        return root['cmd'][command]
        """
        if 'cmd' not in root:
            root['cmd'] = {}
        root['cmd'][command] = {}
        if type:
            root['cmd'][command]['type'] = type
        else :
            root['cmd'][command]['type'] = 'command'
        root['cmd'][command]['returnable'] = returnable
        root['cmd'][command]['desc'] = desc
        if funcname :
            root['cmd'][command]['funcname'] = funcname
        return root['cmd'][command]
    def addArgument(self,root,name,type,returnable,desc,funcname=""):
        """ 
        root['cmd'][name]['type'] = 'argument'
        root['cmd'][name]['argument-type'] = type
        root['cmd'][name]['cmd'] = {} # if you need more command
        """
        if 'cmd' not in root:
            root['cmd'] = {}
        root['cmd'][name] = {}
        root['cmd'][name]['type'] = 'argument'
        root['cmd'][name]['argument-type'] = type
        root['cmd'][name]['returnable'] = returnable
        root['cmd'][name]['desc'] = desc
        # if 'arguments' not in root:
        #     root['arguments'] = []
        # root['arguments'].append({'name':name,'type':type})
        if funcname :
            root['cmd'][name]['funcname'] = funcname
        return root['cmd'][name]
    def setFunc(self,funcname,funcptr):
        self.funcTable[funcname] = funcptr
        if self.debug and funcptr != quit:
            funcptr()
        
    def setCliRule(self,rule):
        self.remoteCmd = rule
        
    def getch(self):
        """ 
        get one character without print
        """
        # https://stackoverflow.com/questions/3523174/raw-input-without-pressing-enter
        import sys, termios, tty

        fd = sys.stdin.fileno()
        orig = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)  # or tty.setraw(fd) if you prefer raw mode's behavior.
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, orig)

    def checkCmd(self,cmd):
        """ 
        check whether this cmd is right
        return the location from rootCmd following cmd  for guiding current and next arguments
        """
        retValue = {}
        retCmdList = []
        words = cmd.split(' ')
        if cmd == "":
            words = []
            if 'cmd' in self.remoteCmd:
                cmdRoot = self.remoteCmd['cmd']
                print(flush=True)
                print("recommend: ",end="",flush=True)
                for s in cmdRoot.keys():
                    print(s," ",end="",flush=True)
                print(flush=True)
        root = self.remoteCmd
        if self.debug:
            print("checkCmd:words:",words)
        lastWord = ""
        newCmd = ""
        while len(words):
            v = words.pop(0)
            if self.debug:
                print("root:",root)
                print("words:",words)
            if v == '':
                if self.debug:
                    print("v is empty")
                # newCmd += " "
                lastWord = ""
                print(flush=True)
                print(flush=True)
                print(flush=True)
                matchedCount = 0
                if ('returnable' in root and root['returnable'] == 'returnable') or 'cmd' not in root:
                    matchedCount += 1
                    print('recommend: <CR>',flush=True)
                matchedCommand = ""
                if 'cmd' in root:
                    for s in root['cmd'].keys():
                        matchedCount += 1
                        cmdRoot = root['cmd']
                        t = 'argument'
                        if cmdRoot[s]['type'] != 'argument':
                            t = 'command'
                            matchedCommand = s
                        returnable = ""
                        if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                            returnable = '[returnable]'
                        print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] , returnable , flush=True)
                        if 'funcname' in cmdRoot[s] and cmdRoot[s]['funcname'] in self.funcTable :
                            t = cmdRoot[s]['funcname']
                            if self.debug:
                                print("funcname:",t)
                                print(self.funcTable)
                            self.funcTable[t]()
                if self.debug:
                    print("matchedCount:",matchedCount)
                    print("matchedCommand:",matchedCommand)
                if matchedCount == 1 and matchedCommand != "":
                    newCmd = self.cmd + matchedCommand + " "
                    print()
                    print("press the space bar")
                break
            lastWord = v
            if 'cmd' in root:
                cmdRoot = root['cmd']
                if self.debug:
                    print("v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
                focus = ""
                matched = []
                for crk, crv in cmdRoot.items():
                    if cmdRoot[crk]['type'] == 'argument':
                        if self.debug :
                            print("argument cmd :",v , "type:" , cmdRoot[crk]['type'], "ar type:" , cmdRoot[crk]['argument-type'] , "next keys:", cmdRoot.keys())
                        focus = crk
                    elif v == crk:
                        if self.debug :
                            print("exact matched cmd key:",crk)
                        focus = crk
                    elif v == crk[:len(v)] :
                        if self.debug :
                            print("matched cmd key:",crk)
                        matched.append(crk)
                if focus:
                    newCmd += v + " "
                    root = cmdRoot[focus]
                    if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                        retValue[focus] = v
                    else:
                        retCmdList.append(v)
                else :
                    if len(matched) == 0:
                        pass
                    elif len(matched) == 1:
                        focus = matched[0]
                        newCmd += matched[0] + " "
                        root = cmdRoot[matched[0]]
                        if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                            retValue[focus] = v
                        else:
                            retCmdList.append(v)
                        self.cmd = newCmd
                    else:
                        newCmd += v
                        print()
                        print("recommend list: ",end="",flush=True)
                        for s in matched:
                            print(s," ",end="",flush=True)
                        print()
                        for s in matched:
                            t = 'argument'
                            if cmdRoot[s]['type'] != 'argument':
                                t = 'command'
                            returnable = ""
                            if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                                returnable = '[returnable]'
                            print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                        break
        if self.debug :
            print("newCmd:/",newCmd,"/ root: ",root,sep="")
        self.cmd = newCmd
        # check auto completion for following order
        # while True:
        #     if 'cmd' in root:
        #         cmdRoot = root['cmd']
        #         # print(cmdRoot)
        #         # print(cmdRoot.keys())
        #         # print(len(cmdRoot.keys()))   
        #         t = list(cmdRoot.keys())
        #         # print(t[0])
        #         if len(t) == 1 and cmdRoot[t[0]]['type'] != 'argument' and cmdRoot[t[0]]['returnable'] != 'returnable' :
        #             self.cmd += t[0] + ' '
        #             retCmdList.append(t[0])
        #             # lastWord = t[0]
        #             root = cmdRoot[t[0]]
        #         else :
        #             break
        #     else :
        #         break
        retValue['__cmd__'] = retCmdList
        return (root,lastWord,retValue)
            
    def run(self):
        """ 
        main part of cisco command line interface
        get string as input
        """
        print("the simple distributed compile environment remotely",flush=True)

        print('input:',end='',flush=True)
        self.cmd = ""
        quoteFlag = False
        while True:
            root , lastCmd , retValue = self.checkCmd(self.cmd)
            if self.debug:
                print('lastCmd:', lastCmd , 'retValue:',retValue)
            if self.c == '\n':
                if self.debug:
                    print('RETURN',flush=True)
                    print("root:",root)
                    print("cmd:",self.cmd.replace('\t',' '))
                retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                if ('returnable' in root and root['returnable'] == 'returnable') or 'cmd' not in root:
                    return retValue
            # get a word
            for i in range(len(lastCmd)):
                if lastCmd[i] == '"' and i != 0 and lastCmd[i-1] != "\\":
                    if quoteFlag == False:
                        quoteFlag = True
                    else :
                        quoteFlag = False
            print("\ninput:",self.cmd.replace("\t"," "),sep="",end="",flush=True)
            while True:
                if self.debug:
                    print(flush=True)
                    print("input:/",self.cmd.replace("\t"," "),"/",self.cmd.replace("\t"," "),sep="",end="",flush=True)
                c = self.getch()
                self.c = c
                
                # print(c,ord(c))
                if ord(c) == 8 or ord(c) == 127 :  # backspace 8:linux terminal ,  127:vscode terminal
                    if len(self.cmd) > 0:
                        print('\b \b',end="",flush=True)
                        if self.cmd[-1] == '"':
                            if quoteFlag == False:
                                quoteFlag = True
                            else :
                                quoteFlag = False                            
                        self.cmd = self.cmd[:-1]
                    continue
                if c == '"' and self.cmd and self.cmd[-1] != "\\":
                    if quoteFlag == False:
                        quoteFlag = True
                    else :
                        quoteFlag = False
                if quoteFlag == True:
                    if c == '\n':
                        continue
                    if c == ' ':
                        c = '\t'
                    self.cmd += c
                    print(c.replace("\t",' '),end="",flush=True)
                else : 
                    if c == '\t' or c == '\n':
                        c = ' '
                    if c == ' ' and self.cmd and self.cmd[-1] != ' ':
                        self.cmd += c
                    if c == ' ' :
                        break
                    if c == '\n':
                        if self.debug:
                            print(c, 'RETURN',flush=True)
                            print("root:",root)
                            print("cmd:",self.cmd.replace('\t',' '))
                        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                        if ('returnable' in root and root['returnable'] == 'returnable') or 'cmd' not in root:
                            return retValue
                    else :
                        print(c,end="",flush=True)
                        self.cmd += c
                        
        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
        return retValue

    def traverseFD(self,f,vv,start:str):
        # print(start," ",file=f)
        if isinstance(vv, dict):
            print(start ,  " = {}", sep="", file=f)
            for k, v in vv.items():
                self.traverseFD(f,v,start + "['" + k  + "']")
        elif isinstance(vv, (list, tuple)):
            for i, x in enumerate(vv):
                self.traverseFD(f,x,start + "[list:" + str(i) + "]" )
        else :
            print(start ,  " = '''", vv , "'''", sep="", file=f)

    def traverseFile(self,filename:str,v,start:str,att):
        with open(filename, att, encoding='utf-8', errors='ignore') as f:
            self.traverseFD(f,v,start)

class RemoteCommand :
    """ 
    This Class choose and execute of remote command.
    Manage the DB (CSV)
    """
    def __init__(self,csvfile="",debug=False):
        if csvfile:
            self.csvfile = csvfile
        self.debug = debug
        self.fieldnames = ['name','id','host','passwd','directory','email','enable']
        self.list = []
        if csvfile and os.path.exists(csvfile):
            with open(csvfile, "r" , newline='') as csvfd:
                reader = csv.DictReader(csvfd)
                for row in reader:
                    self.list.append(row)
                if len(self.fieldnames) < len(list(row.keys())):
                    self.fieldnames = list(row.keys())

    def appendData(self,rv):
        row = {}
        for f in self.fieldnames:
            row[f] = ""
            if f in rv:
                row[f] = rv[f]
        self.list.append(row)
    def dataWrite(self):
        with open('fish.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in self.list:
                writer.writerow(row)
        
    def run(self):
        pass

    def listTable(self):
        print()
        cnt = 0
        for row in self.list:
            print(cnt , ":" , row)
            cnt += 1
        print()

if (__name__ == "__main__"):

    parser = argparse.ArgumentParser(
        prog='fish.py',
        description= 'FISH (Funny sImple distributed system with rSH through sSH)',
        epilog='''down & compile in remote server'''
    )

    parser.add_argument("-t", "--test", action="store_true",default=False,help='show the command but not run it for test & debug')
    parser.add_argument("-d", "--debug", action="store_true",default=False,help='show the command but not run it for test & debug')
    parser.add_argument(
        '--csvfile',
        metavar="<csvfile>",
        type=str,
        default="fish.csv",
        help='csv file with field -  name,login_id,passwd,host,directory,email')
    parser.add_argument(
        '--rulefile',
        metavar="<rulefile>",
        type=str,
        default="rule.py",
        help='python data file to make a command line rule')

    args = parser.parse_args()

    csc = CiscoStyleCli(rule = args.rulefile , debug = args.debug)
    rc = RemoteCommand(csvfile=args.csvfile,debug = args.debug)
    csc.setFunc("listTable",rc.listTable)
    csc.setFunc("quit",quit)
    while True:
        retValue = csc.run()
        if "quit" == retValue['__return__'][:len('quit')]:
            quit()
        elif "register" == retValue['__return__'][:len('register')]:
            rc.appendData(retValue)
            rc.dataWrite()
        print("cmd=[",retValue['__return__'],"]",sep="")
        print("retValue:",retValue)
    
    # import ruleData
    # print(ruleData.remoteCmd)
    


