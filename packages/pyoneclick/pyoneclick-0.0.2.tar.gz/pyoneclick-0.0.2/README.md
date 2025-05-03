## 相对 Stata 版本 oneclick 的特点
1、基于启发式算法而非枚举，低的时间复杂度。
2、灵活的命令估计，无需改变代码习惯，命令可读性更高。
3、支持多命令联合估计。

## 初衷
1、解决按下葫芦浮起瓢的问题。
2、很多时候我们只是需要一个能用的结果，而不是所有能用的结果。


## 需求
在正式使用之前，我们需要具备以下条件：
1. 拥有有效的许可证的 Stata 软件。软件版本必须为 Stata 17 及以上。
2. 合适的 Python 3 环境。

## 安装

1. 首先需要在 Windows 控制面板中设置系统全局变量，变量名为 `STATA_PATH`。值为 Stata 安装路径加上版本号。
以 64 位电脑上 Stata 18 的 MP 版本为例，系统默认安装路径以下所示：
```
STATA_PATH=C:\Program Files\Stata18\StataMP-64.exe
```
2. 安装 `pyoneclick` 命令：
```shell
pip install pyoneclick
```

## 基本使用方法

[查看详细使用说明](https://github.com/zpjbtdjm/pyoneclick/blob/master/USAGE.md)
