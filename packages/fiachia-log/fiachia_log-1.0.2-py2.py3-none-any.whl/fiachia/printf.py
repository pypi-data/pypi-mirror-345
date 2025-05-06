import os

if os.name == 'nt':
    os.system("")  # print颜色开启，如果关闭则不能在windows cmd中显示颜色


class Color:
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    PURPLERED = "purple-red"
    CYANINE = "cyanine"
    WHITE = "white"
    DEFAULT = "default"


class Effect:
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    FLASH = "flash"
    BACKWHITE = "backwhite"
    UNSHOW = "unshow"
    DEFAULT = "default"


class Type:
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    DATA = "data"
    SYSTEM = "system"
    NORMAL = "normal"


# windows仅支持8种颜色
# 黑色、红色、绿色、黄色、蓝色、紫红、靛蓝、白色
__color__ = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "purple-red": "35",
    "cyanine": "36",
    "white": "37",
    "default": "37",
}
# 黑色、红色、绿色、黄色、蓝色、紫红、靛蓝、白色
__background__ = {
    "black": "40;",
    "red": "41;",
    "green": "42;",
    "yellow": "43;",
    "blue": "44;",
    "purple-red": "45;",
    "cyanine": "46;",
    "white": "47;",
    "default": "",
}
# 默认、高亮、下划线、闪烁、反白、不显示
__effect__ = {
    "default": "0",
    "highlight": "1",
    "underline": "4",
    "flash": "5",
    "backwhite": "7",
    "unshow": "8",
}
# 类型：简化设置
__level__ = {
    "error": ["31", "", "4"],
    "warning": ["33", "", "0"],
    "success": ["32", "", "0"],
    "data": ["34", "", "0"],
    "system": ["36", "", "0"],
    "normal": ["30", "", "0"],
    "default": ["30", "", "0"],
}


def style_to_str(style):
    """
    :param style: [color, background, effect]
    :return:
    """
    if len(style) == 3:
        return f"\033[{style[2]};{style[1]}{style[0]}m%s\033[0m"


def value_to_str(*values, sep=" ", end=None):
    if end is None:
        return sep.join(map(str, values))
    else:
        return f"{sep.join(map(str, values))}{end}"


def value_to_fill(*values, fill_width=5, fill_char=" ", fill_type="L", fill_parameter=0.6):
    if len(fill_char) != 1:
        raise OverflowError("填充字符长度只能为1")
    return [
        str_just(
            str(__value_i), fill_width, fill_char, _type=fill_type, _parameter=fill_parameter
        ) for __value_i in values
    ]


class Print:
    def __init__(self, *values, sep=' ', end='\n', file=None, flush=False,
                 level=None, color=None, background=None, effect=None, output=True):
        self.values = values
        self.sep = sep
        self.end = end
        self.file = file
        self.flush = flush
        self.__style = __level__.get(level, None) or [
            __color__.get(color, "30"), __background__.get(background, ""), __effect__.get(effect, "0")
        ]
        self.output = output

    @property
    def color(self):
        return self.style[0]

    @color.setter
    def color(self, value):
        if value in __color__:
            self.style[0] = __color__[value]
        elif value in __color__.values():
            self.style[0] = value

    @property
    def background(self):
        return self.style[1]

    @background.setter
    def background(self, value):
        if value in __background__:
            self.style[0] = __background__[value]
        elif value in __background__.values():
            self.style[0] = value

    @property
    def effect(self):
        return self.style[2]

    @effect.setter
    def effect(self, value):
        if value in __effect__:
            self.style[0] = __effect__[value]
        elif value in __effect__.values():
            self.style[0] = value

    @property
    def style(self):
        return self.__style

    @style.setter
    def style(self, value):
        if value in __level__:
            self.__style = __level__[value]

    def reset(self):
        self.style = "default"

    def __call__(
            self,
            *values,
            sep=None,
            end=None,
            file=None,
            flush=None,
            output=None,
    ):
        if output or (output is None and self.output):
            __sep = self.sep if sep is None else sep
            __end = self.end if end is None else end
            __file = self.file if file is None else file
            __flush = self.flush if flush is None else flush
            __values = self.values if len(values) == 0 else values
            print(
                style_to_str(self.style) % value_to_str(*__values, sep=__sep),
                end=__end, file=__file, flush=__flush
            )

    def printf(
            self,
            *values,
            sep=None,
            end=None,
            file=None,
            flush=None,
            output=None,
    ):
        return self(
            *values, sep=sep, end=end, file=file, flush=flush, output=output
        )

    def fill_print(
            self,
            *values, sep=None, end=None,
            fill_width=5, fill_char=" ", fill_type="L", fill_parameter=0.60,
            file=None, flush=None
    ):
        self(
            value_to_fill(
                *values, fill_width=fill_width, fill_char=fill_char, fill_type=fill_type, fill_parameter=fill_parameter
            ),
            sep=None, end=None, file=None, flush=None
        )

    def left(
            self, *values, sep=None, end=None,
            fill_width=5, fill_char=" ", fill_parameter=0.60,
            file=None, flush=None
    ):
        self.fill_print(
            *values, sep=sep, end=end,
            fill_width=fill_width, fill_char=fill_char, fill_type="L", fill_parameter=fill_parameter,
            file=file, flush=flush
        )

    def right(
            self, *values, sep=None, end=None,
            fill_width=5, fill_char=" ", fill_parameter=0.60,
            file=None, flush=None
    ):
        self.fill_print(
            *values, sep=sep, end=end,
            fill_width=fill_width, fill_char=fill_char, fill_type="R", fill_parameter=fill_parameter,
            file=file, flush=flush
        )

    def center(
            self, *values, sep=None, end=None,
            fill_width=5, fill_char=" ", fill_parameter=0.60,
            file=None, flush=None
    ):
        self.fill_print(
            *values, sep=sep, end=end,
            fill_width=fill_width, fill_char=fill_char, fill_type="C", fill_parameter=fill_parameter,
            file=file, flush=flush
        )


def printf(
        *values, sep=" ", end="\n", file=None, flush=False,
        level=None, color=None, background=None, effect=None, output=True
):
    if output:
        __style = __level__.get(level, None) or [
            __color__.get(color, "30"), __background__.get(background, ""), __effect__.get(effect, "0")
        ]
        print(
            style_to_str(__style) % value_to_str(*values, sep=sep),
            end=end, file=file, flush=flush
        )


def str_just(_string, _length, _fill_char=" ", _type="L", _parameter=0.6):
    """
    中英文混合字符串对齐函数
    str_just(_string, _length[, _type]) -> str


    :param _string:[str]需要对齐的字符串
    :param _length:[int]对齐长度
    :param _fill_char:[str]填充字符
    :param _type:[str]对齐方式（'L'：默认，左对齐；'R'：右对齐；'C'或其他：居中对齐）
    :param _parameter:[float] 长度调节参数
    :return:[str]输出_string的对齐结果
    """
    _str_len = len(_string)
    num = sum('\u2E80' <= _char <= '\uFE4F' for _char in _string)
    _str_len += num * _parameter
    _space = round(_length - _str_len)
    if _type == 'L':
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space // 2
        _right = _space - _left
    return f"{_fill_char}" * _left + _string + f"{_fill_char}" * _right


if __name__ == '__main__':
    a = Print("eee", color="red")
    a()
