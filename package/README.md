
# Introduction
- This Class runs function from command string
- Cisco Style give the recommandation when you can use easily.
- if you do not know what you do , press space or tab.
- then CiscoStyleCli shows the recommendation with help description.
    
# Requirement
- [Python][python] >= 3.6

# Installation
- Install the latest version of ciscostylecli using pip:
```bash
pip3 install ciscostylecli
```

- Install by cloning repository:
```bash
git clone https://github.com/cheoljoo/fish.git
cd CiscoStyleCli
python3 setup.py install
```

# Usage
```python
import CiscoStyleCli
```

```python
CiscoStyleCli(rulePrintFile=None, infinite=False, prompt='FISH~~:', debug=False, isUseDefaultCommon=True)
```

- This Class runs function from command string
- Cisco Style give the recommandation when you can use easily.
- if you do not know what you do , press space or tab.
- then CiscoStyleCli shows the recommendation with help description.

- Aargs
    - :param rulePrintFile: file name to print the tree
    - :param infinite: False (default) or True 
        - True if you want infinite loop. 
        - False if want to finish when you stroke 'return' key.
    - :param prompt: your prompt
    - :param debug: False (default) or True
        - True if you want to print more information
    - :param isUseDefaultCommon: True (default) or False
        - False if you want not to show message when self._common runs

- Sample Codes
    - [Basic Usage interactive test code](https://github.com/cheoljoo/fish/blob/main/package/test.py)
    - [Basic Usage debug test code](https://github.com/cheoljoo/fish/blob/main/package/debug.py)
    - [Basic Usage infinite loop interactive test code](https://github.com/cheoljoo/fish/blob/main/package/infinite.py)
    - [Basic Usage test code with tiger tree syntax](https://github.com/cheoljoo/fish/blob/main/package/tcmd.py)
    - [Basic Usage non-interactive (process command line with return) test code](https://github.com/cheoljoo/fish/blob/main/package/runCommand.py)

## interactive cisco command line interface
```python
from CiscoStyleCli import CiscoStyleCli
csc = CiscoStyleCli.CiscoStyleCli()
csc.run()
```
    - show the prompt to get your command (interactive mode)
    - press enter key , this function will return
    - https://github.com/cheoljoo/fish/package
        - ```make```

## endless interactive cisco command line interface
```python
from CiscoStyleCli import CiscoStyleCli
csc = CiscoStyleCli.CiscoStyleCli(infinite=True)
csc.run() 
```
    - it has infinite loop
    - show the prompt to get your command (interactive mode)
    - you can quit when you meet quit command or quit()
    - https://github.com/cheoljoo/fish/package
        - ```make infinite```

## non-interactive run command
```python
from CiscoStyleCli import CiscoStyleCli
csc = CiscoStyleCli.CiscoStyleCli()
csc.runCommand(cmd)
```
    - run your command (non-interactive mode)
    - https://github.com/cheoljoo/fish/package
        - ```make runCommand```

# Document
- ```
    python3
    >> import CiscoStyleCli
    >> help(CiscoStyleCli)
  ```
- ```python3 -m pydoc CiscoStyleCli > CiscoStyleCli.txt```


# Methods
```
addArgument(self, root, name, type, returnable, desc, prefunc=None, returnfunc=None, additionalDict=None, additionalList=None)
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

addCmd(self, root, command, type, returnable, desc, prefunc=None, returnfunc=None, additionalDict=None, additionalList=None)
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

checkCmd(self, cmd)
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

run(self)
    main part of cisco command line interface
    meet the prompt for your input
    get string from your input
    run() will have infinite loop before meeting quit() if you set infinite argument in __init__() as True.
    :return: retValue with all your input information
            example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}

runCommand(self, cmd)
    non-interactive run command
    
    :param cmd: retValue with all your input information
            example) {'__cmd__': ['gethost', 'choose2'], 'target': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}

setCliRule(self, rule)
    set rule 
    rule is generated from addCmd() and addArgument() functions.
    finally it set the self._comon(v) when returnable is on or this is last token (word).
      and it will add 'list' and 'quit' command automatically if you do not set it.
    
    :code example:
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

setCliRuleTcmd(self, top)
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
    
    :param top: rule dictionary tree with different type
```

# pypi
- Use pypi : https://pypi.org/project/ciscostylecli/

- [work record - lang:korean](https://github.com/cheoljoo/fish/blob/main/msg.md)

