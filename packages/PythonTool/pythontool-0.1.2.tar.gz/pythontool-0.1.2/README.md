# PythonTool

`PythonTool` 是一个用于Python中的常用工具包。

## 安装

```bash
pip install PythonTool
```

## 说明

### `ManimTool`类（部分函数用法详见[manim官网](https://www.manim.community)）

```python
def ChineseMathTex(*texts, color=WHITE, font="SimSun", font_size=DEFAULT_FONT_SIZE, tex_to_color_map={}):
    ... # 省略中间代码
    return MathTex(...) # 省略参数
```

创建中文数学公式，在此函数中直接写入中文即可，无需包裹`\text{}` 。

```python
def YellowCircle(dot1, dot2):
    ... # 省略中间代码
    return line
```

创建以`dot1`为圆心，`dot1`到`dot2`的距离为半径的黄色圆。

```python
def YellowLine(start, end):
    ... # 省略中间代码
    return line
```

创建以`start`开始，到`end`结束的黄色线。

```python
def MathTexLine(start, end, tex, color=WHITE, font_size=DEFAULT_FONT_SIZE, direction=UP, buff=0.5):
    ... # 省略中间代码
    return VGroup(mathtex, line)
```

创建以`start`开始，到`end`结束的线，但可以标注文字、公式等。

```python
def LabelDot(dot_label, dot_pos, label_pos=DOWN, buff=0.1):
    ... # 省略中间代码
    return VGroup(label, dot)
```

创建一个带有名字的点。

```python
def MathTexBrace(start, end, tex, color=WHITE, font_size=DEFAULT_FONT_SIZE, direction=UP, buff=0.5):
    ... # 省略中间代码
    return VGroup(mathtex, brace)
```

创建一个从`start`开始，`end`结束的大括号，并且可以在大括号上标注文字、公式等。

```python
def MathTexDoublearrow(start, end, tex, color=WHITE, font_size=DEFAULT_FONT_SIZE, direction=UP, buff=0.5):
    ... # 省略中间代码
    return VGroup(mathtex, doublearrow)
```

创建一个从`start`开始，`end`结束的双箭头，并且可以在双箭头上标注文字、公式等。

```python
def find_circle_intersections(circle1, circle2):
    ... # 省略中间代码
      if d > circle1_radius + circle2_radius or d < abs(circle1_radius - circle2_radius):
          return None
    ... # 省略中间代码
    return [xs1, ys1, 0], [xs2, ys2, 0]
```

寻找两个圆的交点并返回，如果没有交点会返回`None`。

```python
def find_line_circle_intersections(line, circle):
    ... # 省略中间代码
    if discriminant < 0:
            return None
    ... # 省略中间代码
    return intersections
```

寻找一条线和一个圆的交点并返回，如果没有交点会返回`None`。

```python
def find_line_intersection(line1: Line, line2: Line) -> Optional[Tuple[float, float]]:
    ... # 省略中间代码
    if div == 0:
        return None
    ... # 省略中间代码
    return [x, y, 0]
```

寻找两条线的交点并返回，如果没有交点会返回`None`。

```python
def extend_line(line: Line, extend_distance: float) -> Line:_point)
    ... # 省略中间代码
    return extended_line
```

将一条线延长`extend_distance`的距离。
