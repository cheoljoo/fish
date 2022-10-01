import CiscoStyleCli

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(prompt="TCMD>")
#print(csc.__doc__)

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

csc.run()

