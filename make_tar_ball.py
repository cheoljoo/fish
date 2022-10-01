import re
import os

print('cd tiger-desktop; echo "===========>__<==ROOT" > repo_status.log')
os.system('cd tiger-desktop; echo "===========>__<==ROOT" > repo_status.log')
print('cd tiger-desktop; pwd >> repo_status.log')
os.system('cd tiger-desktop; pwd >> repo_status.log')
print('cd tiger-desktop; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')
os.system('cd tiger-desktop; ../repo forall -c "echo \\"===========>__<==CURRENT\\" ; pwd ; git status --untracked-file=no" >> repo_status.log')

with open("tiger-desktop/repo_status.log", "r" , newline='') as f:
    lines = f.readlines()

newFileRe = re.compile('^\s*new file:\s+(?P<ans>.*)$')
modifiedRe = re.compile('^\s*modified:\s+(?P<ans>.*)$')
rootPathRe = re.compile('^===========>__<==ROOT')
currentPathRe = re.compile('^===========>__<==CURRENT')
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
            filelist.append('.' + currentPath.strip() + '/' + filename.strip())
    elif modifiedRe.search(l):
        grp = modifiedRe.search(l)
        if grp:
            filename = str(grp.group('ans')).strip()
            filelist.append('.' + currentPath.strip() + "/" + filename.strip())
        

    if rootPathFlag:
        rootPath = l.strip()
        rootPathFlag = False
    if currentPathFlag:
        currentPath = l.strip()
        currentPath = currentPath.replace(rootPath,"")
        currentPathFlag = False
    
print("modified filelist:",filelist)

