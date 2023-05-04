# PyQt5-Chrome

## Install
```shell
pip install -r requirements.txt
```

## Run
```shell
python main.py
```

## Package
```shell
pyinstaller --upx-dir ./ -D main.py -i ./icons/logo.ico ^
-p ./font ^
--add-data ./font;./font ^
--add-data ./main.css;./
```
