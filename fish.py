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
import io
import time
import subprocess
import os
import glob
import csv
import sys
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
cpusRe = re.compile('^\s*cpu count:\s*(?P<ans>[0-9\-\+\.]+)')
cpuUsageRe = re.compile('^\s*CPU usage:\s*(?P<ans>[0-9\-\+\.]+)')
dfRe = re.compile('^\s*/dev/\S+\s+\S+\s+\S+\s+(?P<ans>[0-9\-\+\.]+[MGT]+)')



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
        # self.funcTable = {}
        self.remoteCmd = {}
        # register CL cheoljoo.lee lotto645.com akstp! ./desktop/image cheoljoo.lee@gmail.com [return]
        registerCmd = self.addCmd(self.remoteCmd,'register','command',"","registration command (id , host , passwd , etc)")
        tmp = self.addArgument(registerCmd,'name','str' , "", "system nickname ")
        tmp = self.addArgument(tmp,'id','str',"", "login id")
        tmp = self.addArgument(tmp,'host','str',"", "hostname")
        tmp = self.addArgument(tmp,'passwd','str',"", "password")
        tmp = self.addArgument(tmp,'directory','str',"", "output directory")
        tmp = self.addArgument(tmp,'email','str',"", "email address")
        tmp = self.addArgument(tmp,'command','str',"", "commands for site")
        quitCmd = self.addCmd(self.remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self.quit)
        # tmp = self.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.quit)
        # # enable : now i do not use it
        # enableCmd = self.addCmd(self.remoteCmd,'enable','command',"", "change to enable status : you can use this system")
        # tmp = self.addArgument(enableCmd,'choose','int',"returnable", "choose number from the list","listTable")
        # # disable : now i do not use it
        # disableCmd = self.addCmd(self.remoteCmd,'disable','command',"", "change to disable status : you can not use this system")
        # tmp = self.addArgument(disableCmd,'choose','int',"", "choose number from the list","listTable")
        # # list [return] : no arguments
        # listCmd = self.addCmd(self.remoteCmd,'list','command',"returnable", "show system list")
        # # cmd "ls -al \"*.sh\" ; ls "
        # runCmd = self.addCmd(self.remoteCmd,'run','command',"", "execute command with quoted string")
        # tmp = self.addArgument(runCmd,'run','quotestr',"returnable", "execution string ex) \"cd HOME; ls -al\"")
        # # test [return]  <- use it now to check server's status
        # testCmd = self.addCmd(self.remoteCmd,'test','command',"returnable", "test : send command ls -al for each server")
        # twoskipCmd = self.addCmd(testCmd ,'twoskip','command',"", "twoskip follows test")
        # threeCmd = self.addCmd(twoskipCmd ,'three','command',"", "three follows test")
        # # test sldd hmi 4 5 [return]
        # slddCmd = self.addCmd(testCmd ,'sldd','command',"", "sldd follows test")
        # stopCmd = self.addCmd(slddCmd ,'stop','command',"returnable", "stop follows sldd")
        # helpCmd = self.addCmd(slddCmd ,'help','command',"returnable", "help follows sldd")
        # hmiCmd = self.addCmd(slddCmd ,'hmi','command',"", "hmi follows sldd")
        # tmp = self.addArgument(hmiCmd,'first','int',"", "need to input with first integer")
        # tmp = self.addArgument(tmp,'second','int',"", "need to input with second integer")
        # # run [return]  <- use it now to check server's status
        # runCmd = self.addCmd(self.remoteCmd,'run','command',"", "run download & compile")
        # tigerDesktopCmd = self.addCmd(runCmd ,'tiger-desktop','command',"returnable", "download & compile of tiger-desktop")
        
        if self.debug :
            print("remoteCmd:",self.remoteCmd)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
        
    def addCmd(self,root,command,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,chooseList=None):
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
        if additionalDict:
            root['cmd'][command]['additionalDict'] = additionalDict
        if prefunc :
            root['cmd'][command]['prefunc'] = prefunc
        if returnfunc :
            root['cmd'][command]['returnfunc'] = returnfunc
        if chooseList :
            root['cmd'][command]['chooseList'] = chooseList
        return root['cmd'][command]
    def addArgument(self,root,name,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,chooseList=None):
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
        if additionalDict:
            root['cmd'][name]['additionalDict'] = additionalDict
        # if 'arguments' not in root:
        #     root['arguments'] = []
        # root['arguments'].append({'name':name,'type':type})
        if prefunc:
            root['cmd'][name]['prefunc'] = prefunc
        if returnfunc:
            root['cmd'][name]['returnfunc'] = returnfunc
        if chooseList:
            root['cmd'][name]['chooseList'] = chooseList
        return root['cmd'][name]
    
    # def setFunc(self,funcname,funcptr):
    #     self.funcTable[funcname] = funcptr
    #     if self.debug and funcptr != quit:
    #         funcptr()
        
    def setCliRule(self,rule):
        self.remoteCmd = rule
        if 'cmd' in self.remoteCmd and 'quit' not in self.remoteCmd['cmd']:
            quitCmd = self.addCmd(remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self.quit)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.quit)
        if 'cmd' in self.remoteCmd and 'list' not in self.remoteCmd['cmd']:
            listCmd = self.addCmd(remoteCmd ,'list','command',"returnable", "show command line interface list",returnfunc=self.list)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.list)
        if 'cmd' in self.remoteCmd and 'list-detailed' not in self.remoteCmd['cmd']:
            listDetailedCmd = self.addCmd(remoteCmd ,'list-detailed','command',"returnable", "show detailed command line interface list",returnfunc=self.listDetailed)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
    
    def quit(self,v=None):
        print("byebye!!   see you again~~   *^^*")
        quit()
    
    def list(self,v):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug:
            print("functionname:",functionNameAsString)
            print(self,v)
        self.traverseList(self.remoteCmd,"")
        for s in self.tlist:
            print(s)
        print()
    def listDetailed(self,v):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug:
            print("functionname:",functionNameAsString)
            print(self,v)
        self.traverseList(self.remoteCmd,"",detailed=True)
        for s in self.tlist:
            print(s)
        print()
    def traverseList(self,vv,start:str,detailed=False):
        # print(start," ",file=f)
        if isinstance(vv, dict):
            if 'cmd' in vv:
                v2 = vv['cmd']
                for k, v in v2.items():
                    rt = " "
                    if 'returnable' in v and v['returnable'] == 'returnable':
                        rt = ' [leaf]'
                    if self.debug:
                        print("show:",rt,k,v)
                    if detailed:
                        prefunc = ""
                        if 'prefunc' in v:
                            prefunc = " pre-func" + str(v['prefunc'])
                        returnfunc = ""
                        if 'returnfunc' in v:
                            returnfunc = " ret-func:" + str(v['returnfunc'])
                        if 'type' in v and v['type'] != 'argument': 
                            self.traverseList(v,start + " (commands) " + prefunc + k  + returnfunc + rt,detailed=True)
                        else:
                            argtype = v['argument-type']
                            self.traverseList(v,start + " (argument:" + argtype +") " + prefunc + k + returnfunc + rt,detailed=True)
                    else:
                        if 'type' in v and v['type'] != 'argument': 
                            self.traverseList(v,start + " (commands) " + k  + rt)
                        else:
                            self.traverseList(v,start + " (argument) " + k  + rt)
            else:
                if self.debug:
                    print("start:",start)
                self.tlist.append(start)
        # else :
        #     print(start ,  " = '''", vv , "'''", sep="", file=f)

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

    def copyAdditionalDict(self,_from,_to):
        if 'additionalDict' in _from:
            for adk,adv in _from['additionalDict'].items():
                if '__additionalDict__' not in _to:
                    _to['__additionalDict__'] = {}
                _to['__additionalDict__'][adk] = adv
    def checkCmd(self,cmd):
        """ 
        check whether this cmd is right
        return the location from rootCmd following cmd  for guiding current and next arguments
        """
        retValue = {}
        retCmdList = []
        retLiteralCmdList = []
        words = cmd.split(' ')
        # print("key:/",self.c,"/",sep="")
        if cmd == "" and (self.c == ' ' or self.c == '\t'):
            words = []
            if 'cmd' in self.remoteCmd:
                cmdRoot = self.remoteCmd['cmd']
                print(flush=True)
                print("recommend: ",end="",flush=True)
                for s in cmdRoot.keys():
                    print(s," ",end="",flush=True)
                print(flush=True)
                for s in cmdRoot.keys():
                    t = 'argument'
                    if cmdRoot[s]['type'] != 'argument':
                        t = 'command'
                    returnable = ""
                    if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                        returnable = '[returnable]'
                    print('    recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] , returnable , flush=True)
        # print("kkk")
        root = self.remoteCmd
        if self.debug:
            print("checkCmd:words:",words)
        lastWord = ""
        newCmd = ""
        while len(words):
            v = words.pop(0)
            if self.debug:
                print("get word : v :",v)
                print("root:",root)
                print("words:",words)
                print("retValue:",retValue)
            if v == '':
                if self.debug:
                    print("v is empty")
                    print("root:",root)
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
                        elif 'chooseList' in cmdRoot[s]:
                            for ci,cv in enumerate(cmdRoot[s]['chooseList']):
                                print("ci:",ci,cv)
                        returnable = ""
                        if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                            returnable = '[returnable]'
                        self.copyAdditionalDict(cmdRoot[s],retValue)
                        print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] , returnable , flush=True)
                        if 'prefunc' in cmdRoot[s] and cmdRoot[s]['prefunc'] :
                            t = cmdRoot[s]['prefunc']
                            if self.debug:
                                print("prefunc",t)
                                print("funcname:",t)
                                # print(self.funcTable)
                                print("retValue:",retValue)
                            t(retValue)
                if self.debug:
                    print("matchedCount:",matchedCount)
                    print("matchedCommand:",matchedCommand)
                if matchedCount == 1 and matchedCommand != "":
                    newCmd = self.cmd + matchedCommand + " "
                    cmdRoot = root['cmd']
                    #print()
                    #print("empty root:",root)
                    #print("empty cmdRoot:",cmdRoot)
                    #print("empty cmdRoot[]:",matchedCommand,cmdRoot[matchedCommand])
                    #root = cmdRoot[matchedCommand]
                    #cmdRoot = root['cmd']
                    #print("empty root:",root)
                    #print("empty cmdRoot:",cmdRoot)
                    if 'prefunc' in cmdRoot and cmdRoot['prefunc'] :
                        t = cmdRoot['prefunc']
                        if self.debug:
                            print("prefunc",t)
                            print("funcname:",t)
                            # print(self.funcTable)
                            print("retValue:",retValue)
                        t(retValue)
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
                    else:
                        if v == crk:
                            if self.debug :
                                print("exact matched cmd key:",crk)
                            focus = crk
                        if v == crk[:len(v)] :
                            if self.debug :
                                print("matched cmd key:",crk)
                            matched.append(crk)
                if focus and len(matched) <= 1:
                    newCmd += v + " "
                    root = cmdRoot[focus]
                    if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                        retValue[focus] = v
                        if 'chooseList' in cmdRoot[focus]:
                            retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                        else : 
                            retLiteralCmdList.append(v)
                        retValue['__literal_cmd__'] = retLiteralCmdList
                    else:
                        retCmdList.append(v)  # command
                        retValue['__cmd__'] = retCmdList
                        if 'chooseList' in cmdRoot[focus]:
                            retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                        else : 
                            retLiteralCmdList.append(v)
                        retValue['__literal_cmd__'] = retLiteralCmdList
                    self.copyAdditionalDict(cmdRoot[focus],retValue)
                else :
                    if len(matched) == 0:
                        pass
                    elif len(matched) == 1:
                        focus = matched[0]
                        newCmd += matched[0] + " "
                        root = cmdRoot[matched[0]]
                        if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                            retValue[focus] = v
                            if 'chooseList' in cmdRoot[focus]:
                                retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                            else : 
                                retLiteralCmdList.append(v)
                            retValue['__literal_cmd__'] = retLiteralCmdList
                        else:
                            retCmdList.append(v)  # command
                            retValue['__cmd__'] = retCmdList
                            if 'chooseList' in cmdRoot[focus]:
                                retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                            else : 
                                retLiteralCmdList.append(v)
                            retValue['__literal_cmd__'] = retLiteralCmdList
                        self.cmd = newCmd
                        self.copyAdditionalDict(cmdRoot[matched[0]],retValue)
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
        retValue['__literal_cmd__'] = retLiteralCmdList
        retValue['__cmd__'] = retCmdList
        if self.c == '\n':
            if self.debug:
                print("return root:",root)
                print("lastWord:",lastWord)
                print("retValue:",retValue)
                print("cmd:/",self.cmd,"/",sep="")
            if 'cmd' in root:
                cmdRoot = root['cmd']
                focus = ""
                for crk, crv in cmdRoot.items():
                    if lastWord == crk:
                        if self.debug :
                            print("exact matched cmd key:",crk)
                        focus = crk
                        if 'returnable' in cmdRoot[focus] and cmdRoot[focus]['returnable'] == 'returnable' :
                            retCmdList.append(focus)
                            retValue['__cmd__'] = retCmdList
                            if 'chooseList' in cmdRoot[focus]:
                                if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                                    retLiteralCmdList.append(focus)
                                else:
                                    retLiteralCmdList.append(v)
                            retValue['__literal_cmd__'] = retLiteralCmdList
                            root = cmdRoot[focus]
                        
                        break
        return (root,lastWord,retValue)
            
    def run(self):
        """ 
        main part of cisco command line interface
        get string as input
        """
        # print("the simple distributed compile environment remotely",flush=True)

        print('\n'*2)
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
                    if 'returnfunc' in root and root['returnfunc']:
                        if self.debug:
                            print('returnfunc')
                            print("retValue:",retValue)
                        root['returnfunc'](retValue)
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
                        if self.cmd[-1] == '"' and len(self.cmd) >= 2 and self.cmd[-2] != "\\":
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
                    # if c == '\n':
                    #     if self.debug:
                    #         print(c, 'RETURN',flush=True)
                    #         print("root:",root)
                    #         print("cmd:",self.cmd.replace('\t',' '))
                    #     retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                    #     if ('returnable' in root and root['returnable'] == 'returnable') or 'cmd' not in root:
                    #         return retValue
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
        self.fieldnames = ['name','id','host','passwd','directory','email','command','cpus','cpuUsage','df','runnigTime','enable']
        self.list = []
        if csvfile and os.path.exists(csvfile):
            with open(csvfile, "r" , newline='') as csvfd:
                reader = csv.DictReader(csvfd)
                for row in reader:
                    self.list.append(row)
                if len(self.fieldnames) < len(list(row.keys())):
                    self.fieldnames = list(row.keys())
        self.host = ['tiger','bmw','toyota']
        
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
        
    def test(self,onlyEnable=None):
        print('\n'*3)
        for v in self.list:
            command = 'cd code/fish; git pull ; source a/bin/activate; python3 cpu.py ; df -h ~'
            s = "timeout 5 sshpass -p " + v['passwd'] + " ssh -o StrictHostKeyChecking=no " + v['id'] + '@' + v['host'] + ' "' + command + '"'
            print(s)
            if onlyEnable == True and v['enable'] != 'true':
                continue
            out = os.popen(s).read()
            print("out:",out)
            outa = out.split('\n')
            v['cpus'] = ""
            v['cpuUsage'] = ""
            v['df'] = ""
            for l in outa:
                # print(l)
                grp = cpusRe.search(l)
                if grp:
                    v['cpus'] = str(grp.group('ans'))
                grp = cpuUsageRe.search(l)
                if grp:
                    v['cpuUsage'] = str(grp.group('ans'))
                grp = dfRe.search(l)
                if grp:
                    v['df'] = str(grp.group('ans'))
            if v['cpus'] and v['cpuUsage'] and v['df'] :
                v['enable'] = 'true'
                if v['df'][-1] == 'T':
                    if float(v['df'][:-1]) < 0.15:
                        v['enable'] = 'false'
                elif v['df'][-1] == 'G':
                    if float(v['df'][:-1]) < 150.0:
                        v['enable'] = 'false'
            else :
                v['enable'] = 'false'
        self.dataWrite()
    
    def getBest(self):
        best = 100.0
        bestIdx = -1
        for i,v in enumerate(self.list):
            if v['enable'] == 'true':
                if float(v['cpuUsage']) < best:
                    bestIdx = i
                    best = float(v['cpuUsage'])
        if bestIdx == -1:
            return (-1,best,None)
        else:
            return (bestIdx,best,self.list[bestIdx])
        
    def enableTable(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug:
            print("functionname:",functionNameAsString)
            print(v)
        if v and 'choose' in v:
            print(functionNameAsString , v['choose'])
    
    def listTable(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug:
            print("functionname:",functionNameAsString)
            print(self)
            print(v)
        print()
        cnt = 0
        for row in self.list:
            print(cnt , ":" , row)
            cnt += 1
        print()
        
    def setupClean(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        project = v['__cmd__'][2]
        choose = int(v['choose'])
        print()
        print("name:",project)
        id = self.list[choose]['id']
        passwd = self.list[choose]['passwd']
        host = self.list[choose]['host']
        s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; sh ./clean.sh' + '"'
        print(s)
        os.system(s)
        
    def setupDownload(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        project = v['__cmd__'][2]
        choose = int(v['choose'])
        print()
        print("name:",project)
        id = self.list[choose]['id']
        passwd = self.list[choose]['passwd']
        host = self.list[choose]['host']
        s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; sh ./down.sh' + '"'
        print(s)
        os.system(s)
        
    def setupCompile(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        project = v['__cmd__'][2]
        choose = int(v['choose'])
        print()
        print("name:",project)
        id = self.list[choose]['id']
        passwd = self.list[choose]['passwd']
        host = self.list[choose]['host']
        s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; sh ./run-docker.sh build apps' + '"'
        print(s)
        os.system(s)
        s = "sshpass -p " + passwd + " scp -o StrictHostKeyChecking=no " + id + '@' + host + ':' + '~/code/fish/' + project + '/intel-build/build/packages/tiger*.ipk' + ' . '
        print(s)
        os.system(s)
        
    def setupBestCompile(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        self.test(onlyEnable=True)
        project = v['__cmd__'][2]
        bestIdx,best,bestv = self.getBest()
        print()
        print("name:",project)
        if bestv != None:
            print("best index :",bestIdx)
            print("best cpu usage :",best)
            print("bestv:", bestv)
            print("host:",bestv['host'])
            s = "sshpass -p " + bestv['passwd'] + " ssh -o StrictHostKeyChecking=no " + bestv['id'] + '@' + bestv['host'] + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; sh ./run-docker.sh build apps' + '"'
            print(s)
            os.system(s)
            s = "sshpass -p " + bestv['passwd'] + " scp -o StrictHostKeyChecking=no " + bestv['id'] + '@' + bestv['host'] + ':' + '~/code/fish/' + project + '/intel-build/build/packages/tiger*.ipk' + ' . '
            print(s)
            os.system(s)
        else :
            print("All Server is not good.")
        
        # out = os.popen(s).read()
        # print("out:",out)

    def runDownloadTigerDesktop(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        self.test(onlyEnable=True)
        project = v['__cmd__'][2]
        bestIdx,best,bestv = self.getBest()
        print()
        print("name:",project)
        if bestv != None:
            print("best index :",bestIdx)
            print("best cpu usage :",best)
            print("bestv:", bestv)
            print("host:",bestv['host'])
            s = "sshpass -p " + bestv['passwd'] + " ssh -o StrictHostKeyChecking=no " + bestv['id'] + '@' + bestv['host'] + ' ' + '"' + 'cd code/fish; git pull ; cd ' + project + ' ; touch ppp; sh down.sh' + '"'
            print(s)
            os.system(s)
        else :
            print("All Server is not good.")
        
        out = os.popen(s).read()
        print("out:",out)
        
    def showHost(self,v=None):
        for i,v in enumerate(self.host):
            print(i,v)
        print('choose number')
            
        

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
    
    remoteCmd = {}
    # register CL cheoljoo.lee lotto645.com akstp! ./desktop/image cheoljoo.lee@gmail.com [return]
    registerCmd = csc.addCmd(remoteCmd,'register','command',"","registration command (id , host , passwd , etc)")
    tmp = csc.addArgument(registerCmd,'name','str' , "", "system nickname ")
    tmp = csc.addArgument(tmp,'id','str',"", "login id")
    tmp = csc.addArgument(tmp,'host','str',"", "hostname")
    tmp = csc.addArgument(tmp,'passwd','str',"", "password")
    tmp = csc.addArgument(tmp,'directory','str',"", "output directory")
    tmp = csc.addArgument(tmp,'email','str',"", "email address")
    tmp = csc.addArgument(tmp,'command','str',"", "commands for site")
    # enable : now i do not use it
    enableCmd = csc.addCmd(remoteCmd,'enable','command',"", "change to enable status : you can use this system")
    tmp = csc.addArgument(enableCmd,'choose','int',"returnable", "choose number from the list",prefunc=rc.listTable,returnfunc=rc.enableTable)
    # disable : now i do not use it
    disableCmd = csc.addCmd(remoteCmd,'disable','command',"", "change to disable status : you can not use this system")
    tmp = csc.addArgument(disableCmd,'choose','int',"", "choose number from the list",prefunc=rc.listTable)
    # list [return] : no arguments
    # listCmd = csc.addCmd(remoteCmd,'list','command',"returnable", "show system list")
    # cmd "ls -al \"*.sh\" ; ls "
    # runCmd = csc.addCmd(remoteCmd,'run','command',"", "execute command with quoted string")
    # tmp = csc.addArgument(runCmd,'run','quotestr',"returnable", "execution string ex) \"cd HOME; ls -al\"")
    # test [return]  <- use it now to check server's status
    testCmd = csc.addCmd(remoteCmd,'test','command',"", "test : send command ls -al for each server")
    twoskipCmd = csc.addCmd(testCmd ,'twoskip','command',"", "twoskip follows test")
    threeCmd = csc.addCmd(twoskipCmd ,'three','command',"", "three follows test")
    # test sldd hmi 4 5 [return]
    slddCmd = csc.addCmd(testCmd ,'sldd','command',"", "sldd follows test")
    stopCmd = csc.addCmd(slddCmd ,'stop','command',"returnable", "stop follows sldd")
    helpCmd = csc.addCmd(slddCmd ,'help','command',"returnable", "help follows sldd")
    hmiCmd = csc.addCmd(slddCmd ,'hmi','command',"", "hmi follows sldd")
    tmp = csc.addArgument(hmiCmd,'first','int',"", "need to input with first integer")
    tmp = csc.addArgument(tmp,'second','int',"", "need to input with second integer",prefunc=lambda x: print("prefunc:",x))
    # setup
    setupCmd = csc.addCmd(remoteCmd,'setup','command',"returnable", "setup clean or download in all enabled server",returnfunc=rc.test)
    cleanCmd = csc.addCmd(setupCmd ,'clean','command',"", "clean-up")
    tmp = csc.addCmd(cleanCmd ,'tiger-desktop','command',"", "clean in tiger-desktop")
    tmp = csc.addArgument(tmp,'choose','int',"returnable", "choose number from the list",prefunc=rc.listTable,returnfunc=rc.setupClean)
    downloadCmd = csc.addCmd(setupCmd ,'download','command',"", "download")
    tmp = csc.addCmd(downloadCmd ,'tiger-desktop','command',"", "download in tiger-desktop")
    tmp = csc.addArgument(tmp,'choose','int',"returnable", "choose number from the list",prefunc=rc.listTable,returnfunc=rc.setupDownload)
    compileCmd = csc.addCmd(setupCmd ,'compile','command',"", "compile & copy ipk")
    tmp = csc.addCmd(compileCmd ,'tiger-desktop','command',"", "compile and copy ipk in tiger-desktop")
    tmp = csc.addArgument(tmp,'choose','int',"returnable", "choose number from the list",prefunc=rc.listTable,returnfunc=rc.setupCompile)
    bestCompileCmd = csc.addCmd(setupCmd ,'bestcompile','command',"", "compile & copy ipk in best status server")
    tmp = csc.addCmd(bestCompileCmd ,'tiger-desktop','command',"", "compile and copy ipk in tiger-desktop",returnfunc=rc.setupBestCompile)
    # quit
    # quitCmd = csc.addCmd(remoteCmd ,'quit','command',"returnable", "exit",returnfunc=quit)
    # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=quit)
    # run [return]  <- use it now to check server's status
    runCmd = csc.addCmd(remoteCmd,'run','command',"", "run download or compile")
    downloadCmd = csc.addCmd(runCmd,'download','command',"", "run download")
    tigerDesktopCmd = csc.addCmd(downloadCmd ,'tiger-desktop','command',"returnable", "download of tiger-desktop",returnfunc=rc.runDownloadTigerDesktop)
    compileCmd = csc.addCmd(runCmd,'compile','command',"", "run compile")
    tigerDesktopCmd = csc.addCmd(compileCmd ,'tiger-desktop','command',"returnable", "compile of tiger-desktop",additionalDict={'a':'b','c':'d'})
    
    gethostCmd = csc.addCmd(remoteCmd,'gethost','command',"", "gethosthelp")
    tmp = csc.addArgument(gethostCmd,'choose','int',"returnable", "choose number from the list",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'bmw'})
    tmp = csc.addArgument(tmp,'number','chooseList',"returnable", "choose222 number from the list",chooseList=['bmw','tiger','desktop'])
    
    
    
    csc.setCliRule(remoteCmd)
    # csc.setFunc("listTable",rc.listTable)
    # csc.setFunc("quit",quit)
    # TODO : rule을 만들어서 set 해야 한다. csc.setRule(..)
    while True:
        retValue = csc.run()
        if "quit" == retValue['__return__'][:len('quit')]:
            quit()
        elif "register" == retValue['__return__'][:len('register')]:
            rc.appendData(retValue)
            rc.dataWrite()
        elif "test" == retValue['__return__'].strip():
            rc.test()
        elif "run" == retValue['__cmd__'][0]:
            # rc.test(onlyEnable=True)
            bestIdx,best,bestv = rc.getBest()
            # if bestv != None:
            #     print("best index :",bestIdx)
            #     print("best cpu usage :",best)
            #     print("bestv:", bestv)
            #     rc.runTigerDesktop(retValue,bestv)
            # else :
            #     print("All Server is not good.")
            
        print("loop cmd=[",retValue['__return__'],"]",sep="")
        print("loop retValue:",retValue)
    
    # import ruleData
    # print(ruleData.remoteCmd)
    


