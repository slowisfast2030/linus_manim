import sys
sys.path.append("../common/")

from manim import *
from manim.mobject.geometry.tips import ArrowTriangleFilledTip
from reducible_colors import *
from functions import *

from typing import Hashable

import numpy as np
import itertools as it

#linus 随机种子影响马尔科夫图
np.random.seed(23)


class MarkovChain:
    def __init__(
        self,
        states: int,
        edges: list[tuple[int, int]],
        transition_matrix=None,
        dist=None,
    ):
        """
        @param: states -- number of states in Markov Chain
        @param: edges -- list of tuples (u, v) for a directed edge u to v, u in range(0, states), v in range(0, states)
        @param: transition_matrix -- custom np.ndarray matrix of transition probabilities for all states in Markov chain
        @param: dist -- initial distribution across states, assumed to be uniform if none
        """
        #linus 通过range来表达状态数，真是艺高人胆大
        self.states = range(states)
        #linus 嵌套列表，只不过内层是tuple
        self.edges = edges
        #linus 马尔科夫链可以认为是图，图的一种表示方法就是邻接表
        #linus 由edges就可以生成adj_list
        self.adj_list = {}
        for state in self.states:
            self.adj_list[state] = []
            #linus 边里的数据，第一个是起点，第二个终点
            for u, v in edges:
                if u == state:
                    self.adj_list[state].append(v)
        
        #linus 转移矩阵
        if transition_matrix is not None:
            self.transition_matrix = transition_matrix
        else:
            # Assume default transition matrix is uniform across all outgoing edges
            #linus 为同一个节点的所有出边设置均匀分布
            #linus 转移矩阵是一个二维数据。在我的固有观念中，还是习惯于嵌套列表，却没有深刻吸收numpy在并行处理上的巨大优势。
            self.transition_matrix = np.zeros((states, states))
            for state in self.states:
                neighbors = self.adj_list[state]
                for neighbor in neighbors:
                    self.transition_matrix[state][neighbor] = 1 / len(neighbors)

        # handle sink nodes to point to itself
        #linus 设置指向自己的转移概率
        for i, row in enumerate(self.transition_matrix):
            if np.sum(row) == 0:
                self.transition_matrix[i][i] = 1

        #linus 设置节点的初始概率
        if dist is not None:
            self.dist = dist
        else:
            self.dist = np.array(
                [1 / len(self.states) for _ in range(len(self.states))]
            )

        #linus 节点的初始分布
        #linus self.starting_dist和self.dist两个变量是不是有点重复？
        self.starting_dist = self.dist

    #linus 这种写法就是我目前无法驾驭的
    def get_states(self):
        return list(self.states)

    def get_edges(self):
        return self.edges

    def get_adjacency_list(self):
        return self.adj_list

    def get_transition_matrix(self):
        return self.transition_matrix

    def get_current_dist(self):
        return self.dist

    #linus 原来这里的self.dist变量跟踪的是不同时间点的状态分布。属于一个动态概念。
    def update_dist(self):
        """
        Performs one step of the markov chain
        """
        self.dist = np.dot(self.dist, self.transition_matrix)

    #linus 难道这是求得稳态的计算方法吗？
    '''
    np.transpose: 计算转移矩阵的转置
    np.linalg.eig: 计算特征值和特征向量
    取第一个特征向量

    稳态的计算确实只与转移矩阵有关，和初始分布无关
    '''
    '''
    详细的数学解释：https://blog.csdn.net/weixin_42428226/article/details/117713725
    结论：通过特征向量求解稳态不是特别靠谱的方法。
    '''
    def get_true_stationary_dist(self):
        dist = np.linalg.eig(np.transpose(self.transition_matrix))[1][:, 0]
        return dist / sum(dist)

    def set_starting_dist(self, starting_dist):
        self.starting_dist = starting_dist
        self.dist = starting_dist

    def get_starting_dist(self):
        return self.starting_dist

    def set_transition_matrix(self, transition_matrix):
        self.transition_matrix = transition_matrix

