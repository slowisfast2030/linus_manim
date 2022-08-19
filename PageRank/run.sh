# 显示场景 StationaryDistPreview
echo scene: $1
# anaconda python环境
# 新建了虚拟环境manim 
# conda activate manim
python -m manim render markov_chain.py $1 -c manim.cfg