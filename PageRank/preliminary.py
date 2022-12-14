from manim import *

class ToyExample(Scene):
    def construct(self):
        orange_square = Square(color=ORANGE, fill_opacity=0.5)
        blue_circle = Circle(color=BLUE, fill_opacity=0.5)
        self.add(orange_square)
        self.play(ReplacementTransform(orange_square, blue_circle, run_time=3))
        small_dot = Dot()
        small_dot.add_updater(lambda mob: mob.next_to(blue_circle, DOWN))
        self.play(Create(small_dot))
        self.play(blue_circle.animate.shift(RIGHT))
        self.wait()
        self.play(FadeOut(blue_circle, small_dot))

# linus下面的代码等价于
# python -m manim -qm -p preliminary.py ToyExample

# 注意：python -m module等价于 python some_path/module.py 
# 那么-qm -p preliminary.py ToyExample其实就全是module.py的参数

# 可以猜测
# 1.module.py这个脚本会利用-qm -p参数初始化config字典
# 2.module.py这个脚本内部会对preliminary.py脚本中的ToyExample类进行实例化，并调用render方法

with tempconfig({"quality": "medium_quality", "preview": True}):
    scene = ToyExample()
    scene.render()
# python preliminary.py
# 这种执行方式是将上述执行过程显示化 