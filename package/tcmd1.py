from CiscoStyleCli import CiscoStyleCli
import sys

#print(help(CiscoStyleCli))

csc = CiscoStyleCli.CiscoStyleCli(prompt="TCMD>")
#print(csc.__doc__)

TOP = {
    'src': {
        '__attribute' : {
           'desc' : "get project source code"
        },
    },
    'build': {
            'apps': {
                '__attribute' : {
                   'desc' : "build  tiger-desktop ipk image file"
                },
            },
            'target': {
                'apps': None,
            },
            'vbee': {
                '__attribute' : {
                   'desc' : "build  & get ipk image with using VBEE server"
                },
            },
    },
    'run': {
        '__attribute' : {
           'desc' : "run tiger-desktop or TRDK(target-device)"
        },
    },
    'test': {
        '__attribute' : {
           'desc' : "test tiger-desktop or TRDK(target-device). All TestCase of modules (auto_test_*.csv) will be executed"
        },
    },
}
projectList = ['tiger_desktop_release' , 'bmw_icon_nad_release' , 'toyota_24dcm_release' , 'tiger_desktop_honda_release' , 'tiger_desktop_gen12_release']
csc.setCliRuleTcmd(TOP)

if len(sys.argv) > 1:
    print("argv:",sys.argv)
    x = ' '.join(sys.argv[1:])
    csc.runCommand(x)
else :
    csc.run()

