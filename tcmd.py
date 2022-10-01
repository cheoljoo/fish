import CiscoStyleCli
import sys

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(prompt="TCMD>")
#print(csc.__doc__)

TOP = {}
projectList = ['tiger_desktop_release' , 'bmw_icon_nad_release' , 'toyota_24dcm_release' , 'tiger_desktop_honda_release' , 'tiger_desktop_gen12_release']
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
        },
        'target' : {
            '__attribute' : {
                'type' : "argument",
                'desc' : "target",
                'argument-type': 'str',
                'returnable' : "returnable",
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
                'argument-type': projectList,
                'returnable' : "returnable",
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

