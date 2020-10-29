# m3u82mp3
Simple module to convert m3u8 audio stream to complete audio file. It works with python3.
* ### Install
```
$ pip install -r requirements.txt
```
* ### Usage
```
$ python m3u82mp3.py -i input.m3u8 -o output.mp3
```

Program will use STDIN and STDOUT if input or output is not specified:
```
$ python m3u82mp3.py -i input.m3u8 > output1.mp3
$ python m3u82mp3.py > output2.mp3 < input.m3u8
```
