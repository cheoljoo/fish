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
newFileRe = re.compile('^\s*new file:\s+(?P<ans>.*)$')
modifiedRe = re.compile('^\s*modified:\s+(?P<ans>.*)$')
rootPathRe = re.compile('^===========>__<==ROOT')
currentPathRe = re.compile('^===========>__<==CURRENT')



class CiscoStyleCli:
    """ 
    This Class get the string based on cisco style command line interface.
    c = CiscoStyleCli(...)
    lineStr = c.getStr()
    wordStr = c.getWord()
    ch = c.getCh()
    bool = c.setCliRule()
    """
    def __init__(self,rule=None,infinite=False,debug=False):
        """ 
        초기화 self.remoteCmd
        """
        self.infinite = infinite
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
        self.checkReturnable(self.remoteCmd)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
        self.list()
        
    def addCmd(self,root,command,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,chooseList=None):
        """ 
        root['cmd'][command]['type'] = type
        root['cmd'][command]['cmd'] = {} # if you need more command
        return root['cmd'][command]
        """
        functionNameAsString = sys._getframe().f_code.co_name
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
        # check the rule : 1 arugment or all commands
        argumentTypeCount = 0
        commandTypeCount = 0
        anotherTypeCount = 0
        for cmd in root['cmd']:
            if root['cmd'][command]['type'] == 'argument':
                argumentTypeCount += 1
            elif root['cmd'][command]['type'] == 'command':
                commandTypeCount += 1
            else:
                anotherTypeCount += 1
        if argumentTypeCount > 1 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument command type or multiple commands")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        elif argumentTypeCount == 1 and commandTypeCount > 0:
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument.  you should not have any commands type")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        elif anotherTypeCount > 0 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have the following type : argument or command")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        return root['cmd'][command]
    def addArgument(self,root,name,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,chooseList=None):
        """ 
        root['cmd'][name]['type'] = 'argument'
        root['cmd'][name]['argument-type'] = type
        root['cmd'][name]['cmd'] = {} # if you need more command
        """
        functionNameAsString = sys._getframe().f_code.co_name
        if 'cmd' not in root:
            root['cmd'] = {}
        root['cmd'][name] = {}
        root['cmd'][name]['type'] = 'argument'
        root['cmd'][name]['argument-type'] = type
        if isinstance(type,dict):
            for i,v in type.items():
                if not isinstance(i,str):
                    print("key of dictionary should be string type : " , i , ":",  type)
                    quit()
                if not isinstance(v,str):
                    print("value of dictionary should be string type : " ,v , ":", type)
                    quit()
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
        # check the rule : 1 arugment or all commands
        argumentTypeCount = 0
        commandTypeCount = 0
        anotherTypeCount = 0
        for cmd in root['cmd']:
            if root['cmd'][name]['type'] == 'argument':
                argumentTypeCount += 1
            elif root['cmd'][name]['type'] == 'command':
                commandTypeCount += 1
            else:
                anotherTypeCount += 1
        if argumentTypeCount > 1 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument command type or multiple commands")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        elif argumentTypeCount == 1 and commandTypeCount > 0:
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument.  you should not have any commands type")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        elif anotherTypeCount > 0 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have the following type : argument or command")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCound,"others#:",anotherTypeCount)
            quit()
        return root['cmd'][name]
    
    # def setFunc(self,funcname,funcptr):
    #     self.funcTable[funcname] = funcptr
    #     if self.debug and funcptr != quit:
    #         funcptr()
        
    def setCliRule(self,rule):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        self.remoteCmd = rule
        if 'cmd' in self.remoteCmd and 'quit' not in self.remoteCmd['cmd']:
            quitCmd = self.addCmd(remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self.quit)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.quit)
        if 'cmd' in self.remoteCmd and 'list' not in self.remoteCmd['cmd']:
            listCmd = self.addCmd(remoteCmd ,'list','command',"returnable", "show command line interface list",returnfunc=self.list)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.list)
        if 'cmd' in self.remoteCmd and 'list-detailed' not in self.remoteCmd['cmd']:
            listDetailedCmd = self.addCmd(remoteCmd ,'list-detailed','command',"returnable", "show detailed command line interface list",returnfunc=self.listDetailed)
        self.checkReturnable(self.remoteCmd)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
        self.list()
    
    def quit(self,v=None):
        print("byebye!!   see you again~~   *^^*")
        quit()
    
    def list(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self,v)
        self.traverseList(self.remoteCmd,"")
        for s in self.tlist:
            print(s)
        print()
    def listDetailed(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
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
                        rt = ' <CR>'
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
                            self.traverseList(v,start + " (argument:" + str(argtype) +") " + prefunc + k + returnfunc + rt,detailed=True)
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
    def _changeQuoteFlag(self,quoteFlag,s = None):
        if s == None:
            if quoteFlag == False:
                quoteFlag = True
            else :
                quoteFlag = False
        else :
            quoteFlag = False
            i = 0
            for c in s:
                if i == 0 and c == '"':
                    quoteFlag = self._changeQuoteFlag(quoteFlag)
                elif i > 0 and c == '"' and s[i-1] != "\\":
                    quoteFlag = self._changeQuoteFlag(quoteFlag)
                i += 1
        return quoteFlag
    def findRoot(self,cmd):
        """ 
        while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
        'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
        prevCmd = 'gethost'가 들어가면 안성맞춤이다.
        """
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug : 
            print("functionname:",functionNameAsString)
        retValue = {}
        retCmdList = []
        retLiteralCmdList = []
        words = cmd.strip().split(' ')
        root = self.remoteCmd
        lastWord = ""
        newCmd = ""
        #if self.cmd == "":
        #    return (root,lastWord,retValue,quoteFlag)
        #elif self.cmd[0] == ' ':        # self.cmd != ""
        #    return (root,lastWord,retValue,quoteFlag)
        # while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
        # 'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
        # prevCmd = 'gethost'가 들어가면 안성맞춤이다.
        while len(words):
            prevRoot = root
            v = words.pop(0)
            lastWord = v
            if self.debug:
                print("get word : v :",v)
                print("root:",root)
                print("words:",words)
                print("retValue:",retValue)
            if words :  # 마지막 word가 아니면 
                if 'cmd' in root:
                    cmdRoot = root['cmd']
                    if self.debug:
                        print("v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
                    # matched command
                    if v in cmdRoot and cmdRoot[v]['type'] == 'command':
                        root = cmdRoot[v]
                        newCmd += v + ' '
                        continue
                    # matched argument
                    for crk, crv in cmdRoot.items():
                        if cmdRoot[crk]['type'] == 'argument':
                            if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
                                if v not in cmdRoot[crk]['argument-type']:
                                    returnValue = -1
                                    return (returnValue,prevRoot,root,lastWord,newCmd)  # returnValue == -1 : not matched
                            root = cmdRoot[crk]
                            newCmd += v + ' '
                            continue
                returnValue = -1
                return (returnValue,prevRoot,root,lastWord,newCmd) # returnValue == -1 : not matched
    def common(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if v:
            print("v",v)
        
    def _showRecommendation(self,r,retValue):
        root = r
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString , "root:",root)
        if 'returnable' in root and root['returnable'] == 'returnable':
            print("    <CR> : [returnable]")
        if 'cmd' in root :
            cmdRoot = root['cmd']
            for s in cmdRoot:
                t = 'argument'
                if cmdRoot[s]['type'] != 'argument':
                    t = 'command'
                returnable = ""
                if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                    returnable = '[returnable]'
                if 'prefunc' in cmdRoot[s] and cmdRoot[s]['prefunc']:
                    if self.debug:
                        print('prefunc:',cmdRoot[s]['prefunc'])
                        print("retValue:",retValue)
                    print('prefunc:',cmdRoot[s]['prefunc'])
                    cmdRoot[s]['prefunc'](retValue)
                print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                if t == 'argument' and 'argument-type' in cmdRoot[s] :
                    ld = cmdRoot[s]['argument-type']
                    if isinstance(ld,list) :
                        for s in ld:
                            print('    ' + s)
                    elif isinstance(ld,dict):
                        for s in ld.keys():
                            print('    ' + str(s) + ' : ' + ld[s])
                            
                        

        # else :
        #     print(" this is leaf node")

    def checkCmd(self,cmd):
        """ 
        check whether this cmd is right
        return the location from rootCmd following cmd  for guiding current and next arguments

        self.c : current input character
        """
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug : 
            print("functionname:",functionNameAsString)

        retValue = {}
        retCmdList = []
        retLiteralCmdList = []
        words = cmd.strip().split(' ')
        quoteFlag = False
        isFinishedFromReturn = False
        if self.debug:
            print("cmd:[",self.cmd,"]",sep="")
            print("checkCmd:words:",words)
        # for w in words:
        #     i = 0
        #     for s in w:
        #         if i == 0 and s == '"':
        #             quoteFlag = self._changeQuoteFlag(quoteFlag)
        #         elif i > 0 and s == '"' and w[i-1] != "\\":
        #             quoteFlag = self._changeQuoteFlag(quoteFlag)
        #         i += 1

        root = self.remoteCmd
        lastWord = ""
        newCmd = ""
        #if self.cmd == "":
        #    return (root,lastWord,retValue,quoteFlag)
        #elif self.cmd[0] == ' ':        # self.cmd != ""
        #    return (root,lastWord,retValue,quoteFlag)
        # while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
        # 'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
        # prevCmd = 'gethost'가 들어가면 안성맞춤이다.
        while len(words) > 1:
            prevRoot = root
            v = words.pop(0)
            lastWord = v
            if self.debug:
                print("get word : v :",v)
                print("root:",root)
                print("words:",words)
                print("retValue:",retValue)
            if words :  # 마지막 word가 아니면 
                if 'cmd' in root:
                    cmdRoot = root['cmd']
                    if self.debug:
                        print("v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
                    # matched command
                    if v in cmdRoot and cmdRoot[v]['type'] == 'command':
                        root = cmdRoot[v]
                        newCmd += v + ' '
                        retCmdList.append(v)  # command
                        retValue['__cmd__'] = retCmdList
                        continue
                    # matched argument
                    else:
                        for crk, crv in cmdRoot.items():
                            if cmdRoot[crk]['type'] == 'argument':
                                if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
                                    if v not in cmdRoot[crk]['argument-type']:
                                        # returnValue = -1
                                        # return (returnValue,prevRoot,root,lastWord,newCmd)  # returnValue == -1 : not matched
                                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                        self.cmd = newCmd.strip()
                                        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                retValue[crk] = v
                                root = cmdRoot[crk]
                                newCmd += v + ' '
                                continue
                else:
                    # returnValue = -1
                    # return (returnValue,prevRoot,root,lastWord,newCmd) # returnValue == -1 : not matched
                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                    self.cmd = newCmd
                    retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        # last word of command
        if words and len(words) == 1:
            v = words.pop(0)
            lastWord = v
            # return : matched returnable
            if self.c == '\n' and 'cmd' in root:
                print()
                cmdRoot = root['cmd']
                if self.debug:
                    print("last matched returnable v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
                # matched command
                if v in cmdRoot and cmdRoot[v]['type'] == 'command':
                    root = cmdRoot[v]
                    newCmd += v + ' '
                    retCmdList.append(v)  # command
                    retValue['__cmd__'] = retCmdList
                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                    if 'returnable' in root and root['returnable'] == 'returnable':
                        if 'returnfunc' in root and root['returnfunc']:
                            if self.debug:
                                print('returnfunc:',root['returnfunc'])
                                print("retValue:",retValue)
                            print('returnfunc',root['returnfunc'])
                            root['returnfunc'](retValue)
                        self.cmd = ""
                        if self.debug:
                            print("matched command:",retValue)
                        isFinishedFromReturn = True
                        return (root,lastWord,retValue,False,isFinishedFromReturn)
                # matched argument
                else : 
                    for crk, crv in cmdRoot.items():
                        if cmdRoot[crk]['type'] == 'argument':
                            matchedFlag = False
                            if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
                                if v in cmdRoot[crk]['argument-type']:   # matched
                                    matchedFlag = True
                            else:   # matched
                                matchedFlag = True
                            if matchedFlag : # matched
                                retValue[crk] = v
                                root = cmdRoot[crk]
                                newCmd += v + ' '
                                retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                if self.debug:
                                    print("matched argument or list/dict :",retValue)
                                if 'returnable' in root and root['returnable'] == 'returnable':
                                    if 'returnfunc' in root and root['returnfunc']:
                                        if self.debug:
                                            print('returnfunc',root['returnfunc'])
                                            print("retValue:",retValue)
                                        print('returnfunc',root['returnfunc'])
                                        root['returnfunc'](retValue)
                                    self.cmd = ""
                                    if self.debug:
                                        print("matched command:",retValue)
                                    isFinishedFromReturn = True
                                    return (root,lastWord,retValue,False,isFinishedFromReturn)


            # return : not matched returnable or space : recommendate next string
            if self.debug:
                print("last not matched returnable v:",v,"root:",root)
            # if 'returnable' in root and root['returnable'] == 'returnable':
            #     print("recommend : <CR> -" , root['desc'])
            if 'cmd' in root:
                cmdRoot = root['cmd']
                if self.debug:
                    print("not matched returnable v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
                focusType = ''
                focus = ""
                matched = []
                for crk, crv in cmdRoot.items():
                    if cmdRoot[crk]['type'] == 'argument':
                        if self.debug :
                            print("argument cmd :",v , "type:" , cmdRoot[crk]['type'], "ar type:" , cmdRoot[crk]['argument-type'] , "next keys:", cmdRoot.keys())
                        focus = crk
                        focusType = cmdRoot[crk]['type']
                        break
                    else:   # command
                        if v == crk:
                            if self.debug :
                                print("exact matched cmd key:",crk)
                            focus = crk
                            focusType = cmdRoot[crk]['type']
                        if v == crk[:len(v)] :
                            if self.debug :
                                print("matched cmd key:",crk)
                            matched.append(crk)
                # 우리는 focusType (즉, argument , command)로 나누어 처리한다. 
                # argument일때는 딱 1개만 존재하게 되고, argument와 command가 같이 있다면 무조건 argument가 우선순위가 높다.
                if focusType == 'argument':
                    oldCmd = newCmd
                    newCmd += v + " "
                    if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                        if 'argument-type' in cmdRoot[focus] and isinstance(cmdRoot[focus]['argument-type'],(list,dict)) :
                            if self.debug:
                                print("cmdRoot[focus]['argument-type']:", cmdRoot[focus]['argument-type'])
                                for v in cmdRoot[focus]['argument-type']:
                                    print("   " , v)
                            if v not in cmdRoot[focus]['argument-type']:
                                temp = v
                                longestMatch = v
                                arguMatched = []
                                for atv in cmdRoot[focus]['argument-type']:
                                    if v == atv[:len(v)]:
                                        arguMatched.append(atv)
                                if arguMatched:
                                    for c in arguMatched[0][len(v):]:
                                        temp += c
                                        longestMatchFlag = True
                                        for m in arguMatched:
                                            if temp != m[:len(temp)] :
                                                longestMatchFlag = False
                                                break
                                        if longestMatchFlag == True:
                                            longestMatch = temp
                                        else :
                                            break
                                    newCmd = oldCmd + longestMatch
                                    print()
                                    print("recommend list:",flush=True)
                                    for s in cmdRoot[focus]['argument-type']:
                                        print('    list or dict:',s , flush=True)
                                    print('choose one from upper list.')
                                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                    self.cmd = newCmd
                                    # show recommendation
                                    self._showRecommendation(root,retValue)
                                    if self.debug:
                                        print("longest matched command:",retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                else : 
                                    newCmd = oldCmd
                                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                    self.cmd = newCmd
                                    if self.debug:
                                        print("not matched command:",retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                        root = cmdRoot[focus]
                        retValue[focus] = v
                        retValue['__return__'] = newCmd.strip().replace('\t',' ')
                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                        self.cmd = newCmd
                        # show recommendation
                        self._showRecommendation(root,retValue)
                        if self.debug:
                            print("matched command:",retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                        # if 'chooseList' in cmdRoot[focus]:
                        #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                        # else : 
                        #     retLiteralCmdList.append(v)
                        # retValue['__literal_cmd__'] = retLiteralCmdList
                    # self.copyAdditionalDict(cmdRoot[focus],retValue)
                else: # command
                    if focus and len(matched) <= 1:  # command중에 딱 맞는게 있다.
                        newCmd += v + " "
                        root = cmdRoot[focus]
                        retCmdList.append(v)  # command
                        retValue['__cmd__'] = retCmdList
                        retValue['__return__'] = newCmd.strip().replace('\t',' ')
                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                        self.cmd = newCmd
                        # show recommendation
                        self._showRecommendation(root,retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                        # if 'chooseList' in cmdRoot[focus]:
                        #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                        # else : 
                        #     retLiteralCmdList.append(v)
                        # retValue['__literal_cmd__'] = retLiteralCmdList
                        # self.copyAdditionalDict(cmdRoot[focus],retValue)
                    else :  # 딱 맞는 것은 없다.
                        if len(matched) == 0:
                            retValue['__return__'] = newCmd.strip().replace('\t',' ')
                            quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                            self.cmd = newCmd
                            print('ERROR: no matched == 0')
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                        elif len(matched) == 1:
                            focus = matched[0]
                            newCmd += matched[0] + " "
                            root = cmdRoot[focus]
                            if 'type' in cmdRoot[focus] and cmdRoot[focus]['type'] == 'argument' :
                                print("ERROR: not reachable")
                                # if 'chooseList' in cmdRoot[focus]:
                                #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                                # else : 
                                #     retLiteralCmdList.append(v)
                                # retValue['__literal_cmd__'] = retLiteralCmdList
                            else:
                                retCmdList.append(v)  # command
                                retValue['__cmd__'] = retCmdList
                                # if 'chooseList' in cmdRoot[focus]:
                                #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['chooseList'][int(v)])
                                # else : 
                                #     retLiteralCmdList.append(v)
                                # retValue['__literal_cmd__'] = retLiteralCmdList
                            retValue[focus] = v
                            retValue['__return__'] = newCmd.strip().replace('\t',' ')
                            quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                            self.cmd = newCmd
                            # show recommendation
                            self._showRecommendation(root,retValue)
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                            # self.copyAdditionalDict(cmdRoot[matched[0]],retValue)
                        else:
                            print()
                            print("recommend list: ",end="",flush=True)
                            for s in matched:
                                print(s," ",end="",flush=True)
                            print()
                            temp = v
                            longestMatch = v
                            matchFlag = True
                            for c in matched[0][len(v):]:
                                temp += c
                                for m in matched:
                                    if temp != m[:len(temp)] :
                                        matchFlag = False
                                        break
                                if matchFlag == True:
                                    longestMatch = temp
                                else :
                                    break
                            newCmd += longestMatch
                            retValue['__return__'] = newCmd.strip().replace('\t',' ')
                            quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                            self.cmd = newCmd
                            for s in matched:
                                t = 'argument'
                                if cmdRoot[s]['type'] != 'argument':
                                    t = 'command'
                                returnable = ""
                                if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                                    returnable = '[returnable]'
                                print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        else :  # cmd == "" 인 경우
            print("ERROR:words length", len(words) , words)

        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)


        #if self.cmd == "":
        #    return (root,lastWord,retValue,quoteFlag)
        #elif self.cmd[0] == ' ':        # self.cmd != ""
        #    return (root,lastWord,retValue,quoteFlag)
        # while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
        # 'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
        # prevCmd = 'gethost'가 들어가면 안성맞춤이다.


    def checkReturnable(self,root):
        if 'cmd' in root:
            rootCmd = root['cmd']
            for k,v in rootCmd.items():
                if 'cmd' in rootCmd[k]:
                    self.checkReturnable(rootCmd[k])
                else:
                    rootCmd[k]['returnable'] = 'returnable'
                if 'returnable' in rootCmd[k] and rootCmd[k]['returnable'] == 'returnable':
                    if 'returnfunc' not in rootCmd[k] or not rootCmd[k]['returnfunc']:
                        rootCmd[k]['returnfunc'] = self.common
        return
            
    def run(self):
        """ 
        main part of cisco command line interface
        get string as input
        """
        # print("the simple distributed compile environment remotely",flush=True)


        print('\n'*2)
        self.cmd = ""
        self.c = ''
        while True:
            root , lastCmd , retValue , quoteFlag , isFinishedFromReturn = self.checkCmd(self.cmd.strip())
            if self.debug:
                # print("self.remoteCmd:",self.remoteCmd)
                #print('root:', root)
                print('quoteFlag:',quoteFlag, "isFinishedFromReturn:",isFinishedFromReturn)
                print('lastCmd:', lastCmd , 'retValue:',retValue , 'self.infinite:',self.infinite)
            if isFinishedFromReturn == True and self.infinite == False:
                return retValue
            print('input:', self.cmd.replace('\t',' '),end='',sep='',flush=True)
            while True:
                if self.debug:
                    print(flush=True)
                    print("quoteFlag:",quoteFlag," input:/",self.cmd.replace("\t"," "),"/",self.cmd.replace("\t"," "),sep="",end="",flush=True)
                c = self.getch()
                self.c = c
                
                # print(c,ord(c))
                if ord(c) == 8 or ord(c) == 127 :  # backspace 8:linux terminal ,  127:vscode terminal
                    if len(self.cmd) > 0:
                        print('\b \b',end="",flush=True)
                        last = self.cmd[-1]
                        self.cmd = self.cmd[:-1]
                        if last == '"' and len(self.cmd) >= 1 and self.cmd[-1] != "\\":
                            quoteFlag = self._changeQuoteFlag(quoteFlag)
                        continue
                    continue
                if self.debug:
                    print("cmd1:[",self.cmd,"] quoteFlag=",quoteFlag,sep="")
                if self.cmd and c == '"' and self.cmd[-1] != "\\":
                    quoteFlag = self._changeQuoteFlag(quoteFlag)
                    if quoteFlag == False:
                        self.cmd += c + ' '
                        self.c = ' '
                        break
                elif not self.cmd and c == '"':
                    quoteFlag = self._changeQuoteFlag(quoteFlag)
                    if quoteFlag == False:
                        self.cmd += c + ' '
                        self.c = ' '
                        break
                if self.debug:
                    print("cmd2:[",self.cmd,"] quoteFlag=",quoteFlag,sep="")
                if quoteFlag == True:
                    if c == '\n':
                        continue
                    if c == ' ':
                        c = '\t'
                    self.cmd += c
                    if self.debug:
                        print("in quote cmd:[",self.cmd,"] quoteFlag=",quoteFlag,sep="")
                    print(c.replace("\t",' '),end="",flush=True)
                else : 
                    if c == '\t' or c == '\n':
                        c = ' '
                    if self.c == '\n':
                        break
                    if c == ' ' and self.cmd and self.cmd[-1] == ' ':
                        break
                    print(c,end="",flush=True)
                    self.cmd += c
                    if c == ' ' :
                        break
                        
        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
        return retValue

    def traverseFD(self,f,vv,start:str):
        # print(start," ",file=f)
        if isinstance(vv, dict):
            print(start ,  " = {}", sep="", file=f)
            for k, v in vv.items():
                self.traverseFD(f,v,start + "['" + str(k)  + "']")
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
        
    def setupCopy(self,v=None):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self)
            print("v:",v)
        project = v['__cmd__'][2]
        choose = int(v['choose'])
        print()
        print("name:",project)

        print('cd ' + project + ' ; echo "===========>__<==ROOT" > repo_status.log')
        os.system('cd ' + project + ' ; echo "===========>__<==ROOT" > repo_status.log')
        print('cd ' + project + ' ; pwd >> repo_status.log')
        os.system('cd ' + project + ' ; pwd >> repo_status.log')
        print('cd ' + project + ' ; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')
        os.system('cd ' + project + ' ; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')

        with open(project + "/repo_status.log", "r" , newline='') as f:
            lines = f.readlines()

        rootPath = ""
        currentPath = ""
        rootPathFlag = False
        currentPathFlag = False
        filelist = []
        for l in lines:
            if rootPathRe.search(l):
                grp = rootPathRe.search(l)
                rootPathFlag = True
                continue
            elif currentPathRe.search(l):
                grp = currentPathRe.search(l)
                if grp:
                    currentPathFlag = True
                    continue
            elif newFileRe.search(l):
                grp = newFileRe.search(l)
                if grp:
                    filename = str(grp.group('ans')).strip()
                    if currentPath.find('intel-build') == -1:
                        filelist.append('.' + currentPath.strip() + '/' + filename.strip())
            elif modifiedRe.search(l):
                grp = modifiedRe.search(l)
                if grp:
                    filename = str(grp.group('ans'))
                    if currentPath.find('intel-build') == -1:
                        filelist.append('.' + currentPath.strip() + "/" + filename.strip())
            if rootPathFlag:
                rootPath = l.strip()
                rootPathFlag = False
            if currentPathFlag:
                currentPath = l.strip()
                currentPath = currentPath.replace(rootPath,"")
                currentPathFlag = False
            
        print("filelist:",filelist)
        s = 'cd ' + project + ' ; tar cvfz modified.tar.gz ' + ' '.join(filelist)
        print(s)
        os.system(s)

        id = self.list[choose]['id']
        passwd = self.list[choose]['passwd']
        host = self.list[choose]['host']
        s = "sshpass -p " + passwd + " scp -o StrictHostKeyChecking=no " + project + '/modified.tar.gz ' + id + '@' + host + ':~/code/fish/' + project
        print(s)
        os.system(s)

        s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; tar xvfz modified.tar.gz' + '"'
        print(s)
        os.system(s)

        s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; python3 make_tar_ball.py' + '"'
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
            id = bestv['id']
            passwd = bestv['passwd']
            host = bestv['host']

            print('cd ' + project + ' ; echo "===========>__<==ROOT" > repo_status.log')
            os.system('cd ' + project + ' ; echo "===========>__<==ROOT" > repo_status.log')
            print('cd ' + project + ' ; pwd >> repo_status.log')
            os.system('cd ' + project + ' ; pwd >> repo_status.log')
            print('cd ' + project + ' ; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')
            os.system('cd ' + project + ' ; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')
    
            with open(project + "/repo_status.log", "r" , newline='') as f:
                lines = f.readlines()
    
            rootPath = ""
            currentPath = ""
            rootPathFlag = False
            currentPathFlag = False
            filelist = []
            for l in lines:
                if rootPathRe.search(l):
                    grp = rootPathRe.search(l)
                    rootPathFlag = True
                    continue
                elif currentPathRe.search(l):
                    grp = currentPathRe.search(l)
                    if grp:
                        currentPathFlag = True
                        continue
                elif newFileRe.search(l):
                    grp = newFileRe.search(l)
                    if grp:
                        filename = str(grp.group('ans')).strip()
                        if currentPath.find('intel-build') == -1:
                            filelist.append('.' + currentPath.strip() + '/' + filename.strip())
                elif modifiedRe.search(l):
                    grp = modifiedRe.search(l)
                    if grp:
                        filename = str(grp.group('ans'))
                        if currentPath.find('intel-build') == -1:
                            filelist.append('.' + currentPath.strip() + "/" + filename.strip())
                if rootPathFlag:
                    rootPath = l.strip()
                    rootPathFlag = False
                if currentPathFlag:
                    currentPath = l.strip()
                    currentPath = currentPath.replace(rootPath,"")
                    currentPathFlag = False
            print("filelist:",filelist)
    
            s = 'cd ' + project + ' ; tar cvfz modified.tar.gz ' + ' '.join(filelist)
            print(s)
            os.system(s)
            s = "sshpass -p " + passwd + " scp -o StrictHostKeyChecking=no " + project + '/modified.tar.gz ' + id + '@' + host + ':~/code/fish/' + project
            print(s)
            os.system(s)
            s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; tar xvfz modified.tar.gz' + '"'
            print(s)
            os.system(s)
            s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; python3 make_tar_ball.py' + '"'
            print(s)
            os.system(s)

            s = "sshpass -p " + passwd + " ssh -o StrictHostKeyChecking=no " + id + '@' + host + ' ' + '"' + 'cd code/fish ; cd ' + project + ' ; sh ./run-docker.sh build apps' + '"'
            print(s)
            os.system(s)
            s = "sshpass -p " + passwd + " scp -o StrictHostKeyChecking=no " + id + '@' + host + ':' + '~/code/fish/' + project + '/intel-build/build/packages/tiger*.ipk' + ' . '
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
    parser.add_argument("--infinite", action="store_true",default=False,help='show the command but not run it for test & debug')
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
    
    parser.add_argument('X', type=str, nargs='+')

    args = parser.parse_args()

    X_list = args.X
    print("argv:",X_list)

    csc = CiscoStyleCli(rule = args.rulefile , infinite = args.infinite , debug = args.debug)
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
    copyCmd = csc.addCmd(setupCmd ,'copy','command',"", "modified source copy")
    tmp = csc.addCmd(copyCmd ,'tiger-desktop','command',"", "copy modified code in tiger-desktop")
    tmp = csc.addArgument(tmp,'choose','int',"returnable", "choose number from the list",prefunc=rc.listTable,returnfunc=rc.setupCopy)
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
    tigerDesktopCmd = csc.addArgument(downloadCmd ,'model',['tiger-desktop'],"returnable", "download of tiger-desktop",returnfunc=rc.runDownloadTigerDesktop)
    compileCmd = csc.addCmd(runCmd,'compile','command',"", "run compile")
    tigerDesktopCmd = csc.addArgument(compileCmd ,'model',['tiger-desktop','bmw'],"returnable", "compile of tiger-desktop",additionalDict={'a':'b','c':'d'})
    
    gethostCmd = csc.addCmd(remoteCmd,'gethost','command',"", "gethosthelp")
    tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
    tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
    tmp = csc.addCmd(gethostCmd,'choose2','command',"", "choose type2",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
    tmp = csc.addArgument(tmp,'number',['cheetah','tiger','fish'],"returnable", "type from the list",returnfunc=csc.common)
    tmp = csc.addCmd(gethostCmd,'choose3','command',"", "choose type3",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
    tmp = csc.addArgument(tmp,'shoot',{'0':'car','1':'tiger','2':'telematics'},"returnable", "type key from the dictionary",returnfunc=csc.common)
    
    
    
    csc.setCliRule(remoteCmd)
    # csc.setFunc("listTable",rc.listTable)
    # csc.setFunc("quit",quit)

    if args.X:
        x = ' '.join(args.X)
        print(x)
        csc.c = '\n'
        root , lastCmd , retValue , quoteFlag , isFinishedFromReturn = csc.checkCmd(x)
        print('quoteFlag:',quoteFlag, "isFinishedFromReturn:",isFinishedFromReturn)
        print('lastCmd:', lastCmd , 'retValue:',retValue)
        quit()

    while True:
        retValue = csc.run()
        if "quit" == retValue['__return__'][:len('quit')]:
            quit()
        elif "register" == retValue['__return__'][:len('register')]:
            print('register')
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
    


# TODO
# argument list
# process argument-type , we show the list and use these definition when argument-type is list
# auto completion
# show the list at "" when we press the spacebar
# when we press ? , we show the following whole commands and show the mapping table for arguments until input now.