# 这个类很是典型。
# 以前总是好奇，为何
class CustomLabel(Text):
    def __init__(self, label, font="SF Mono", scale=1, weight=BOLD):
        #linus 如果没有下面这一行，子类会覆盖父类的__init__函数
        #linus 现在调用父类的__init__函数，会把父类初始化时的变量引入
        #linus 子类构造函数调用super()._init_()的时候，会从父类继承属性
        """
        当子类不做初始化的时候，会自动继承父类的属性；
        当子类做初始化（子类中包含新的属性）的时候，子类不会自动继承父类的属性；
        当子类做初始化（子类中包含新的属性）的时候，如果子类调用super初始化了父类的构造函数，那么子类会继承父类的属性。
        class father:
        def __init__(self, father_attribute = "father"):
            self.father_attribute = father_attribute

        class child_without_ini(father):
            pass

        class child_with_ini(father):
            def __init__(self, child_attribute):
                self.child_attribute = child_attribute

        class child_with_super(father):
            def __init__(self,father_attribute, child_attribute):
                self.child_attribute = child_attribute
                super().__init__(father_attribute)

        test_class_without_ini = child_without_ini()
        test_class_with_ini = child_with_ini('child')
        test_class_with_super = child_with_super('child_father', 'child')


        #linus 自动继承父类所有的属性
        print("test_class_without_ini:")
        print(test_class_without_ini.father_attribute, "\n")

        #linus 不仅仅有父类属性，还有子类的属性
        print("test_class_with_super:")
        print(test_class_with_super.father_attribute)
        print(test_class_with_super.child_attribute, "\n")

        #linus 父类的初始化函数被覆盖
        print("test_class_with_ini:")
        print(test_class_with_ini.child_attribute)
        print(test_class_with_ini.father_attribute)
        """
        #linus 如果抽象得看，类只是拥有类内的函数的使用权。
        #linus 一旦发生继承，子类就会拥有父类函数的使用权。
        super().__init__(label, font=font, weight=weight)
        #linus 发生了继承，那么子类就有了父类函数的使用权。scale()是父类函数。
        #linus 调用父类函数是为了修改某一属性。
        self.scale(scale)


class CustomCurvedArrow(CurvedArrow):
    def __init__(self, start, end, tip_length=0.15, **kwargs):
        #linus 这里也能看出来，子类的属性会比父类更多
        super().__init__(start, end, **kwargs)
        self.pop_tips()
        self.add_tip(
            tip_shape=ArrowTriangleFilledTip,
            tip_length=tip_length,
            at_start=False,
        )
        self.tip.z_index = -100

    def set_opacity(self, opacity, family=True):
        #linus 通过父类的函数赋值，没想到。深度思考，常问本质！
        return super().set_opacity(opacity, family)

    #linus 高端操作
    @override_animate(set_opacity)
    def _set_opacity_animation(self, opacity=1, anim_args=None):
        if anim_args is None:
            anim_args = {}

        animate_stroke = self.animate.set_stroke(opacity=opacity)
        animate_tip = self.tip.animate.set_opacity(opacity)

        return AnimationGroup(*[animate_stroke, animate_tip])


