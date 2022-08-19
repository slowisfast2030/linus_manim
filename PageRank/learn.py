from manim import *

# python -m manim learn.py ShowScreenResolution 如果配置文件是manim.cfg就不需要写-c参数，程序会自动在文件的当前目录下寻找manim.cfg文件
# python -m manim learn.py ShowScreenResolution -c *.cfg 如果配置文件不是取名manim.cfg，就需要指明配置文件名

class ShowScreenResolution(Scene):
    def construct(self):
        #linus 下面的注释严格来讲是不准确的。只有qh是参数1080*1920所示。
        pixel_height = config["pixel_height"]  #  1080 is default
        pixel_width = config["pixel_width"]  # 1920 is default
        #linus 显示在屏幕上的宽度和高度
        frame_width = config["frame_width"]
        frame_height = config["frame_height"]
        print("pixel_height:", pixel_height)
        print("pixel_width:", pixel_width)
        print("frame_width:", frame_width)
        print("frame_height:", frame_height)
        
        self.add(Dot())
        d1 = Line(frame_width * LEFT / 2, frame_width * RIGHT / 2).to_edge(DOWN)
        # print(frame_width * LEFT / 2, frame_width * RIGHT / 2)
        self.add(d1)
        self.add(Text(str(pixel_width)).next_to(d1, UP))
        d2 = Line(frame_height * UP / 2, frame_height * DOWN / 2).to_edge(LEFT)
        # print(frame_height * UP / 2, frame_height * DOWN / 2)
        self.add(d2)
        self.add(Text(str(pixel_height)).next_to(d2, RIGHT))

        print(config['quality'])