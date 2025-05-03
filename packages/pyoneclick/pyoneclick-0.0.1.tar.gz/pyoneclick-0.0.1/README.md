# 相对 stata 版本 oneclick 的特点
1、基于启发式算法而非枚举，低的时间复杂度。
2、灵活的命令估计，无需改变代码习惯，命令可读性更高。
3、支持多命令联合估计。

# 初衷
1、解决按下葫芦浮起瓢的问题。
2、很多时候我们只是需要一个能用的结果，而不是所有能用的结果。


# 需要设置系统变量
```
STATA_PATH=C:\Program Files\Stata18\StataMP-64.exe
```

# 安装
```shell
pip install pyoneclick
```

[查看使用说明](examples/USAGE.md)

