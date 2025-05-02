from collections import deque

__ALL__ = ['Line']

class Line:
    def __init__(self, maxlen=3):
        self.data = deque([None] * maxlen, maxlen=maxlen)

    def append(self, value):
        """ 追加数据 """
        self.data.append(value)

    def __getitem__(self, index):
        """ 自定义索引访问规则：t[0] 访问最新的值，t[-1] 访问倒数第 3 个值 """
        if index >= 0:
            return self.data[-1 - index]  # t[0] 访问最新的
        else:
            return self.data[-1 + index]  # 负索引反向访问

    def __setitem__(self, index, value):
        """ 允许 t[0] = value 进行赋值 """
        if index == 0:
            self.data[-1] = value  # 修改最新的值
        elif index > 0:
            self.data[-1 - index] = value  # 修改历史值
        else:
            self.data[-1 + index] = value  # 负索引修改

    def __repr__(self):
        return f"Line({list(self.data)}, maxlen={self.data.maxlen})"