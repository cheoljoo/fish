### 2.3.2. make package
- ```
    cd package
    python3 -m pip install --upgrade setuptools wheel
    python3 setup.py sdist bdist_wheel
    ```
- verify the result
    - ```txt
        package/dist  $  ls -l
        total 40
        -rw-rw-r-- 1 cheoljoo.lee cheoljoo.lee 15326 Sep 30 23:04 ciscostylecli-1.0.0.0-py3-none-any.whl
        -rw-rw-r-- 1 cheoljoo.lee cheoljoo.lee 15483 Sep 30 23:04 ciscostylecli-1.0.0.0.tar.gz
        ```
### 2.3.3. upload package (distribution)
- ```
    cd package
    python3 -m pip install --upgrade twine
    python3 -m twine upload --skip-existing dist/*
    pypi's id and passwd
    ```

