# 2022.09.28 [220923/refactoring_CiscoStyleCommandLineInterface] TIGER-13896 TIGER-13897 :  refactoring

[VLM] TIGER-13896 , TIGER-13897
- CiscoStyleCLI class
- --infinite 를 하면 self.run() 안에서 무한 loop 로 동작
- self.checkReturnable() 에서 끝이면 returnable 을 알아서 붙여주고 , returnfunc도 self.common()으로 set
- argument일 경우 argument-type에 int , str 대신  list , dictionary도 추가하도록 함.
- checkCmd 에서 다음의 일들을 처리
  - TODO : 한줄로 들어오는 것을 처리  - 일단 입력부터 한줄로 받을수 있는 것을 알아봐야함.
    - https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=cjh226&logNo=220997049388
- 전체적 flow refactoring
  - 입력단에서 처리
    - " " quote string의 경우 입력단에서 처리
    - backspace 처리
    - space , \n , \t 일 경우 현재까지의 command를 CiscoStyleCLI.checkCmd()에 넘김
  - CiscoStyleCLI.checkCmd() 처리
    - token으로 잘라내어 , 마지막 token 전까지 tree를 쫓아간다. 
      - tree의 문법과 맞지 않으면 , 처리하는 곳까지를 return한다. command도 처리되는 것까지만 남겨둔다.
    - 마지막 token에 대해서 처리
      - 명령이 \n 이면 
        - command이면
          - command로써 syntax에 부합되면 
            - returnable일 경우 returnfunc를 수행시켜주고 return한다.
          - 부합되지 않으면 space를 눌렀을때와 같이 다음으로 처리 (goto space)
        - argument일 경우
          - argument-type이 list와 dictionary인 경우는 위의 command와 같이 처리
            - list와 directionary일때만 부합되지 않는 illegal한 경우는 space와 같이 처리 (goto space)
          - returnable일 경우 returnfunc를 수행시켜주고 return한다.
      - space : space 를 받았다고 가정하고 (\t로 space로 취급)
        - recommend를 할 모든 case들을 print해준다. argument-type이 list와 dictionary 인 것도 따로 처리해준다.
        - 입력이 완료되지 않은 경우 , longest matching을 찾아서 거기까지는 채워준다. 
        - 다음 입력이 command이면서 한개의 명령이 있는 경우 자동으로 채워준다.
        - 다음 명령을 recommend 할때 , prefunc이 있는 경우 해당 내용을 수행해준다. 
    - retValue 에 최종 parsing된 내용을 넣어서 return한다.
      - 위에서 prefunc , returnfunc를 수행할때도 기본 argument로 retValue가 주어진다. 

-----------------------
# 2022.09.28 [220923/refactoring_CiscoStyleCommandLineInterface] TIGER-14194 :  not interactive (one line command)

[VLM] TIGER-14194
- checkCmd를 call해주면됨
- parser.add_argument('X', type=str, nargs='+')

-----------------------
# 2022.09.28 [220923/refactoring_CiscoStyleCommandLineInterface] TIGER-14192 : (tcmd type command) seungdae.goh's command architecture   

[VLM] TIGER-14192
```
Cisco style  dict  입력  변경 건의 드립니다.
1 >  '__attribute' 를 keyword 으로 사용 
TOP ['register'] = {
    '__attribute' : {
        'type' : "command"
        'returnable' : ""
        'desc' : "registration~~"
        'returnable' : ""
        },
    'name' : { 
        '__attribute' : {
            'type' : "command"
            'returnable' : ""
            'desc' : "name~~"
            'returnable' : ""
        },
        'target' : {
            ...
        }
    },
}


2  >  attribue 기본 (default) 값은 생략 가능 하며,   return 함수 지정 
TOP['build'] = {
    'tyt_24dcm' : { 
        '__attribute' : {
            'desc' : "registration~~"
            'retrurnfunc' :   rc.show  or  rc.default_exec    # // call  python function  :  default_exec ( arg all )    -->  "shell command"
        'target' : {
        }
```
- --prompt option
- --tcmd option : seungdae.goh 's request for tcmd
- retValue 형식 변경
  - ```v {'__cmd__': ['gethost', 'choose2'], 'number': {'choice': 'tiger', 'data': ['cheetah', 'tiger', 'fish', 'turtle', 'tigiris']}, '__return__': 'gethost choose2 tiger'}```
  - ```v {'__cmd__': ['gethost', 'choose1'], 'choose': '0', '__return__': 'gethost choose1 0'}```
  - ```v {'__cmd__': ['gethost', 'choose3'], 'shoot': {'choice': '1', 'data': {'0': 'car', '1': 'tiger', '2': 'telematics'}}, '__return__': 'gethost choose3 1'}```

-----------------------
# 2022.10.01 [220930/pypi] TIGER-14204 : pypi - upload python module on pypi

[VLM] TIGER-14204
- TIGER-14204 : python으로 cisco style command line 만들기 - CiscoStyleCLI 의 python module package 수행 (설명서와 help / guide)도 만들어야 할 듯.. 배포 할 것
## make package
```
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
## upload package (distribution)
```
cd package
python3 -m pip install --upgrade twine
python3 -m twine upload --skip-existing dist/*
pypi's id and passwd
```

-----------------------
# 2022.10.05 [221005/tcmd] apply it to tcmd (AutoTest_Cmd)

- apply CiscoStyleCli to AutoTest_Cmd
    - http://mod.lge.com/hub/seungdae.goh/AutoTest_Cmd.git
- exmaple: tcmd3.py
- bug fix -1 (line:820)
    - test tt [enter]
    - test tt tt [enter]
- add function  (line:979)
    - auto completion when next item is only one command
- bug fix -2
    - show the recommendation when i meet argument

