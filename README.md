# fish
FISH (Funny sImple distributed system with rSH through sSH)

# Class
- CiscoStyleCli Class
    - quit[return] is possbile.  before changing , we can input [return] after spacebar.
    - add running function without parameter. 
        - we can put the function-name at last parameter of addArgument() and addCmd().
        - and we should bind between function-name and real function pointer with setFunc("listTable",rc.listTable)
    - output file
        - ruleData.py : rule information
- RemoteCommand Class
    - add database for user and server
    - input/output file
        - fish.csv : user and server database

# how to run
- make
    - output
```txt
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
- add running function without parameter
    - ```
            enableCmd = self.addCmd(self.remoteCmd,'enable','command',"", "change to enable status : you can use this system")
            tmp = self.addArgument(enableCmd,'choose','int',"returnable", "choose number from the list","get")

            csc = CiscoStyleCli(rule = args.rulefile , debug = args.debug)
            csc.setFunc("get",get)
      ```
    - ruleData.py : readable command line interface database
    - fish.csv : readable id_passwd table for each server

# TODO
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
