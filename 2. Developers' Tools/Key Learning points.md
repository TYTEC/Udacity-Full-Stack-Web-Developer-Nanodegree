# Key Learning points for Developer's Tools



## Table of contents

1. Shell Workshop

## 1.  Shell Workshop
- __echo__ command is used to print messages in the shell.
- __!__ mark is a special character in the shell.
- If you put __' '__ around special signs then shell will interpret them as a regular string.
- To list content of a directory in the shell command __ls__ can be used.
- When you start the shell it will look into your home directory. To list content of another directory you can write __ls name_of_directory__.
- To check current directory use command __cd__.
- To go to another directory write __cd new_directory__.
- To go back to parent directory use command __..__
- __;__ lets us write two commands on the same line. They will be executed separately
- __$__ sign in front of the word indicates that it is a shell variable.
- __pwd__ stands for print working directory.
- Unix uses __/__ to separate folders in the directory.
- __ls -l__ - prints longer, more details description of files.
- Shell lets you match file names with the patterns. If you want to find all pdf documents in your directory you can use following code: __ls -l Documents/*.pdf__
- __ls abc*__   # list all files starting with abc---
- __ls *abc*__  # list all files containing --abc--
- __ls *abc__   # list all files ending with --abc
- __mkdir__ is used for creating new directory.
- In order to move file to another folder you can use command __mv__. You need to specify which file are you moving to which directory __mv 'file_to_move' drectory_name__
- It is also possible to match many documents at the same time and move them together to the new directory e.g __mv Documents/*pdf Documents/Books
-