class MarkovChainGraph(Graph):
    def __init__(
        self,
        # 类型注释只是一种提示，并非强制的。python解释器不会去校验value的类型是否真的是type
        markov_chain: MarkovChain,
        vertex_config={
            "stroke_color": REDUCIBLE_PURPLE,
            "stroke_width": 3,
            "fill_color": REDUCIBLE_PURPLE,
            "fill_opacity": 0.5,
        },
        # 参数类型是dict，默认值是None
        curved_edge_config: dict = None,
        straight_edge_config: dict = None,
        enable_curved_double_arrows=True,
        labels=True,
        state_color_map=None,
        #linus 以前学习的参数都是固定参数，这一次是可变参数。确实挺耳目一新的。
        # def add(*numbers):
        #     total = 0
        #     for num in numbers:
        #         total += num
        #     return total


        # print(add(2, 3))
        # print(add(2, 3, 5))
        # print(add(2, 3, 5, 7))
        # print(add(2, 3, 5, 7, 9))

        # def total_fruits(**fruits):
        #     total = 0
        #     for amount in fruits.values():
        #         total += amount
        #     return total


        # print(total_fruits(banana=5, mango=7, apple=8))
        # print(total_fruits(banana=5, mango=7, apple=8, oranges=10))
        # print(total_fruits(banana=5, mango=7))

        **kwargs,
    ):
        self.markov_chain = markov_chain
        #linus 弯曲的双向箭头
        self.enable_curved_double_arrows = enable_curved_double_arrows
        #linus 曲边
        self.default_curved_edge_config = {
            "color": REDUCIBLE_VIOLET,
            "stroke_width": 3,
            "radius": 4,
        }
        #linus 直边
        self.default_straight_edge_config = {
            "color": REDUCIBLE_VIOLET,
            "max_tip_length_to_length_ratio": 0.06,
            "stroke_width": 3,
        }
        self.state_color_map = state_color_map

        if labels:
            labels = {
                k: CustomLabel(str(k), scale=0.6) for k in markov_chain.get_states()
            }
        
        if self.state_color_map:
            new_vertex_config = {}
            for state in markov_chain.get_states():
                new_vertex_config[state] = vertex_config.copy()
                new_vertex_config[state]["stroke_color"] = self.state_color_map[state]
                new_vertex_config[state]["fill_color"] = self.state_color_map[state]

            vertex_config = new_vertex_config

        self.labels = {}

        super().__init__(
            markov_chain.get_states(),
            markov_chain.get_edges(),
            vertex_config=vertex_config,
            labels=labels,
            **kwargs,
        )

        self._graph = self._graph.to_directed()
        self.remove_edges(*self.edges)

        self.add_markov_chain_edges(
            *markov_chain.get_edges(),
            straight_edge_config=straight_edge_config,
            curved_edge_config=curved_edge_config,
        )

        self.clear_updaters()
        # this updater makes sure the edges remain connected
        # even when states move around
        def update_edges(graph):
            for (u, v), edge in graph.edges.items():
                v_c = self.vertices[v].get_center()
                u_c = self.vertices[u].get_center()
                vec = v_c - u_c
                unit_vec = vec / np.linalg.norm(vec)

                u_radius = self.vertices[u].width / 2
                v_radius = self.vertices[v].width / 2

                arrow_start = u_c + unit_vec * u_radius
                arrow_end = v_c - unit_vec * v_radius
                edge.put_start_and_end_on(arrow_start, arrow_end)

        self.add_updater(update_edges)
        update_edges(self)

    def add_edge_buff(
        self,
        edge: tuple[Hashable, Hashable],
        edge_type: type[Mobject] = None,
        edge_config: dict = None,
    ):
        """
        Custom function to add edges to our Markov Chain,
        making sure the arrowheads land properly on the states.
        """
        if edge_config is None:
            edge_config = self.default_edge_config.copy()
        added_mobjects = []
        for v in edge:
            if v not in self.vertices:
                added_mobjects.append(self._add_vertex(v))
        u, v = edge

        self._graph.add_edge(u, v)

        base_edge_config = self.default_edge_config.copy()
        base_edge_config.update(edge_config)
        edge_config = base_edge_config
        self._edge_config[(u, v)] = edge_config

        v_c = self.vertices[v].get_center()
        u_c = self.vertices[u].get_center()
        vec = v_c - u_c
        unit_vec = vec / np.linalg.norm(vec)

        if self.enable_curved_double_arrows:
            arrow_start = u_c + unit_vec * self.vertices[u].radius
            arrow_end = v_c - unit_vec * self.vertices[v].radius
        else:
            arrow_start = u_c
            arrow_end = v_c
            edge_config["buff"] = self.vertices[u].radius

        edge_mobject = edge_type(
            start=arrow_start, end=arrow_end, z_index=-100, **edge_config
        )
        self.edges[(u, v)] = edge_mobject

        self.add(edge_mobject)
        added_mobjects.append(edge_mobject)
        return self.get_group_class()(*added_mobjects)

    def add_markov_chain_edges(
        self,
        *edges: tuple[Hashable, Hashable],
        curved_edge_config: dict = None,
        straight_edge_config: dict = None,
        **kwargs,
    ):
        """
        Custom function for our specific case of Markov Chains.
        This function aims to make double arrows curved when two nodes
        point to each other, leaving the other ones straight.
        Parameters
        ----------
        - edges: a list of tuples connecting states of the Markov Chain
        - curved_edge_config: a dictionary specifying the configuration
        for CurvedArrows, if any
        - straight_edge_config: a dictionary specifying the configuration
        for Arrows
        """

        if curved_edge_config is not None:
            curved_config_copy = self.default_curved_edge_config.copy()
            curved_config_copy.update(curved_edge_config)
            curved_edge_config = curved_config_copy
        else:
            curved_edge_config = self.default_curved_edge_config.copy()

        if straight_edge_config is not None:
            straight_config_copy = self.default_straight_edge_config.copy()
            straight_config_copy.update(straight_edge_config)
            straight_edge_config = straight_config_copy
        else:
            straight_edge_config = self.default_straight_edge_config.copy()

        print(straight_edge_config)

        edge_vertices = set(it.chain(*edges))
        new_vertices = [v for v in edge_vertices if v not in self.vertices]
        added_vertices = self.add_vertices(*new_vertices, **kwargs)

        edge_types_dict = {}
        for e in edges:
            if self.enable_curved_double_arrows and (e[1], e[0]) in edges:
                edge_types_dict.update({e: (CustomCurvedArrow, curved_edge_config)})

            else:
                edge_types_dict.update({e: (Arrow, straight_edge_config)})

        added_mobjects = sum(
            (
                self.add_edge_buff(
                    edge,
                    edge_type=e_type_and_config[0],
                    edge_config=e_type_and_config[1],
                ).submobjects
                for edge, e_type_and_config in edge_types_dict.items()
            ),
            added_vertices,
        )

        return self.get_group_class()(*added_mobjects)

    def get_transition_labels(self, scale=0.3, round_val=True):
        """
        This function returns a VGroup with the probability that each
        each state has to transition to another state, based on the
        Chain's transition matrix.
        It essentially takes each edge's probability and creates a label to put
        on top of it, for easier indication and explanation.
        This function returns the labels already set up in a VGroup, ready to just
        be created.
        """
        tm = self.markov_chain.get_transition_matrix()

        labels = VGroup()
        for s in range(len(tm)):

            for e in range(len(tm[0])):
                if s != e and tm[s, e] != 0:

                    edge_tuple = (s, e)
                    matrix_prob = tm[s, e]

                    if round_val and round(matrix_prob, 2) != matrix_prob:
                        matrix_prob = round(matrix_prob, 2)

                    label = (
                        Text(str(matrix_prob), font=REDUCIBLE_MONO)
                        .set_stroke(RED, width=8, background=True, opacity=0.8)
                        .scale(scale*1)
                        .move_to(self.edges[edge_tuple].point_from_proportion(0.2))
                    )

                    labels.add(label)
                    self.labels[edge_tuple] = label

        def update_labels(graph):
            for e, l in graph.labels.items():
                l.move_to(graph.edges[e].point_from_proportion(0.2))

        self.add_updater(update_labels)

        return labels


