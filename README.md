- [1. fish](#1-fish)
  - [1.1. main](#11-main)
  - [1.2. RemoteCommand Class](#12-remotecommand-class)
- [2. library](#2-library)
  - [2.1. Cisco Style Cli](#21-cisco-style-cli)
  - [2.2. CiscoStyleCli Class](#22-ciscostylecli-class)
    - [2.2.1. document](#221-document)
  - [2.3. make package and distribute python module](#23-make-package-and-distribute-python-module)
    - [2.3.1. file tree to make a python module](#231-file-tree-to-make-a-python-module)
      - [2.3.1.1. LICENSE](#2311-license)
      - [2.3.1.2. pyproject.toml](#2312-pyprojecttoml)
      - [2.3.1.3. README.md](#2313-readmemd)
      - [2.3.1.4. setup.py](#2314-setuppy)
      - [2.3.1.5. CiscoStyleCli.py](#2315-ciscostyleclipy)
      - [2.3.1.6. __init__.py](#2316-initpy)
    - [2.3.2. make package](#232-make-package)
    - [2.3.3. test](#233-test)
    - [2.3.4. reference links](#234-reference-links)
- [3. how to run](#3-how-to-run)
  - [3.1. run (normal mode)](#31-run-normal-mode)
  - [3.2. run (debug mode)](#32-run-debug-mode)
  - [3.3. run (tiger command style)](#33-run-tiger-command-style)
  - [3.4. run (infinite mode)](#34-run-infinite-mode)
  - [3.5. others](#35-others)
- [4. asciicast2gif : convert asciinema record to gif](#4-asciicast2gif--convert-asciinema-record-to-gif)
  - [4.1. working process](#41-working-process)
  - [4.2. how to run asciicast2gif](#42-how-to-run-asciicast2gif)
  - [4.3. samples for FISH and Cisco Style Cli](#43-samples-for-fish-and-cisco-style-cli)
  - [4.4. reference links](#44-reference-links)
- [5. DESIGN](#5-design)

--------

# 1. fish
FISH (Funny sImple distributed system with rSH through sSH)

## 1.1. main
- use RemoteCommand Class to run remote works
- use CiscoStyleCli Class to get input
- set rules for Remotecommand

## 1.2. RemoteCommand Class
- add database for user and server
- input/output file
    - fish.csv : user and server database

# 2. library
## 2.1. Cisco Style Cli
- Use pypi : https://pypi.org/project/ciscostylecli/

## 2.2. CiscoStyleCli Class
- structure
    - type : command (fixed value) or argument(variant value)
    - returnable : whether you can end or not although you strike the [return] key.
    - desc : description for help
    - prefunc : run this function before reach this command
    - return func : run this function when you reach this command
- quit[return] is possbile.  before changing , we can input [return] after spacebar.
- add running function without parameter. 
    - we can put the function-name at last parameter of addArgument() and addCmd().
    - and we should bind between function-name and real function pointer with setFunc("listTable",rc.listTable)
- setCliRule
    - set user rule
- basic command
    - list : show the command structure
    - quit : quit from this program
- you can not get out from this class when you meet the [returnable] or the end of command although you strke [return] key.
- output file
    - rulePrint.py : rule information

### 2.2.1. document
- ```
    python3
    >> import CiscoStyleCli
    >> help(CiscoStyleCli)
  ```
- ```python3 -m pydoc CiscoStyleCli > CiscoStyleCli.txt```

- ```
    Help on module CiscoStyleCli:

    NAME
        CiscoStyleCli

    CLASSES
        builtins.object
            CiscoStyleCli
        
        class CiscoStyleCli(builtins.object)
        |  CiscoStyleCli(rulePrintFile=None, infinite=False, prompt='FISH~~:', debug=False, isUseDefaultCommon=True)
        |  
        |  This Class runs function from command string
        |  Cisco Style give the recommandation when you can use easily.
        |  if you do not know what you do , press space or tab.
        |  then CiscoStyleCli shows the recommendation with help description.
        |  
        |  1. interactive cisco command line interface
        |  from CiscoStyleCli import CiscoStyleCli
        |  csc = CiscoStyleCli.CiscoStyleCli()
        |  csc.run()
        |      - show the prompt to get your command (interactive mode)
        |      - press enter key , this function will return
        |  
        |  2. endless interactive cisco command line interface
        |  from CiscoStyleCli import CiscoStyleCli
        |  csc = CiscoStyleCli.CiscoStyleCli(infinite=True)
        |  csc.run() 
        |      - it has infinite loop
        |      - show the prompt to get your command (interactive mode)
        |      - you can quit when you meet quit command or quit()
        |  
        |  3. non-interactive run command
        |  from CiscoStyleCli import CiscoStyleCli
        |  csc = CiscoStyleCli.CiscoStyleCli()
        |  csc.runCommand(cmd)
        |      - run your command (non-interactive mode)
        |  
        |  :param rulePrintFile: file name to print the tree
        |  :param infinite: False (default) or True 
        |          True if you want infinite loop. 
        |          False if want to finish when you stroke 'return' key.
        |  :param prompt: your prompt
        |  :param debug: False (default) or True
        |          True if you want to print more information
        |  :param isUseDefaultCommon: True (default) or False
        |          False if you want not to show message when self._common runs
        |  
        |  Methods defined here:
        |  
        |  __init__(self, rulePrintFile=None, infinite=False, prompt='FISH~~:', debug=False, isUseDefaultCommon=True)
        |      initalize
        |      it has only 2 commands : quit , list
        |      
        |      :param rulePrintFile: file name to print the tree
        |      :param infinite: False (default) or True 
        |              True if you want infinite loop. 
        |              False if want to finish when you stroke 'return' key.
        |      :param prompt: your prompt
        |      :param debug: False (default) or True
        |              True if you want to print more information
        |      :param isUseDefaultCommon: True (default) or False
        |              False if you want not to show message when self._common runs
        |  
        |  addArgument(self, root, name, type, returnable, desc, prefunc=None, returnfunc=None, additionalDict=None, additionalList=None)
        |      add node (argument type) in tree
        |      argument type means variable type. it is not fixed string. user should put the variant value.
        |          - argument type : int
        |          - argument type : str
        |          - argument type : float
        |          - argument type : [strA,strB,strC,...]  - list type : user can use one string in this list  (all are string)
        |          - argument type : { key1:value1 , key2:value2 , ...} - dictionary type : user can use one key in this dictionary (all key and value are string)
        |      
        |      :command tree example:
        |          gethost choose1 choose <CR>
        |          gethost choose2 target <CR>
        |          gethost choose3 shoot <CR>
        |          quit <CR>
        |          list <CR> detailed <CR>
        |          list <CR> simple <CR>
        |      
        |      :code example:
        |          from CiscoStyleCli import CiscoStyleCli
        |          csc = CiscoStyleCli.CiscoStyleCli()
        |          cmdTop = {}
        |          gethostCmd = csc.addCmd(cmdTop,'gethost','command',"", "gethosthelp")                                                            # level 1
        |          tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})        # level 2
        |          tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})     # level 3
        |          quitCmd = self.addCmd(cmdTop ,'quit','command',"returnable", "exit",returnfunc=self._quit)                                       # level 1
        |          listCmd = self.addCmd(cmdTop ,'list','command',"returnable", "show command line interface list",returnfunc=self._list)           # level 1
        |          tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self._listDetailed) # level 2
        |          tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self._listSimple)       # level 2
        |          csc.setCliRule(cmdTop)
        |      
        |      :param root: parent node
        |      :param name: argument name - retValue will have dictionary {name:value}
        |      :param type: argument type - int , float , str , list , dict
        |              when you use list and dict , it will give the recommendation with these list and dictionary contents (keys).
        |      :param returnable: 'returnable' when we run something after strike 'return' key.  
        |      :param desc: description
        |      :param prefunc: function pointer - it will be run if your command meets this function.  show the example to understand easily
        |      :param returnfunc: function pointer - it will be run when returnable == 'returnable' and you strike 'return' key.  default returnfunc=self._common
        |              v : {'__cmd__': ['gethost', 'choose3'], 'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}, '__return__': 'gethost choose3 2'}
        |              v : {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        |      :param additionalDict: give this information to argument of prefunc and returnfunc. 
        |              'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}
        |      :param additionalList: give this information to argument of prefunc and returnfunc. 
        |              'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}
        |      :return: current node of tree
        |  
        |  addCmd(self, root, command, type, returnable, desc, prefunc=None, returnfunc=None, additionalDict=None, additionalList=None)
        |      add node (command type) in tree
        |      it is fixed string.
        |      
        |      :command tree example:
        |          gethost choose1 choose <CR>
        |          gethost choose2 target <CR>
        |          gethost choose3 shoot <CR>
        |          quit <CR>
        |          list <CR> detailed <CR>
        |          list <CR> simple <CR>
        |      
        |      :code example:
        |          from CiscoStyleCli import CiscoStyleCli
        |          csc = CiscoStyleCli.CiscoStyleCli()
        |          cmdTop = {}
        |          gethostCmd = csc.addCmd(cmdTop,'gethost','command',"", "gethosthelp")                                                            # level 1
        |          tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})        # level 2
        |          tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})     # level 3
        |          quitCmd = self.addCmd(cmdTop ,'quit','command',"returnable", "exit",returnfunc=self._quit)                                       # level 1
        |          listCmd = self.addCmd(cmdTop ,'list','command',"returnable", "show command line interface list",returnfunc=self._list)           # level 1
        |          tmp = self.addCmd(listCmd ,'detailed','command',"returnable", "show detailed command line interface list",returnfunc=self._listDetailed) # level 2
        |          tmp = self.addCmd(listCmd ,'simple','command',"returnable", "show simple command line interface list",returnfunc=self._listSimple)       # level 2
        |          csc.setCliRule(cmdTop)
        |      
        |      :param root: parent node
        |      :param command: command name - retValue will have dictionary {name:value}
        |      :param type: command
        |      :param returnable: 'returnable' when we run something after strike 'return' key.  
        |      :param desc: description
        |      :param prefunc: function pointer - it will be run if your command meets this function.  show the example to understand easily
        |      :param returnfunc: function pointer - it will be run when returnable == 'returnable' and you strike 'return' key.  default returnfunc=self._common
        |              v : {'__cmd__': ['gethost', 'choose3'], 'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}, '__return__': 'gethost choose3 2'}
        |              v : {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        |      :param additionalDict: give this information to argument of prefunc and returnfunc. 
        |              'shoot': {'choice': '2', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}
        |      :param additionalList: give this information to argument of prefunc and returnfunc. 
        |              'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}
        |      :return: current node of tree
        |  
        |  checkCmd(self, cmd)
        |      check whether this cmd is right and run registered function in prefunc and returnfunc arguments of addArgument() or addCmd()
        |      return the location from rootCmd following cmd  for guiding current and next arguments
        |      self.c : current input character
        |      
        |      flows
        |          - while process each token (word) before last token (word)
        |              move the next tree node each token
        |              return current node if token has wrong input against tree
        |          - process last token (word)
        |              if input is return character,
        |                  if returnable , run returnfunc
        |              if input is space or tab character,
        |                  find longestmatch
        |          - return retValue
        |      call function of prefunc and returnfunc
        |          - prefunc and returnfunc has only one dictionary argument including all information
        |      
        |      :param cmd: input command line
        |      :return root: node of tree for next argument.
        |      :return lastWord: last stroke word
        |      :return retValue: all your input information
        |              example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        |      :return quoteflag: False or True according to the quotation counts
        |      :return isFinishedFromReturn: False or True.   if it returns from input "return" , it is True.
        |  
        |  run(self)
        |      main part of cisco command line interface
        |      meet the prompt for your input
        |      get string from your input
        |      run() will have infinite loop before meeting quit() if you set infinite argument in __init__() as True.
        |      :return: retValue with all your input information
        |              example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        |  
        |  runCommand(self, cmd)
        |      non-interactive run command
        |      
        |      :param cmd: retValue with all your input information
        |              example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}
        |  
        |  setCliRule(self, rule)
        |      set rule 
        |      rule is generated from addCmd() and addArgument() functions.
        |      finally it set the self._comon(v) when returnable is on or this is last token (word).
        |        and it will add 'list' and 'quit' command automatically if you do not set it.
        |      
        |      :code example:
        |          from CiscoStyleCli import CiscoStyleCli
        |          csc = CiscoStyleCli.CiscoStyleCli()
        |          remoteCmd = {}
        |          gethostCmd = csc.addCmd(remoteCmd,'gethost','command',"", "gethosthelp")
        |          tmp = csc.addCmd(gethostCmd,'choose1','command',"", "choose type1",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})
        |          tmp = csc.addArgument(tmp,'choose','int',"returnable", "type integer",prefunc=rc.showHost,additionalDict={'0':'tiger','1':'animal'})
        |          tmp = csc.addCmd(gethostCmd,'choose2','command',"", "choose type2",additionalDict={'0':'tiger','1':'animal'})
        |          tmp = csc.addArgument(tmp,'target',['cheetah','tiger','fish','turtle','tigiris'],"returnable", "type from the list")
        |          tmp = csc.addCmd(gethostCmd,'choose3','command',"", "choose type3",additionalDict={'0':'tiger','1':'animal'})
        |          tmp = csc.addArgument(tmp,'shoot',{'0':'car','1':'tiger','2':'telematics'},"returnable", "type key from the dictionary")
        |          csc.setCliRule(remoteCmd)
        |      
        |      verification method: you can show the tree with the following command
        |          list<CR>
        |          list simple<CR>
        |          list detailed<CR>
        |          
        |      Args:
        |          rule (dict): rule dictionary tree made by addCmd() and addArgument()
        |  
        |  setCliRuleTcmd(self, top)
        |      set rule for our tiger project (Tcmd : Tiger Command)
        |      it has different sequence of dictionary tree.
        |      finally it set the self._comon(v) when returnable is on or this is last token (word).
        |        and it will add 'list' and 'quit' command automatically if you do not set it.
        |      
        |      :code example:
        |          TOP = {}
        |          projectList = ['tiger','cheetah','fish']
        |          TOP ['register'] = {
        |              '__attribute' : {
        |                  'type' : "command",
        |                  'desc' : "registration~~",
        |                  'returnable' : "returnable"
        |                  },
        |              'name' : {
        |                  '__attribute' : {
        |                      'type' : "command",
        |                      'desc' : "name~~",
        |                      'returnable' : "",
        |                  }
        |              },
        |              'target' : {
        |                  'next-target' : {}
        |              },
        |              'target2' : {
        |                  'next2-target' : {
        |                      '__attribute' : {
        |                          'desc' : "next target",
        |                          'returnable' : "",
        |                      }
        |                  }
        |              },
        |              'vbee' : {
        |                  'project' : {
        |                      '__attribute' : {
        |                          'desc' : "choose from list",
        |                          'type' : 'argument',
        |                          'argument-type' : projectList
        |                      }
        |                  }
        |              }
        |          }
        |          csc.setCliRuleTcmd(TOP)
        |      
        |      if you do not '__attribute' , we will set as default
        |          ['__attribute']['returnable'] = ""
        |          ['__attribute']['type'] = 'command'
        |          ['__attribute']['returnable'] = ""
        |          ['__attribute']['desc'] = ""
        |          ['__attribute']['argument-type'] = None
        |          if you want to use dictionary or list , 
        |              ['__attribute']['type'] = 'argument'
        |              ['__attribute']['argument-type'] = one dimentional dictionary or list
        |      
        |      verification method: you can show the tree with the following command
        |          list<CR>
        |          list simple<CR>
        |          list detailed<CR>
        |      
        |      Args:
        |          top(dict) : rule dictionary tree with different type
        |  
  ```

## 2.3. make package and distribute python module
- FISH project includes CiscoStyleCli python module
  - refer to https://github.com/cheoljoo/fish/tree/main/package

### 2.3.1. file tree to make a python module
- need the following file to make a python module
- ```txt
    .
    ├── CiscoStyleCli
    │   ├── CiscoStyleCli.py
    │   └── __init__.py
    ├── LICENSE
    ├── pyproject.toml
    ├── README.md
    └── setup.py
    ```
#### 2.3.1.1. LICENSE
- it is [MIT LICENSE](https://github.com/cheoljoo/fish/blob/main/package/LICENSE)
#### 2.3.1.2. pyproject.toml
- toml file : i do not know well. just copy it to use.
#### 2.3.1.3. README.md 
- this information will be used in pypi pages.
#### 2.3.1.4. [setup.py](https://github.com/cheoljoo/fish/blob/main/package/setup.py)
- name : lower characters
- version : increase version when you update
- py_modules , packages : use your class name (CiscoStyleCli)
#### 2.3.1.5. CiscoStyleCli.py
- your python class file
#### 2.3.1.6. __init__.py
- change it


### 2.3.2. make package
- ```
    cd package
    python3 -m pip install --upgrade setuptools wheel
    python3 setup.py sdist bdist_wheel
    ```
    - verify the result
    ```txt
    package/dist  $  ls -l
    total 40
    -rw-rw-r-- 1 cheoljoo.lee cheoljoo.lee 15326 Sep 30 23:04 ciscostylecli-1.0.0.0-py3-none-any.whl
    -rw-rw-r-- 1 cheoljoo.lee cheoljoo.lee 15483 Sep 30 23:04 ciscostylecli-1.0.0.0.tar.gz
  ```
### 2.3.2. upload package (distribution)
- ```
    cd package
    python3 -m pip install --upgrade twine
    python3 -m twine upload --skip-existing dist/*
    pypi's id and passwd
  ```

### 2.3.3. test
- ```
    python3 -m pip install ciscostylecsc
    cd package
    python3 test.py
    functionname: _list
    (commands) quit <CR>
    (commands) list <CR> (commands) detailed <CR>
    (commands) list <CR> (commands) simple <CR>


        This Class runs function from command string
        Cisco Style give the recommandation when you can use easily.
        if you do not know what you do , press space or tab.
        then CiscoStyleCli shows the recommendation with help description.

        1. interactive cisco command line interface
        csc = CiscoStyleCli()
        csc.run()
            - show the prompt to get your command (interactive mode)
            - press enter key , this function will return

        2. endless interactive cisco command line interface
        csc = CiscoStyleCli(infinite=True)
        csc.run()
            - it has infinite loop
            - show the prompt to get your command (interactive mode)
            - you can quit when you meet quit command or quit()

        3. non-interactive run command
        csc = CiscoStyleCli()
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


    recommend list: quit  list
        -> (command) quit - exit [returnable]
        -> (command) list - show command line interface list [returnable]
    FISH~~:list
    returnfunc <bound method CiscoStyleCli._list of <CiscoStyleCli.CiscoStyleCli.CiscoStyleCli object at 0x7faec8e8ccd0>>
    functionname: _list
    (commands) quit <CR>
    (commands) list <CR> (commands) detailed <CR>
    (commands) list <CR> (commands) simple <CR>
  ```

### 2.3.4. reference links
- https://valuefactory.tistory.com/565
- https://stackoverflow.com/questions/52016336/how-to-upload-new-versions-of-project-to-pypi-with-twine
- https://rampart81.github.io/post/python_package_publish/
- https://jammdev.tistory.com/34
- https://www.holaxprogramming.com/2017/06/28/python-project-structures/



# 3. how to run
## 3.1. run (normal mode)
- python3 fish.py
    - output
        - ```txt
          python3 fish.py
          python3 fish.py
          ['/data01/cheoljoo.lee/code/fish', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/data01/cheoljoo.lee/code/problemSolving/2022/a/lib/python3.8/site-packages']
          the simple distributed compile environment remotely
          input:
          recommend: register  enable  disable  list  run  test

          input:re


          recommend: <CR>
          recommend: (argument) name - system nickname

          input:register n


          recommend: (argument) id - login id

          input:register n i


          recommend: (argument) host - hostname

          input:register n i h


          recommend: (argument) passwd - password

          input:register n i h p


          recommend: (argument) directory - output directory

          input:register n i h p d


          recommend: (argument) email - email address

          input:register n i h p d e


          recommend: <CR>

          input:register n i h p d e cmd=[register n i h p d e]
          retValue: {'name': 'n', 'id': 'i', 'host': 'h', 'passwd': 'p', 'directory': 'd', 'email': 'e', '__cmd__': ['register'], '__return__': 'register n i h p d e'}
          ```
    - return value
        - ```retValue: {'name': 'n', 'id': 'i', 'host': 'h', 'passwd': 'p', 'directory': 'd', 'email': 'e', '__cmd__': ['register'], '__return__': 'register n i h p d e'}```
        - each item has each value as dictionary type.
    - ruleData.py : readable command line interface database
    - fish.csv : readable id_passwd table for each server
## 3.2. run (debug mode)
- python3 fish.py --debug

## 3.3. run (tiger command style)
- python3 fish.py --prompt="TCMD>" --tcmd

## 3.4. run (infinite mode)
- python3 fish.py --infinite

## 3.5. others
- make cpu
    - get cpu usage and disk storage status
- make modified-file
    - get modified file list in tiger-desktop
    - it use repo command
- make test-cmd
    - interactive normal mode
- make test-debug
    - interactive debug mode
- make test-tcmd
    - interactive normal mode using tiger syntax tree
- make test-infinite
    - interactive loop mode
- make test-runCommand
    - non-interactive mode (run once with your input command with return key)

# 4. asciicast2gif : convert asciinema record to gif
## 4.1. working process
1. asciinema record : ```asciinema rec```
	- upload it into asciinea.org  and download from their link (enter)
        - just asciinema.org supports for 7 days.
	- save it locally
    - asciinema: press <enter> to upload to asciinema.org, <ctrl-c> to save locally
1. asciinema play : ```asciinema play <asciicast file>```
    - you can play it.  but we need to different methods to show theis result
1. convert asciinema to gif : ```asciicast2gif <asciicast file> <target.gif>```
    - you can upload this gif without specific server to play it.
## 4.2. how to run asciicast2gif
- set alias in .bashrc
    - ```alias asciicast2gif='docker run --rm -v $PWD:/data asciinema/asciicast2gif' ```
- run
    - ```asciicast2gif <asciicast file> <target.gif>```
## 4.3. samples for FISH and Cisco Style Cli
- [fish.asciicast](https://github.com/cheoljoo/fish/blob/main/img/fish.asciicast)
    - ![](https://github.com/cheoljoo/fish/blob/main/img/fish.gif)
- cisco style cli interactive [normal.asciicast](https://github.com/cheoljoo/normal/blob/main/img/normal.asciicast)
    - ![](https://github.com/cheoljoo/fish/blob/main/img/normal.gif)
- cisco style cli interactive infinite loop [infinite.asciicast](https://github.com/cheoljoo/infinite/blob/main/img/infinite.asciicast)
    - ![](https://github.com/cheoljoo/fish/blob/main/img/infinite.gif)
- cisco style cli interactive mode for tiger project [tcmd.asciicast](https://github.com/cheoljoo/tcmd/blob/main/img/tcmd.asciicast)
    - ![](https://github.com/cheoljoo/fish/blob/main/img/tcmd.gif)
- cisco style cli run command once [runcommand.asciicast](https://github.com/cheoljoo/runcommand/blob/main/img/runcommand.asciicast)
    - ![](https://github.com/cheoljoo/fish/blob/main/img/runcommand.gif)
## 4.4. reference links
- https://github.com/asciinema/asciinema-player
- https://github.com/asciinema/asciicast2gif
- docker : https://hub.docker.com/r/asciinema/asciicast2gif

# 5. DESIGN
- ssh
    - If a command is specified, it is executed on the remote host instead of a login shell.
- rsh 
    - ```alias rsh-file='sshpass -p [your_passwd] ssh -o StrictHostKeyChecking=no [your_id]@[hostname]'```
- how to get system performance
    - CPU Benchmark : https://github.com/alexdedyura/cpu-benchmark
        - ```txt
            rsh-file "cd cpu-benchmark ; python3 cpu-benchmark.py"
            Python CPU Benchmark by Alex Dedyura (Windows, macOS(Darwin), Linux)
            CPU: Intel(R) Core(TM) i5-3470 CPU @ 3.20GHz
            Arch: x86_64
            OS: Linux
            
            Benchmarking:
            
            Time: 42.18s
            Time: 42.165s
            Time: 42.172s
            Time: 42.159s
            Time: 42.168s
            Time: 42.166s
            Time: 42.168s
            Time: 42.165s
            Time: 42.178s
            Time: 42.169s
            Average (from 10 repeats): 42.169s
          ```
    - https://ziggurat2020.tistory.com/2
    - https://pypi.org/project/cmdbench/
        - cmdbench --iterations 10 --print-averages --save-plot=plot.png node test.js
- how to get current usage
    - https://www.delftstack.com/ko/howto/python/get-cpu-usage-in-python/
        - ```python3 cpu.py```
- Python * OS 명령어 결과를 Python 코드에서 사용할래! 
    - 출처: https://proni.tistory.com/8 [Programmer Leni 🤪:티스토리]
- 가상환경 기존과 같이 한꺼번에 깔기
    - virtualenv 이용후 다음을 하여 모든 python package설치
        - sudo apt install virtualenv
        - sudo apt install python3-pip
    - pip3 freeze > requirements.txt
    - pip3 install -r requirements.txt
- 환경 설정과 실행 부분을 나누어야 한다. 
    - 환경설정
        - fish/a 로 virtualenv를 넣어서 사용한다.
        - tiger-desktop , bmw등을 수행할수 있는 script를 만들어두어야 한다. 
        - tcmd를 받아서 설치하는 것도 넣어두자.
        - tcmd 에 넣어서 remote에서도 동작하게 할까?
            - remote-install
            - remote-run-shell
            - remote-get-image 를 하면 image를 받아서 설치 할수 있게 , 필요하면 copy하게... 
            - remote-cmd
            - id , passwd는 한번 물어보고 실패할때만 다시 넣게 하여 그것을 사용하는 것으로 하면 좋을 것으로 생각된다. 
    - 실행
        - fish안에 py로 만들어 수행하도록하고
        - tiger-desktop등도 여기서 받고 compile 한다. 이후 image도 가져오면 된다. 
        - tcmd 로 설치 할수 있어야 한다.
- tiger / tiger01 / lotto645 /  ci 는 알아보는 중!
- remote
    - register [name] [id] [host] [passwd] [get directory_path from ~ ]
        - save csv file & read from this file
        - id,host,passwd,directory,enable
    - deregister : list -> choose
    - enable : list -> choose
    - disable : list -> choose
    - list
    - cmd [name] [command]
        - we should store various *.sh files to do different works in FISH.
- fish.py로 따로 갈것 : shell에서 tcmd remote일때 remote.py를 실행시켜주는 것으로 한다. 
- curl    http://tiger.lge.com/AutoTest_Cmd/tiger_common_cmd.sh  -f  --output     tiger_common_cmd.sh
    - tiger_common_cmd.sh


- implement the choose , list function
    - 각기 command에 대해서 함수를 정의한다. 이 함수는 외부에 있는 함수이다. class에 있지 않음
    - ciscoCLI class에서는 정해진 함수를 수행한다. 주로 list를 하는 것이다. 거기서 값을 return하면 그 값을 받아야 한다. 
    - table을 보고 해당 값을 처리해야한다. 

- list
    - draw the structure
- checkStructure
    - check whether their input structure is right

