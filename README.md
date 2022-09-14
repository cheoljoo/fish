# fish
FISH (Funny sImple distributed system with rSH through sSH)

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
- 이렇게 하면 혹시 v
