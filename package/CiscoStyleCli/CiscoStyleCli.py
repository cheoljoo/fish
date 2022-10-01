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

dateRe = re.compile('^\s*(?P<date>(?P<year>20[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+))')
intRe = re.compile('^\s*(?P<ans>[0-9\-\+]+)\s*$')
floatRe = re.compile('^\s*(?P<ans>[0-9\-\+\.]+)\s*$')
wordRe = re.compile('^\s*(?P<ans>[^ \n]+)')


class CiscoStyleCli:
    """ 
    This Class runs function from command string
    Cisco Style give the recommandation when you can use easily.
    if you do not know what you do , press space or tab.
    then CiscoStyleCli shows the recommendation with help description.
    
    1. interactive cisco command line interface
    from CiscoStyleCli import CiscoStyleCli
    csc = CiscoStyleCli.CiscoStyleCli()
    csc.run()
        - show the prompt to get your command (interactive mode)
        - press enter key , this function will return
    
    2. endless interactive cisco command line interface
    from CiscoStyleCli import CiscoStyleCli
    csc = CiscoStyleCli.CiscoStyleCli(infinite=True)
    csc.run() 
        - it has infinite loop
        - show the prompt to get your command (interactive mode)
        - you can quit when you meet quit command or quit()
    
    3. non-interactive run command
    from CiscoStyleCli import CiscoStyleCli
    csc = CiscoStyleCli.CiscoStyleCli()
    csc.runCommand(cmd)
        - run your command (non-interactive mode)
    
    :param rulePrintFile: file name to print the tree
    :param infinite: False (default) or True 
            True if you want infinite loop. 
            False if want to finish when you stroke 'return' key.
    :param prompt: your prompt
    :param debug: False (default) or True
            True if you want to print more information
    :param isUseDefaultCommon: True (default) or False
            False if you want not to show message when self._common runs
    """
    def __init__(self,rulePrintFile=None,infinite=False,prompt = "FISH~~:" , debug=False , isUseDefaultCommon = True):
        """ 
        initalize
        it has only 2 commands : quit , list
        
        :param rulePrintFile: file name to print the tree
        :param infinite: False (default) or True 
                True if you want infinite loop. 
                False if want to finish when you stroke 'return' key.
        :param prompt: your prompt
        :param debug: False (default) or True
                True if you want to print more information
        :param isUseDefaultCommon: True (default) or False
                False if you want not to show message when self._common runs
        """
        self.infinite = infinite
        self.debug = debug
        self.c = ''
        self.prompt = prompt
        self.remoteCmd = {}
        self.remoteCmd['cmd'] = {}
        self.rulePrintFile = rulePrintFile
        self._setCliDefault()
        self.isUseDefaultCommon = isUseDefaultCommon
        
        if self.debug :
            print("remoteCmd:",self.remoteCmd)
        self._checkReturnable(self.remoteCmd)
        if self.rulePrintFile:
            self._traverseFile(self.rulePrintFile,self.remoteCmd,"remoteCmd","w")
        self._list()
        
    def addCmd(self,root,command,type,returnable,desc,prefunc=None,returnfunc=None,additionalDict=None,additionalList=None):
        """ 
        add node (command type) in tree
        it is fixed string.
        
        :command tree example:
            gethost choose1 choose <CR>
            gethost choose2 target <CR>
            gethost choose3 shoot <CR>
            quit <CR>
            list <CR> detailed <CR>
            list <CR> simple <CR>

        :code example:
            from CiscoStyleCli import CiscoStyleCli
            csc = CiscoStyleCli.CiscoStyleCli()
            cmdTop = {}
            gethostCmd = csc.addCmd(cmdTop,'gethost','command',"", "gethosthelp")                                                            # level 1
            tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})        # level 2
            tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})     # level 3
            quitCmd = self.addCmd(cmdTop ,'quit','command',"returnable", "exit",returnfunc=self._quit)                                       # level 1
            listCmd = self.addCmd(cmdTop ,'list','command',"returnable", "show command line interface list",returnfunc=self._list)           # level 1
            tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self._listDetailed) # level 2
            tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self._listSimple)       # level 2
            csc.setCliRule(cmdTop)
        
        :param root: parent node
        :param command: command name - retValue will have dictionary {name:value}
        :param type: command
        :param returnable: 'returnable' when we run something after strike 'return' key.  
        :param desc: description
        :param prefunc: function pointer - it will be run if your command meets this function.  show the example to understand easily
        :param returnfunc: function pointer - it will be run when returnable == 'returnable' and you strike 'return' key.  default returnfunc=self._common
                v : {'__cmd__': ['gethost', 'choose3'], 'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}, '__return__': 'gethost choose3 2'}
                v : {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        :param additionalDict: give this information to argument of prefunc and returnfunc. 
                'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}
        :param additionalList: give this information to argument of prefunc and returnfunc. 
                'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}
        :return: current node of tree
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
        add node (argument type) in tree
        argument type means variable type. it is not fixed string. user should put the variant value.
            - argument type : int
            - argument type : str
            - argument type : float
            - argument type : [strA,strB,strC,...]  - list type : user can use one string in this list  (all are string)
            - argument type : { key1:value1 , key2:value2 , ...} - dictionary type : user can use one key in this dictionary (all key and value are string)
        
        :command tree example:
            gethost choose1 choose <CR>
            gethost choose2 target <CR>
            gethost choose3 shoot <CR>
            quit <CR>
            list <CR> detailed <CR>
            list <CR> simple <CR>

        :code example:
            from CiscoStyleCli import CiscoStyleCli
            csc = CiscoStyleCli.CiscoStyleCli()
            cmdTop = {}
            gethostCmd = csc.addCmd(cmdTop,'gethost','command',"", "gethosthelp")                                                            # level 1
            tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})        # level 2
            tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})     # level 3
            quitCmd = self.addCmd(cmdTop ,'quit','command',"returnable", "exit",returnfunc=self._quit)                                       # level 1
            listCmd = self.addCmd(cmdTop ,'list','command',"returnable", "show command line interface list",returnfunc=self._list)           # level 1
            tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self._listDetailed) # level 2
            tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self._listSimple)       # level 2
            csc.setCliRule(cmdTop)
        
        :param root: parent node
        :param name: argument name - retValue will have dictionary {name:value}
        :param type: argument type - int , float , str , list , dict
                when you use list and dict , it will give the recommendation with these list and dictionary contents (keys).
        :param returnable: 'returnable' when we run something after strike 'return' key.  
        :param desc: description
        :param prefunc: function pointer - it will be run if your command meets this function.  show the example to understand easily
        :param returnfunc: function pointer - it will be run when returnable == 'returnable' and you strike 'return' key.  default returnfunc=self._common
                v : {'__cmd__': ['gethost', 'choose3'], 'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}, '__return__': 'gethost choose3 2'}
                v : {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        :param additionalDict: give this information to argument of prefunc and returnfunc. 
                'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}
        :param additionalList: give this information to argument of prefunc and returnfunc. 
                'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}
        :return: current node of tree
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
    
        
    def _setCliDefault(self):
        if 'cmd' in self.remoteCmd and 'quit' not in self.remoteCmd['cmd']:
            quitCmd = self.addCmd(self.remoteCmd ,'quit','command',"returnable", "exit",returnfunc=self._quit)
        if 'cmd' in self.remoteCmd and 'list' not in self.remoteCmd['cmd']:
            listCmd = self.addCmd(self.remoteCmd ,'list','command',"returnable", "show command line interface list",returnfunc=self._list)
            tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self._listDetailed)
            tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self._listSimple)
            
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
            if v and '__attribute' in v:
                if 'type' in v['__attribute']:
                    type = v['__attribute']['type']
                if 'returnable' in v['__attribute']:
                    returnable = v['__attribute']['returnable']
                if 'desc' in v['__attribute']:
                    desc = v['__attribute']['desc']
                if 'argument-type' in v['__attribute']:
                    argumentType = v['__attribute']['argument-type']
            if type == 'argument':
                tmpRoot = self.addArgument(root,k,argumentType,returnable,desc)
            else:
                tmpRoot = self.addCmd(root,k,'command',returnable,desc)
            if v and (('__attribute' in v and len(v) > 1) or ('__attribute' not in v and len(v) > 0)):
                self._setCliRuleTcmdRecursive(tmpRoot,v)
            
    def setCliRuleTcmd(self,top):
        """ 
        set rule for our tiger project (Tcmd : Tiger Command)
        it has different sequence of dictionary tree.
        finally it set the self._comon(v) when returnable is on or this is last token (word).
          and it will add 'list' and 'quit' command automatically if you do not set it.
        
        :code example:
            TOP = {}
            projectList = ['tiger','cheetah','fish']
            TOP ['register'] = {
                '__attribute' : {
                    'type' : "command",
                    'desc' : "registration~~",
                    'returnable' : "returnable"
                    },
                'name' : {
                    '__attribute' : {
                        'type' : "command",
                        'desc' : "name~~",
                        'returnable' : "",
                    }
                },
                'target' : {
                    'next-target' : {}
                },
                'target2' : {
                    'next2-target' : {
                        '__attribute' : {
                            'desc' : "next target",
                            'returnable' : "",
                        }
                    }
                },
                'vbee' : {
                    'project' : {
                        '__attribute' : {
                            'desc' : "choose from list",
                            'type' : 'argument',
                            'argument-type' : projectList
                        }
                    }
                }
            }
            csc.setCliRuleTcmd(TOP)

        if you do not '__attribute' , we will set as default
            ['__attribute']['returnable'] = ""
            ['__attribute']['type'] = 'command'
            ['__attribute']['returnable'] = ""
            ['__attribute']['desc'] = ""
            ['__attribute']['argument-type'] = None
            if you want to use dictionary or list , 
                ['__attribute']['type'] = 'argument'
                ['__attribute']['argument-type'] = one dimentional dictionary or list

        verification method: you can show the tree with the following command
            list<CR>
            list simple<CR>
            list detailed<CR>
        
        Args:
            top(dict) : rule dictionary tree with different type
        """
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        self.remoteCmd = {}
        self._setCliRuleTcmdRecursive(self.remoteCmd,top)
        
        self._setCliDefault()
        self._checkReturnable(self.remoteCmd)
        if self.rulePrintFile:
            self._traverseFile(self.rulePrintFile,self.remoteCmd,"remoteCmd","w")
        self._listSimple()

    def setCliRule(self,rule):
        """ 
        set rule 
        rule is generated from addCmd() and addArgument() functions.
        finally it set the self._comon(v) when returnable is on or this is last token (word).
          and it will add 'list' and 'quit' command automatically if you do not set it.
        
        :code example:
            from CiscoStyleCli import CiscoStyleCli
            csc = CiscoStyleCli.CiscoStyleCli()
            remoteCmd = {}
            gethostCmd = csc.addCmd(remoteCmd,'gethost','command',"", "gethosthelp")
            tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})
            tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})
            tmp = csc.addCmd(gethostCmd,'choose2','command',"", "choose type2",additionalDict={'0':'tiger','1':'animal'})
            tmp = csc.addArgument(tmp,'target',['cheetah','tiger','fish','turtle','tigiris'],"returnable", "type from the list")
            tmp = csc.addCmd(gethostCmd,'choose3','command',"", "choose type3",additionalDict={'0':'tiger','1':'animal'})
            tmp = csc.addArgument(tmp,'shoot',{'0':'car','1':'tiger','2':'telematics'},"returnable", "type key from the dictionary")
            csc.setCliRule(remoteCmd)
        
        verification method: you can show the tree with the following command
            list<CR>
            list simple<CR>
            list detailed<CR>
            
        Args:
            rule (dict): rule dictionary tree made by addCmd() and addArgument()
        """
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        self.remoteCmd = rule
        self._setCliDefault()
        self._checkReturnable(self.remoteCmd)
        if self.rulePrintFile:
            self._traverseFile(self.rulePrintFile,self.remoteCmd,"remoteCmd","w")
        self._listSimple()
    
    def _quit(self,v=None):
        print("byebye!!   see you again~~   *^^*")
        quit()
    
    def _list(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self,v)
        self._traverseList(self.remoteCmd,"")
        for s in self.tlist:
            print(s)
        print()
    def _listDetailed(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self,v)
        self._traverseList(self.remoteCmd,"",detailed=True)
        for s in self.tlist:
            print(s)
        print()
    def _listSimple(self,v=None):
        self.tlist = []
        functionNameAsString = sys._getframe().f_code.co_name
        print("functionname:",functionNameAsString)
        if self.debug:
            print(self,v)
        self._traverseList(self.remoteCmd,"",detailed=True,simple=True)
        for s in self.tlist:
            print(s)
        print()
    def _traverseList(self,vv,start:str,detailed=False,simple=False):
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
                            self._traverseList(v,start + " " + k + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self._traverseList(v,start + " " + k  + rt,detailed,simple)
                    elif detailed:
                        prefunc = ""
                        if 'prefunc' in v:
                            prefunc = " pre-func" + str(v['prefunc'])
                        returnfunc = ""
                        if 'returnfunc' in v:
                            returnfunc = " ret-func:" + str(v['returnfunc'])
                        if 'type' in v and v['type'] != 'argument': 
                            self._traverseList(v,start + " (commands) " + prefunc + k  + returnfunc + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self._traverseList(v,start + " (argument:" + str(argtype) +") " + prefunc + k + returnfunc + rt,detailed,simple)
                    else:
                        if 'type' in v and v['type'] != 'argument': 
                            self._traverseList(v,start + " (commands) " + k  + rt,detailed,simple)
                        else:
                            argtype = v['argument-type']
                            self._traverseList(v,start + " (argument:" + str(argtype) + ") " + k  + rt,detailed,simple)
            else:
                if self.debug:
                    print("start:",start)
                self.tlist.append(start)
        # else :
        #     print(start ,  " = '''", vv , "'''", sep="", file=f)

    def _getch(self):
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

    def _copyAdditionalDictAndList(self,_from,_to):
        if 'additionalDict' in _from:
            for adk,adv in _from['additionalDict'].items():
                if '__additionalDict__' not in _to:
                    _to['__additionalDict__'] = {}
                _to['__additionalDict__'][adk] = adv
        if 'additionalList' in _from:
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
    # def findRoot(self,cmd):
    #     """ 
    #     while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
    #     'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
    #     prevCmd = 'gethost'가 들어가면 안성맞춤이다.
    #     """
    #     functionNameAsString = sys._getframe().f_code.co_name
    #     if self.debug : 
    #         print("functionname:",functionNameAsString)
    #     retValue = {}
    #     retCmdList = []
    #     retLiteralCmdList = []
    #     words = cmd.strip().split(' ')
    #     root = self.remoteCmd
    #     lastWord = ""
    #     newCmd = ""
    #     #if self.cmd == "":
    #     #    return (root,lastWord,retValue,quoteFlag)
    #     #elif self.cmd[0] == ' ':        # self.cmd != ""
    #     #    return (root,lastWord,retValue,quoteFlag)
    #     # while에서는 root를 tree에 따라 변경시켜주는 일을 한다.
    #     # 'gethost' 라고 하면 root = root['cmd']['gethost'] 으로 변경되어 , root['type'] 부터 볼수 있는 것을 의미한다. 
    #     # prevCmd = 'gethost'가 들어가면 안성맞춤이다.
    #     while len(words):
    #         prevRoot = root
    #         v = words.pop(0)
    #         lastWord = v
    #         if self.debug:
    #             print("get word : v :",v)
    #             print("root:",root)
    #             print("words:",words)
    #             print("retValue:",retValue)
    #         if words :  # 마지막 word가 아니면 
    #             if 'cmd' in root:
    #                 cmdRoot = root['cmd']
    #                 if self.debug:
    #                     print("v:",v,"checkCmd:cmd:keys",cmdRoot.keys())
    #                 # matched command
    #                 if v in cmdRoot and cmdRoot[v]['type'] == 'command':
    #                     root = cmdRoot[v]
    #                     newCmd += v + ' '
    #                     continue
    #                 # matched argument
    #                 for crk, crv in cmdRoot.items():
    #                     if cmdRoot[crk]['type'] == 'argument':
    #                         if 'argument-type' in cmdRoot[crk] and isinstance(cmdRoot[crk]['argument-type'],(list,dict)) :
    #                             if v not in cmdRoot[crk]['argument-type']:
    #                                 returnValue = -1
    #                                 return (returnValue,prevRoot,root,lastWord,newCmd)  # returnValue == -1 : not matched
    #                         root = cmdRoot[crk]
    #                         newCmd += v + ' '
    #                         continue
    #             returnValue = -1
    #             return (returnValue,prevRoot,root,lastWord,newCmd) # returnValue == -1 : not matched
    def _common(self,v=None):
        if not self.isUseDefaultCommon:
            return
        functionNameAsString = sys._getframe().f_code.co_name
        print("This is common type of prefunc and returnfunc function argument.")
        print("functionname:",functionNameAsString)
        if v:
            print("function argument: v :",v)
        print("Warning : set your returnfunc. this is templae function of prefunc and returnfunc argument.")
        
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
                print('    -> ({})'.format(t) , s , "-" , cmdRoot[s]['desc'] ,returnable , flush=True)
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
        check whether this cmd is right and run registered function in prefunc and returnfunc arguments of addArgument() or addCmd()
        return the location from rootCmd following cmd  for guiding current and next arguments
        self.c : current input character
        
        flows
            - while process each token (word) before last token (word)
                move the next tree node each token
                return current node if token has wrong input against tree
            - process last token (word)
                if input is return character,
                    if returnable , run returnfunc
                if input is space or tab character,
                    find longestmatch
            - return retValue
        call function of prefunc and returnfunc
            - prefunc and returnfunc has only one dictionary argument including all information
        
        :param cmd: input command line
        :return root: node of tree for next argument.
        :return lastWord: last stroke word
        :return retValue: all your input information
                example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        :return quoteflag: False or True according to the quotation counts
        :return isFinishedFromReturn: False or True.   if it returns from input "return" , it is True.
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
            print("cmd:[",cmd,"]",sep="")
            print("checkCmd:words:",words)

        root = self.remoteCmd
        lastWord = ""
        newCmd = ""
        # while process before last word
        # when we exist while loop , we should process the last word.
        # we will process last word in sentence with [LAST_WORD]
        while len(words) > 1:
            prevRoot = root
            v = words.pop(0)
            lastWord = v
            if self.debug:
                print("get word : v :",v)
                print("root:",root)
                print("words:",words)
                print("retValue:",retValue)
            if words :  # not last word  (exit the loop if it is last word)
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
                                        self._copyAdditionalDictAndList(root,retValue)
                                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                elif 'argument-type' in cmdRoot[crk]:
                                    if self._checkArgumentType(v,cmdRoot[crk]['argument-type']) == False:
                                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                        self.cmd = newCmd
                                        retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                        self._copyAdditionalDictAndList(root,retValue)
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
                    self._copyAdditionalDictAndList(root,retValue)
                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        # last word of command
        # [LAST_WORD]
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
                    self._copyAdditionalDictAndList(root,retValue)
                    if self.debug:
                        print('matched command : check returnable : root:',root)
                    if 'returnable' in root and root['returnable'] == 'returnable':
                        if 'returnfunc' in root and root['returnfunc']:
                            if self.debug:
                                print('matched command returnfunc:',root['returnfunc'])
                                print("matched command retValue:",retValue)
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
                                self._copyAdditionalDictAndList(root,retValue)
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
                                self._copyAdditionalDictAndList(root,retValue)
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
                # 우리는 focusType (즉, argument , command)로 나누어 처리한다.   we have only two type (argument or command)
                # argument일때는 딱 1개만 존재하게 되고, argument와 command가 같이 있다면 무조건 argument가 우선순위가 높다.
                #    it can have only zero or one argument. but it can have many commands if it does not have argument.
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
                                    self._copyAdditionalDictAndList(root,retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                                else : 
                                    newCmd = oldCmd
                                    retValue['__return__'] = newCmd.strip().replace('\t',' ')
                                    quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                                    self.cmd = newCmd
                                    if self.debug:
                                        print("not matched command:",retValue)
                                    self._copyAdditionalDictAndList(root,retValue)
                                    return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                            else :
                                data = cmdRoot[focus]['argument-type']
                        elif 'argument-type' in cmdRoot[focus]:
                            if self._checkArgumentType(v,cmdRoot[focus]['argument-type']) == False:
                                quoteFlag = self._changeQuoteFlag(quoteFlag,oldCmd)
                                self.cmd = oldCmd
                                retValue['__return__'] = self.cmd.strip().replace('\t',' ')
                                self._copyAdditionalDictAndList(root,retValue)
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
                        self._copyAdditionalDictAndList(root,retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                else: # command
                    if focus and len(matched) <= 1:  # matched only 1 command
                        newCmd += v + " "
                        root = cmdRoot[focus]
                        retCmdList.append(v)  # command
                        retValue['__cmd__'] = retCmdList
                        retValue['__return__'] = newCmd.strip().replace('\t',' ')
                        quoteFlag = self._changeQuoteFlag(quoteFlag,newCmd)
                        self.cmd = newCmd
                        # show recommendation
                        self._showRecommendation(root,retValue)
                        self._copyAdditionalDictAndList(root,retValue)
                        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
                    else :  # not matched
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
                            self._copyAdditionalDictAndList(root,retValue)
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
                            self._copyAdditionalDictAndList(root,retValue)
                            return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)
        else :  # cmd == "" 인 경우
            print("ERROR:words length", len(words) , words)

        self._copyAdditionalDictAndList(root,retValue)
        return (root,lastWord,retValue,quoteFlag,isFinishedFromReturn)


    def _checkReturnable(self,root):
        if 'cmd' in root:
            rootCmd = root['cmd']
            for k,v in rootCmd.items():
                if 'cmd' in rootCmd[k]:
                    self._checkReturnable(rootCmd[k])
                else:
                    rootCmd[k]['returnable'] = 'returnable'
                if 'returnable' in rootCmd[k] and rootCmd[k]['returnable'] == 'returnable':
                    if 'returnfunc' not in rootCmd[k] or not rootCmd[k]['returnfunc']:
                        rootCmd[k]['returnfunc'] = self._common
        return
            
    def run(self):
        """ 
        main part of cisco command line interface
        meet the prompt for your input
        get string from your input
        run() will have infinite loop before meeting quit() if you set infinite argument in __init__() as True.
        :return: retValue with all your input information
                example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        """

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
                c = self._getch()
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

    def _traverseFD(self,f,vv,start:str):
        # print(start," ",file=f)
        if isinstance(vv, dict):
            print(start ,  " = {}", sep="", file=f)
            for k, v in vv.items():
                self._traverseFD(f,v,start + "['" + str(k)  + "']")
        elif isinstance(vv, (list, tuple)):
            for i, x in enumerate(vv):
                self._traverseFD(f,x,start + "[list:" + str(i) + "]" )
        else :
            print(start ,  " = '''", vv , "'''", sep="", file=f)

    def _traverseFile(self,filename:str,v,start:str,att):
        with open(filename, att, encoding='utf-8', errors='ignore') as f:
            self._traverseFD(f,v,start)
    
    def runCommand(self,cmd):
        """ 
        non-interactive run command
        
        :param cmd: retValue with all your input information
                example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        """
        functionNameAsString = sys._getframe().f_code.co_name
        if self.debug : 
            print("functionname:",functionNameAsString)
        self.c = '\n'
        root , lastCmd , retValue , quoteFlag , isFinishedFromReturn = self.checkCmd(cmd)
        if self.debug:
            print('quoteFlag:',quoteFlag, "isFinishedFromReturn:",isFinishedFromReturn)
            print('lastCmd:', lastCmd , 'retValue:',retValue)

