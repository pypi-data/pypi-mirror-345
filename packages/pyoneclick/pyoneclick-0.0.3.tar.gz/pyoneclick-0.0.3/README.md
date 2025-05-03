
# pyoneclick

该 Python 工具能够自动过滤控制变量，类似于 Stata 的 `oneclick` 命令，但提供更强大的功能。

- English: [README_en.md](https://github.com/zpjbtdjm/pyoneclick/blob/master/README_en.md)

## 简介

### 洞见

本研究的开发基于以下见解：

1. 要做时间与最优解的权衡。在筛选控制变量的过程中，当控制变量过多时，筛选最优解在时间上是不可接受的。很多时候我们只需要快速得出一个能用的结果，即一个接近最优解的结果，而不是所有能用的结果。

2. 要解决按下葫芦浮起瓢的问题。很多时候一个变量在特定命令中显著了，另一个变量或者另一条命令中的同一个变量又不显著了，因此用于筛选的命令需要解决这类需要同时显著的问题。

### 命令特点

相对 Stata 中的 oneclick 命令，本命令加入了许多新的特性。本命令具有以下特性：

1. 筛选更加高效。本命令基于模拟退火算法而非枚举，在搜索可用控制变量过程中具有较低的时间复杂度。

2. 逻辑更加清晰。在执行命令过程中可以直接传入 Stata 的原生代码，无需改变代码习惯，命令可读性更高。

3. 功能范围更广。支持多命令联合估计，支持同时对多个变量或多条命令的显著性进行调整。

## 使用

### 需求

在正式使用之前，我们需要具备以下条件：

1. 拥有有效的许可证的 Stata 软件。软件版本必须为 Stata 17 及以上。

2. 合适的 Python 3 环境。建议为 Python 3.8 及以上版本。

### 安装

1. 首先需要在 Windows 控制面板中设置系统全局变量，变量名为 `STATA_PATH`。变量的值设定为 Stata 安装路径加上版本号。以 64 位电脑上 Stata 18 的 MP 版本为例，系统默认安装路径以下所示：
```
STATA_PATH=C:\Program Files\Stata18\StataMP-64.exe
```

2. 安装 `pyoneclick` 命令：
```shell
pip install pyoneclick
```

### 开始使用

`pyoneclick` 命令的功能较为复杂，完整掌握可能需要一定时间。
- 我们提供了详细的使用说明，以帮助用户快速上手：[查看详细使用说明](https://github.com/zpjbtdjm/pyoneclick/blob/master/docs/USAGE.md)

## 致谢

本项目的开发受到了 [StataOneClick](https://github.com/ShutterZor/StataOneClick) 项目的启发，在此我们向该项目的作者致以诚挚的感谢。作者的卓越工作为我们的项目提供了宝贵的思路，并成为了本项目开发的重要基础。
