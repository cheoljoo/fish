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

#import email, smtplib, ssl
#from email import encoders
#from email.mime.base import MIMEBase
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

import CiscoStyleCli

jira_rest_url = "http://vlm.lge.com/issue/rest/api/latest/"
issue_url = jira_rest_url + "issue/"
search_url = jira_rest_url + "search/"
tracker_url = jira_rest_url + "project/"
fieldList_url = jira_rest_url + "field/"
jsonHeaders = {'Content-Type': 'application/json'}

# - 특정 조건 : 그 사람 (최근 일주일)
#- 모든 ticket중에서 "그 사람"이 comments를 남긴 내용중에 tiger_weekly_report 이 comments의 첫줄에 적은 ticket들에 적은 comments를 출력한다.
#- status 상관없고, 

wordRe = re.compile('^\s*(?P<ans>[^ \n]+)')
cpusRe = re.compile('^\s*cpu count:\s*(?P<ans>[0-9\-\+\.]+)')
cpuUsageRe = re.compile('^\s*CPU usage:\s*(?P<ans>[0-9\-\+\.]+)')
dfRe = re.compile('^\s*/dev/\S+\s+\S+\s+\S+\s+(?P<ans>[0-9\-\+\.]+[MGT]+)')
newFileRe = re.compile('^\s*new file:\s+(?P<ans>.*)$')
modifiedRe = re.compile('^\s*modified:\s+(?P<ans>.*)$')
rootPathRe = re.compile('^===========>__<==ROOT')
currentPathRe = re.compile('^===========>__<==CURRENT')


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
    parser.add_argument("--infinite", action="store_true",default=False,help='CiscoStyleCLI has infinite loop')
    parser.add_argument("--tcmd", action="store_true",default=False,help="use tcmd's command architecture to make a tree")
    parser.add_argument(
        '--prompt',
        metavar="<str>",
        type=str,
        default="FISH~~:",
        help='your prompt  default :  FISH~~:')
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
    
    parser.add_argument('X', type=str, nargs='*')

    args = parser.parse_args()

    X_list = args.X
    print("argv:",X_list)

    csc = CiscoStyleCli.CiscoStyleCli(rule = args.rulefile , infinite = args.infinite , prompt = args.prompt, debug = args.debug)
    rc = RemoteCommand(csvfile=args.csvfile,debug = args.debug)
    

    # args.tcmd = True
    if args.tcmd:
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
    else:
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
        tmp = csc.addArgument(tmp,'second','float',"", "need to input with second integer",prefunc=lambda x: print("prefunc:",x))
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
        tmp = csc.addCmd(gethostCmd,'choose2','command',"", "choose type2",additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
        tmp = csc.addArgument(tmp,'number',['cheetah','tiger','fish','turtle','tigiris'],"returnable", "type from the list",returnfunc=csc.common)
        tmp = csc.addCmd(gethostCmd,'choose3','command',"", "choose type3",additionalDict={'0':'tiger','1':'bmw'},returnfunc=csc.common)
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

