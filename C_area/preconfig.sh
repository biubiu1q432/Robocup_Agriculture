#!/bin/bash
#这是 Shebang，表示这个脚本需要使用 Bash 解释器来执行。
#当你在终端运行这个脚本时，系统会自动调用 /bin/bash 来解析和执行脚本中的命令。
export PYTHONPATH=/home/gintama/mainpart/:/home/gintama/mainpart/Modules/:/home/gintama/mainpart/Modules/VisionModule/:/home/gintama/mainpart/Modules/utils/:/home/gintama/mainpart/Modules/const/:$PYTHONPATH
#export 是 Bash 中的一个命令，用于设置环境变量。
#PYTHONPATH 是 Python 的一个环境变量，用于指定 Python 在导入模块时搜索的额外路径。
#这里将多个路径添加到 PYTHONPATH 中，路径之间用冒号:分隔。
#具体路径：
#/home/gintama/mainpart/
#主项目的根目录。
#/home/gintama/mainpart/Modules/
#主项目下的 Modules 目录，可能包含一些核心模块。
#/home/gintama/mainpart/Modules/VisionModule/
#VisionModule 目录，可能包含与视觉处理相关的模块。
#/home/gintama/mainpart/Modules/utils/
#utils 目录，可能包含一些工具函数或工具类。
#/home/gintama/mainpart/Modules/const/
#const 目录，可能包含一些常量定义。
#:$PYTHONPATH
#将原有的 PYTHONPATH 值追加到新路径的后面，确保不会覆盖原有的路径
echo "已导入文件路径..."
#echo 是 Bash 中的一个命令，用于输出文本到终端。
#这里输出 "已导入文件路径..."，表示脚本已经成功设置了 PYTHONPATH。
#注意事项
#临时生效：
#通过 export 设置的环境变量只在当前终端会话中有效。如果关闭终端或打开新的终端窗口，PYTHONPATH 会被重置。
#如果需要永久生效，可以将 export 语句添加到 ~/.bashrc 或 ~/.bash_profile 文件中。
#路径顺序：
#Python 会按照 PYTHONPATH 中路径的顺序搜索模块。如果多个路径下有同名模块，Python 会使用第一个找到的模块。
#路径分隔符：
#在 Linux/macOS 中，路径分隔符是冒号 :在 Windows 中，路径分隔符是分号 ;

