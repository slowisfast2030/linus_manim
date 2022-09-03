# linus_manim

# 发现一个先manimce源码特别好的方法：
* 下载manimce源码
* vscode在打开后，选择一个没有安装manim的python环境
* 在example_scenes里点击manim变量，可以直接在源码里跳转

路径疑问：
example_scenes和manim文件夹是同级目录，那么example_scenes下的文件为何可以直接引用manim文件夹里的变量呢？


/opt/anaconda3/envs/manim/lib/python3.9/site-packages/manim/animation/animation.py
193:print("linus starting animation")