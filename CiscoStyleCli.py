import datetime
import re
import argparse
import io
import time
import subprocess
import os
import glob
import csv
import sys

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
intRe = re.compile('^\s*(?P<ans>[0-9\-\+]+)\s*$')
floatRe = re.compile('^\s*(?P<ans>[0-9\-\+\.]+)\s*$')
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
    def __init__(self,rule=None,infinite=False,prompt = "FISH~~:" , debug=False):
        """ 
        초기화 self.remoteCmd
        """
        self.infinite = infinite
        self.debug = debug
        self.c = ''
        self.prompt = prompt
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
        
    def addCmd(self,root,command,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,additionalList=None):
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
        if additionalList :
            root['cmd'][command]['additionalList'] = additionalList
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
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        elif argumentTypeCount == 1 and commandTypeCount > 0:
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument.  you should not have any commands type")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        elif anotherTypeCount > 0 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have the following type : argument or command")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        return root['cmd'][command]
    def addArgument(self,root,name,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,additionalList=None):
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
        if additionalList:
            root['cmd'][name]['additionalList'] = additionalList
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
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        elif argumentTypeCount == 1 and commandTypeCount > 0:
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have just 1 argument.  you should not have any commands type")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        elif anotherTypeCount > 0 :
            print("functionname:",functionNameAsString, locals())
            print("ERROR: you should have the following type : argument or command")
            print("    your result : argument#:",argumentTypeCount , "command#:",commandTypeCount,"others#:",anotherTypeCount)
            quit()
        return root['cmd'][name]
    
    # def setFunc(self,funcname,funcptr):
    #     self.funcTable[funcname] = funcptr
    #     if self.debug and funcptr != quit:
    #         funcptr()
    def _setCliRuleTcmdRecursive(self,root,topNode):
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug:
            print("functionname:",functionNameAsString)
            print("root:",root)
            print("top:",topNode)
        for k,v in topNode.items():
            if k == '__attribute':
                continue
            type = 'command'
            returnable = ""
            desc = ""
            argumentType = None
            if '__attribute' in v:
                if 'type' in v['__attribute']:
                    type = v['__attribute']['type']
                if 'returnable' in v['__attribute']:
                    returnable = v['__attribute']['returnable']
                if 'desc' in v['__attribute']:
                    desc = v['__attribute']['desc']
                if 'argument-type' in v['__attribute']:
                    argumentType = v['__attribute']['argument-type']
            if type == 'argument':
                tmpRoot = csc.addArgument(root,k,argumentType,returnable,desc)
            else:
                tmpRoot = csc.addCmd(root,k,'command',returnable,desc)
            if ('__attribute' in v and len(v) > 1) or ('__attribute' not in v and len(v) > 0):
                self._setCliRuleTcmdRecursive(tmpRoot,v)
    def setCliRuleTcmd(self,top):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        self.remoteCmd = {}
        self._setCliRuleTcmdRecursive(self.remoteCmd,top)
        
        if 'cmd' in self.remoteCmd and 'quit' not in self.remoteCmd['cmd']:
            quitCmd = self.addCmd(self.remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self.quit)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.quit)
        if 'cmd' in self.remoteCmd and 'list' not in self.remoteCmd['cmd']:
            listCmd = self.addCmd(self.remoteCmd ,'list','command',"returnable", "show command line interface list",returnfunc=self.list)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.list)
            tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self.listDetailed)
            tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self.listSimple)
        self.checkReturnable(self.remoteCmd)
        self.traverseFile("ruleData.py",self.remoteCmd,"remoteCmd","w")
        self.list()

    def setCliRule(self,rule):
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        self.remoteCmd = rule
        if 'cmd' in self.remoteCmd and 'quit' not in self.remoteCmd['cmd']:
            quitCmd = self.addCmd(self.remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self.quit)
            # tmp = csc.addCmd(quitCmd ,'','command',"", "exit",prefunc=self.quit)
        if 'cmd' in self.remoteCmd and 'list' not in self.remoteCmd['cmd']:
            listCmd = self.addCmd(self.remoteCmd ,'list','command',"returnable", "show command line interface list",returnfunc=self.list)
            tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self.listDetailed)
            tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self.listSimple)
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
    def listSimple(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self,v)
        self.traverseList(self.remoteCmd,"",detailed=True,simple=True)
        for s in self.tlist:
            print(s)
        print()
    def traverseList(self,vv,start:str,detailed=False,simple=False):
        # print(start," ",file=f)
        if isinstance(vv, dict):
            if 'cmd' in vv:
                v2 = vv['cmd']
                for k, v in v2.items():
                    rt = ""
                    if 'returnable' in v and v['returnable'] == 'returnable':
                        rt = ' <CR>'
                    if self.debug:
                        print("show:",rt,k,v)
                    if simple:
                        if 'type' in v and v['type'] != 'argument': 
                            self.traverseList(v,start + " " + k + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self.traverseList(v,start + " " + k  + rt,detailed,simple)
                    elif detailed:
                        prefunc = ""
                        if 'prefunc' in v:
                            prefunc = " pre-func" + str(v['prefunc'])
                        returnfunc = ""
                        if 'returnfunc' in v:
                            returnfunc = " ret-func:" + str(v['returnfunc'])
                        if 'type' in v and v['type'] != 'argument': 
                            self.traverseList(v,start + " (commands) " + prefunc + k  + returnfunc + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self.traverseList(v,start + " (argument:" + str(argtype) +") " + prefunc + k + returnfunc + rt,detailed,simple)
                    else:
                        if 'type' in v and v['type'] != 'argument': 
                            self.traverseList(v,start + " (commands) " + k  + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self.traverseList(v,start + " (argument:" + str(argtype) + ") " + k  + rt,detailed,simple)
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

    def copyAdditionalDictAndList(self,_from,_to):
        if 'additionalDict' in _from:
            for adk,adv in _from['additionalDict'].items():
                if '__additionalDict__' not in _to:
                    _to['__additionalDict__'] = {}
                _to['__additionalDict__'][adk] = adv
        if 'additionalList' in _from:
            for adk,adv in _from['additionalList']:
                _to['__additionalList__'] = _from['additionalList']
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
        print("ERROR: need your definiation for return function")
        
    def _showRecommendation(self,r,retValue):
        root = r
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug :
            print("functionname:",functionNameAsString , "root:",root)
        if 'returnable' in root and root['returnable'] == 'returnable':
            print("    -> <CR> : [returnable]")
        
        if 'cmd' in root :
            cmdRoot = root['cmd']
            for s in cmdRoot:
                t = 'argument'
                if cmdRoot[s]['type'] != 'argument':
                    t = 'command'
                else:
                    if 'argument-type' in cmdRoot[s]:
                        t += ":" + str(cmdRoot[s]['argument-type'])
                returnable = ""
                if 'returnable' in cmdRoot[s] and cmdRoot[s]['returnable'] == 'returnable':
                    returnable = '[returnable]'
                if 'prefunc' in cmdRoot[s] and cmdRoot[s]['prefunc']:
                    if self.debug:
                        print('prefunc:',cmdRoot[s]['prefunc'])
                        print("retValue:",retValue)
                    # print('prefunc:',cmdRoot[s]['prefunc'])
                    cmdRoot[s]['prefunc'](retValue)
                if self.debug:
                    print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                print('help: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                if cmdRoot[s]['type'] == 'argument' and 'argument-type' in cmdRoot[s] :
                    ld = cmdRoot[s]['argument-type']
                    if isinstance(ld,list) :
                        for s in ld:
                            print('    ->' + s)
                    elif isinstance(ld,dict):
                        for s in ld.keys():
                            print('    ->' + str(s) + ' : ' + ld[s])
        # else :
        #     print(" this is leaf node")
    def _checkArgumentType(self,v,type):
        if type == 'int':
            grp = intRe.search(v)
            if not grp:
                return False
        elif type == 'float':
            grp = floatRe.search(v)
            if not grp:
                return False
        return True
    def checkCmd(self,cmd):
        """ 
        check whether this cmd is right
        return the location from rootCmd following cmd  for guiding current and next arguments

        self.c : current input character
        """
        print()
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
                                data = None
                                if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
                                    data = cmdRoot[crk]['argument-type']
                                    if v not in cmdRoot[crk]['argument-type']:
                                        # returnValue = -1
                                        # return (returnValue,prevRoot,root,lastWord,newCmd)  # returnValue == -1 : not matched
                                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                        self.cmd = newCmd.strip()
                                        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                        self.copyAdditionalDictAndList(root,retValue)
                                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                elif 'argument-type' in cmdRoot[crk]:
                                    if self._checkArgumentType(v,cmdRoot[crk]['argument-type']) == False:
                                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                        self.cmd = newCmd
                                        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                        self.copyAdditionalDictAndList(root,retValue)
                                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                if data:
                                    retValue[crk] = { 'choice':v , 'data':data }
                                else : 
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
                    self.copyAdditionalDictAndList(root,retValue)
                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        # last word of command
        if words and len(words) == 1:
            v = words.pop(0)
            lastWord = v
            # return : matched returnable
            if self.c == '\n' and 'cmd' in root:
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
                    self.copyAdditionalDictAndList(root,retValue)
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
                            data = None
                            if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
                                if v in cmdRoot[crk]['argument-type']:   # matched
                                    matchedFlag = True
                                    data = cmdRoot[crk]['argument-type']
                            elif 'argument-type' in cmdRoot[crk] and self._checkArgumentType(v,cmdRoot[crk]['argument-type']) == False:
                                quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                self.cmd = newCmd
                                retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                self.copyAdditionalDictAndList(root,retValue)
                                return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                            else:   # matched
                                matchedFlag = True
                            if matchedFlag : # matched
                                if data:
                                    retValue[crk] = { 'choice':v , 'data':data }
                                else:
                                    retValue[crk] = v
                                root = cmdRoot[crk]
                                newCmd += v + ' '
                                retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                self.copyAdditionalDictAndList(root,retValue)
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
                        data = None
                        if 'argument-type' in cmdRoot[focus] and isinstance(cmdRoot[focus]['argument-type'],(list,dict)) :
                            if self.debug:
                                print("cmdRoot[focus]['argument-type']:", cmdRoot[focus]['argument-type'])
                                for v in cmdRoot[focus]['argument-type']:
                                    print("     |->" , v)
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
                                    if self.debug:
                                        print("recommend list :",flush=True)
                                    print("help list :",flush=True)
                                    for s in cmdRoot[focus]['argument-type']:
                                        if longestMatch == s[:len(longestMatch)]:
                                            print('    ->',s , flush=True)
                                    # print('choose one from upper list.')
                                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                    self.cmd = newCmd
                                    # show recommendation
                                    # self._showRecommendation(root,retValue)
                                    if self.debug:
                                        print("longest matched command:",retValue)
                                    self.copyAdditionalDictAndList(root,retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                else : 
                                    newCmd = oldCmd
                                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                    self.cmd = newCmd
                                    if self.debug:
                                        print("not matched command:",retValue)
                                    self.copyAdditionalDictAndList(root,retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                            else :
                                data = cmdRoot[focus]['argument-type']
                        elif 'argument-type' in cmdRoot[focus]:
                            if self._checkArgumentType(v,cmdRoot[focus]['argument-type']) == False:
                                quoteFlag = self._changeQuoteFlag(quoteFlag,oldCmd)
                                self.cmd = oldCmd
                                retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                self.copyAdditionalDictAndList(root,retValue)
                                return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                        root = cmdRoot[focus]
                        if data:
                            retValue[focus] = { 'choice':v , 'data':data }
                        else:
                            retValue[focus] = v
                        retValue['__return__'] = newCmd.strip().replace('\t',' ')
                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                        self.cmd = newCmd
                        # show recommendation
                        self._showRecommendation(root,retValue)
                        if self.debug:
                            print("matched command:",retValue)
                        self.copyAdditionalDictAndList(root,retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
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
                        self.copyAdditionalDictAndList(root,retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
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
                                # if 'additionalList' in cmdRoot[focus]:
                                #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['additionalList'][int(v)])
                                # else : 
                                #     retLiteralCmdList.append(v)
                                # retValue['__literal_cmd__'] = retLiteralCmdList
                            else:
                                retCmdList.append(v)  # command
                                retValue['__cmd__'] = retCmdList
                                # if 'additionalList' in cmdRoot[focus]:
                                #     retLiteralCmdList.append(v + ":" + cmdRoot[focus]['additionalList'][int(v)])
                                # else : 
                                #     retLiteralCmdList.append(v)
                                # retValue['__literal_cmd__'] = retLiteralCmdList
                            retValue[focus] = v
                            retValue['__return__'] = newCmd.strip().replace('\t',' ')
                            quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                            self.cmd = newCmd
                            # show recommendation
                            self._showRecommendation(root,retValue)
                            self.copyAdditionalDictAndList(root,retValue)
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
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
                                if self.debug:
                                    print('recommend: ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                                print('    -> ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
                            self.copyAdditionalDictAndList(root,retValue)
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        else :  # cmd == "" 인 경우
            print("ERROR:words length", len(words) , words)

        self.copyAdditionalDictAndList(root,retValue)
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
            print(self.prompt, self.cmd.replace('\t',' '),end='',sep='',flush=True)
            while True:
                if self.debug:
                    print(flush=True)
                    print("quoteFlag:",quoteFlag," ",self.prompt,"/",self.cmd.replace("\t"," "),"/",self.cmd.replace("\t"," "),sep="",end="",flush=True)
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