class MarkovChainSimulator:
    def __init__(
        self,
        markov_chain: MarkovChain,
        markov_chain_g: MarkovChainGraph,
        num_users=50,
        user_radius=0.035,
    ):
        self.markov_chain = markov_chain
        self.markov_chain_g = markov_chain_g
        self.num_users = num_users
        self.state_counts = {i: 0 for i in markov_chain.get_states()}
        self.user_radius = user_radius
        self.distribution_sequence = []
        self.init_users()

    def init_users(self):
        self.user_to_state = {
            i: np.random.choice(
                self.markov_chain.get_states(), p=self.markov_chain.get_current_dist()
            )
            for i in range(self.num_users)
        }
        for user_id in self.user_to_state:
            self.state_counts[self.user_to_state[user_id]] += 1

        #linus 每一个点模拟一个user
        self.users = [
            Dot(radius=self.user_radius)
            .set_color(REDUCIBLE_YELLOW)
            .set_opacity(0.6)
            .set_stroke(REDUCIBLE_YELLOW, width=2, opacity=0.8)
            for _ in range(self.num_users)
        ]

        for user_id, user in enumerate(self.users):
            user_location = self.get_user_location(user_id)
            user.move_to(user_location)

        self.distribution_sequence.append(self.markov_chain.get_current_dist())

    def get_user_location(self, user: int):
        user_state = self.user_to_state[user]
        user_location = self.markov_chain_g.vertices[user_state].get_center()
        distributed_point = self.poisson_distribution(user_location)

        user_location = [distributed_point[0], distributed_point[1], 0.0]

        return user_location

    def get_users(self):
        return self.users

    def transition(self):
        for user_id in self.user_to_state:
            self.user_to_state[user_id] = self.update_state(user_id)
        self.markov_chain.update_dist()
        self.distribution_sequence.append(self.markov_chain.get_current_dist())

    def update_state(self, user_id: int):
        current_state = self.user_to_state[user_id]
        transition_matrix = self.markov_chain.get_transition_matrix()
        new_state = np.random.choice(
            self.markov_chain.get_states(), p=transition_matrix[current_state]
        )
        self.state_counts[new_state] += 1
        return new_state

    def get_state_counts(self):
        return self.state_counts

    def get_user_dist(self, round_val=False):
        dist = {}
        total_counts = sum(self.state_counts.values())
        for user_id, count in self.state_counts.items():
            dist[user_id] = self.state_counts[user_id] / total_counts
            if round_val:
                dist[user_id] = round(dist[user_id], 2)
        return dist

    def get_instant_transition_animations(self):
        transition_animations = []
        self.transition()
        for user_id, user in enumerate(self.users):
            new_location = self.get_user_location(user_id)
            transition_animations.append(user.animate.move_to(new_location))
        return transition_animations

    def get_lagged_smooth_transition_animations(self):
        transition_map = {i: [] for i in self.markov_chain.get_states()}
        self.transition()
        for user_id, user in enumerate(self.users):
            new_location = self.get_user_location(user_id)
            transition_map[self.user_to_state[user_id]].append(
                user.animate.move_to(new_location)
            )
        return transition_map

    def poisson_distribution(self, center):
        """
        This function creates a poisson distribution that places
        users around the center of the given state,
        particularly across the state's stroke.
        Implementation taken from: https://github.com/hpaulkeeler/posts/blob/master/PoissonCircle/PoissonCircle.py
        """

        radius = self.markov_chain_g.vertices[0].width / 2

        xxRand = np.random.normal(0, 1, size=(1, 2))

        # generate two sets of normal variables
        normRand = np.linalg.norm(xxRand, 2, 1)

        # Euclidean norms
        xxRandBall = xxRand / normRand[:, None]

        # rescale by Euclidean norms
        xxRandBall = radius * xxRandBall

        # rescale for non-unit sphere
        # retrieve x and y coordinates
        xx = xxRandBall[:, 0]
        yy = xxRandBall[:, 1]

        # Shift centre of circle to (xx0,yy0)
        xx = xx + center[0]
        yy = yy + center[1]

        return (xx[0], yy[0])

    def get_state_to_user(self):
        state_to_users = {}
        for user_id, state in self.user_to_state.items():
            if state not in state_to_users:
                state_to_users[state] = [user_id]
            else:
                state_to_users[state].append(user_id)
        return state_to_users

    def get_distribution_sequence(self):
        return self.distribution_sequence


