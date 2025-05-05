# Dirmarks
Dirmarks is a directory bookmarking tool that allows you to easily manage, navigate, and switch between directories using bookmarks. This tool can save you time and make working with the command line more efficient.


## Installation
Install the Markdirs package using pip:

```
pip install dirmarks
```

## Shell Function Setup
To enable the dir command for changing directories using bookmarks, add the following shell function to your .profile, .bashrc, or .zshrc file, depending on your shell:

```
#!/bin/bash
dir() {
if [ "$#" -eq 0 ]; then
    dirmarks list
else
OPT=$1;
shift;
case $OPT in
        -l)
        dirmarks list
        ;;
        -h)
        dirmarks help
        ;;
        -d)
        dirmarks delete $1
        ;;
        -m)
        dirmarks add $1 $PWD
        ;;
        -u)
        dirmarks update $1 $2
        ;;
        -a)
        dirmarks add $1 $2
        ;;
        -p)
        GO=`dirmarks get $1`;
        if [ "X$GO" != "X" ]; then
                echo $GO;
        fi
        ;;
        *)
        GO=`dirmarks get $OPT`;
        if [ "X$GO" != "X" ]; then
                cd $GO;
        fi
        ;;
esac
fi

}
```

Or add a file .functions in your home directory and source it in .bashrc

```
echo "source ~/.functions" >> ~/.bashrc
```
## Setup dirmarks for all users 

```
mkdir -p /etc/bash.functions 
cp data/marks.function /etc/bsh.fucntions
```

### Append the following line in /etc/bash.bashrc

```
if [ -d /etc/bash.functions ]; then
        for i in /etc/bash.functions/*;do 
                source $i
        done
fi
```

## Usage:

```
dir -h   ------------------ prints this help
dir -l	------------------ list marks
dir <[0-9]+> -------------- dir to mark[x] where is x is the index
dir <name> ---------------- dir to mark where key=<shortname>
dir -a <name> <path> ------ add new mark
dir -d <name>|[0-9]+ ------ delete mark
dir -u <name> <path> ------ update mark
dir -m <name> ------------- add mark for PWD
dir -p <name> ------------- prints mark
```

## Usage example

```
majam@dirose:~$ dir -l
0 => meirm:/net/xen/mnt/sdb1/meirm
1 => edonkey:/net/xen/mnt/sdb1/majam/aMule/Incoming
2 => init:/etc/init.d
3 => majam:/net/xen/mnt/sdb1/majam

majam@dirose:~$ dir 1
majam@dirose:/net/xen/mnt/sdb1/majam/aMule/Incoming$ 

majam@dirose:/etc/init.d$ dir majam
majam@dirose:/net/xen/mnt/sdb1/majam$ 

majam@dirose:~$ dir -d 2
majam@dirose:~$
```

