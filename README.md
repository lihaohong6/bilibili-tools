# Bilibili Tools

This is a personal project aimed at analyzing [bilibili](https://www.bilibili.com) content. 

Bilibili-Tools provides several Python scripts to
* Find time intervals of greatest danmaku activity in a video – likely where something interesting occurred. 
* Fetch all dynamic of a user. 

## Dependencies

`Python 3.9` works. Not sure about lower versions.

`bilibili_api` should be the only required package. Install with pip.

## Example usage
```
python3 main.py BV1yF411Y7xs some_file.xml
```
Explanation: analyze danmaku from two videos: BV1yF411Y7xs and another unnamed video whose danmaku is stored in `some_file.xml `. 
```
python3 main.py -f sources.txt -m 5
```
Explanation: analyze danmaku from BV numbers stored in a file named sources.txt. The file must be in the same directory as the script. Otherwise, provide a relative or absolute directory. Peak multiplier is set to 5, lower than the default. This means the program will generate more intervals than default. 

Use `python3 main.py -h` to get a list of full parameters. 
