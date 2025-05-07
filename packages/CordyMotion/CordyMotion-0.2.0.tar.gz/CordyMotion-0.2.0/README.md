.
# CordyMotion
CordyMotion 是基于珠海市科迪电子科技有限公司平台的设备驱动运控程序客户端cordymotioncaller的一层封装。主要是用于IRU以及SimpleIQ等测试设备调用的API。
目前CordyMotion只支持Linux(Ubuntu22.04)版本。

---
## 主要特点
* CordyMotion 安装时会自动添加依赖，其配置文件cordy.ini 会默认安装在Ubuntu当前用户目录下的Bin/Config下（例如：~/Bin/Config/cordy.ini)

---

## pip 安装
CordyMotion 已经发布到 Pypi 官网，通过 pip 指令可以安装。
注意：需要提前在 Ubuntu22.04 操作系统上安装python(版本3.10)
```
pip install CordyMotion
```

验证CordyMotion 是否安装成功
```
>>> from CordyMotion import IRU
>>> help(IRU)

```
输出如下内容:
```
|  IRU命名空间，包含方法fixture_load(), fixture_unload(), power_on_dut(), power_off_dut(), fixture_iru_pos()
 |  
 |  示例:
 |      >>> from CordyMotion import IRU
 |      >>> IRU.fixture_load()
 |  
 ...
```
表示安装成功

## 帮助说明

* 使用者可以通过 help() 来查询 CordyMoion 的帮助说明。目前支持对整个whl包、某个类或者类中的某个函数接口的使用说明。

### 查看整个IRU类的帮助
```
from CordyMotion import IRU, SimpleIQ

help(IRU) 
help(SimpleIQ)
```

### 查看特定方法的帮助
```
from CordyMotion import IRU, SimpleIQ
help(IRU.fixture_load)
help(SimpleIQ.fixture_unload)
```
### 查看包级帮助
```
import CordyMotion
help(CordyMotion)
```