class MarkovChainTester(Scene):
    def construct(self):
        markov_chain = MarkovChain(
            4,
            [(0, 1), (1, 0), (0, 2), (1, 2), (1, 3), (2, 3), (3, 1)],
        )
        #linus [0, 1, 2, 3]
        print(markov_chain.get_states())

        #linus [(0, 1), (1, 0), (0, 2), (1, 2), (1, 3), (2, 3), (3, 1)]
        print(markov_chain.get_edges())

        #linus [0.25 0.25 0.25 0.25]
        print(markov_chain.get_current_dist())

        #linus {0: [1, 2], 1: [0, 2, 3], 2: [3], 3: [1]}
        print(markov_chain.get_adjacency_list())
        
        '''
        [[0.         0.5        0.5        0.        ]
        [0.33333333 0.         0.33333333 0.33333333]
        [0.         0.         0.         1.        ]
        [0.         1.         0.         0.        ]]
        '''
        print(markov_chain.get_transition_matrix())

        markov_chain_g = MarkovChainGraph(
            markov_chain, enable_curved_double_arrows=True
        )
        markov_chain_t_labels = markov_chain_g.get_transition_labels()

        # 马尔科夫链状态转换
        self.play(FadeIn(markov_chain_g))
        # linus 概率
        self.play(FadeIn(markov_chain_t_labels))
        self.wait()