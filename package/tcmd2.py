from CiscoStyleCli import CiscoStyleCli
import sys

def runReturnFunc(v):
    functionNameAsString = sys._getframe().f_code.co_name
    print("This is common type of prefunc and returnfunc function argument.")
    print("functionname:",functionNameAsString)
    if v:
        print("function argument: v :",v)
    print('run your code with arbument v')

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(prompt="TCMD:>")
#print(csc.__doc__)

TOP = {}
projectList = ['tiger_desktop_release' , 'bmw_icon_nad_release' , 'toyota_24dcm_release' , 'tiger_desktop_honda_release' , 'tiger_desktop_gen12_release']
projectDict = {
    'tiger_desktop_release' : 'tiger release on x86',
    'bmw_icon_nad_release' : 'BMW iconnic sf24' , 
    'toyota_24dcm_release' : 'TOYOTA 24cy dcm', 
    'tiger_desktop_honda_release' : 'HONDA 23MY' , 
    'tiger_desktop_gen12_release' : 'GM gen12'
}
TOP ['src'] = {
    '__attribute' : {
        'desc' : "get source code",
    },
    'project' : {
        '__attribute' : {
            'type' : "argument",
            'desc' : "project name",
            'argument-type': projectList,
            'returnable' : "returnable",
            'returnfunc' : runReturnFunc,
        },
        'target' : {
            '__attribute' : {
                'type' : "argument",
                'desc' : "target",
                'argument-type': 'str',
                'returnable' : "returnable",
                'additionalList' : projectList,
                'additionalDict' : projectDict,
            },
        }
    },
}
TOP ['run'] = {
    '__attribute' : {
        'desc' : "run",
    },
    'desktop' : {
        '__attribute' : {
            'desc' : "desktop",
        },
        'committest' : {
            '__attribute' : {
                'desc' : "committest",
                'type' : 'command',
                'returnable' : "returnable",
            }
        }
    }
}
TOP ['test'] = {
    '__attribute' : {
        'desc' : "build & test",
    },
    'daily' : {
        '__attribute' : {
            'desc' : "daily",
        },
        'project' : {
            '__attribute' : {
                'desc' : "project name",
                'type' : 'argument',
                'argument-type': projectList,
                'returnable' : "returnable",
            }
        }
    },
    'vt' : {
        '__attribute' : {
            'desc' : "vbee test",
        },
        'project' : {
            '__attribute' : {
                'desc' : "project name",
                'type' : 'argument',
                'argument-type': projectDict,
                'returnable' : "returnable",
                'returnfunc' : runReturnFunc,
            }
        }
    }
}
csc.setCliRuleTcmd(TOP)

if len(sys.argv) > 1:
    print("argv:",sys.argv)
    x = ' '.join(sys.argv[1:])
    csc.runCommand(x)
else :
    csc.run()

