# Dependencies

Python 3.9 works. Not sure about lower versions.

bilibili_api should be the only required package. Install with pip.

# Example usage
```
python3 main.py BV1yF411Y7xs BV1Cq4y1u7Pt
```
Explanation: analyze danmaku from two videos with BV number BV1yF411Y7xs and BV1Cq4y1u7Pt
```
python3 main.py -f sources.txt -m 5
```
Explanation: analyze danmaku from BV numbers stored in a file named sources.txt. The file must be in the same directory 
as the script. Otherwise, provide a relative or absolute directory. Peak multiplier is set to 5, lower than the default. 
This means the program will generate more intervals than default. 
