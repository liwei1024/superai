<!-- TOC -->

1. [1. 声明](#1-声明)
2. [2. 安装说明](#2-安装说明)
3. [3. 目前效果](#3-目前效果)
4. [4. 所涉及到的知识](#4-所涉及到的知识)

<!-- /TOC -->


# 1. 声明

本程序并非外挂(不注入,不修改游戏内存,不调用call). 用途是对游戏人工智能技术做研究(计算机视觉,传统游戏人工智能,现代强化学习等), 在游戏中想要达到的目标是

1. 路径规划,智能安排技能策略组合等打败副本怪物,和人类竞速
2. pk竞技场打败人类

仅仅只是做技术探讨,研究.如果有人利用此程序恶意大量获取游戏内资源,破坏游戏系统公平,与本人无关. 

欢迎加入qq群: 597496810. 做游戏人工智能/强化学习/windows内核技术探讨 (仅限正经程序员同行,非法工作室勿扰)

(单凭python脚本无法运行本程序,需要dll和驱动程序,对于个人用户有限提供)

欢迎提PR!

# 2. 安装说明

```bash
git clone git@github.com:yqsy/superai.git
cd superai
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 经过身份认证进群下载 驱动和dll. 将 xxiii 放到superai同级目录

- project
  - superai
  - xxiii
   - x64
    - Release
     - core-sys.sys
     - helpdll-xxiii.dll
     - load.cmd
     - unload.cmd

cd superai

# 运行
python supergui.py
```

# 3. 目前效果

* https://www.bilibili.com/video/av70441860
* https://www.bilibili.com/video/av70124981

# 4. 所涉及到的知识

* <软件调试>
* <x86_x64体系探索及编程>
* <游戏人工智能>
* 计算机视觉 (目标检测 + 模板识别)
* 强化学习
* c++ & python
