
# Grid Control
> "国家电网调控AI创新大赛：电网运行组织智能安排"比赛相关资料，包括文档、代码和数据等。



## 文件说明

```
    - data: 和比赛相关的数据
    - docs: 关于环境、策略的说明文档
    - src: 源代码
```

## 环境安装

首先安装虚拟环境，并安装和线上环境相同的依赖        
```bash
    conda create -n grid_control python=3.6.9
    conda activate grid_control
    pip install -r requirements.txt
```

然后可以执行一个dummy agent来验证环境安装成功
```bash
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:src/lib64   # 添加动态库依赖
    cd src
    python main.py
```



## 参考资料

[比赛说明页面](http://sgcc.smartgrid-challenge.com.cn/#/channels/4)

[AI Studio线上平台](https://aistudio.baidu.com/aistudio/competition/detail/111)

[数据保密协议](https://pan.baidu.com/s/1MM3Pmhk-tbJkOFvYz3S0gA?_at_=1629269632128) 提取码: epri

[相关数据](https://pan.baidu.com/s/15Q_w2AbwMBnLPX6AaywOKg) 提取码: cyn6

## Reference

Gómez-Expósito, A., Conejo, A. J., & Cañizares, C. (Eds.). (2018). Electric energy systems: analysis and operation. CRC press.


