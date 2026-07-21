# 后端开发

作为多后端的GUI库，支持使用多种后端来构建应用程序，为了统一接口，我们提供了一个模板来帮助开发者快速上手。以下是模板的基本结构和使用方法。


## 模板结构
模板主要包含以下几个部分：
1. `Backend`类：用于定义后端的基本接口和功能。
2. 各种`*SupportState`类：用于表明是否支持对应后端功能。
3. 各种`*Base`类：用于定义对应后端的基本接口和功能。

至于细节可以参见{doc}`/api/backend/template`去查阅有哪些类。

## 编写后端接口
这里先用`Genesis`后端作为演示，学习如何编写一个后端接口。

### 编写GUI后端接口
先要注明后端的基本信息，包括简写名称、具体名称、版本号和作者等。然后继承`template.Backend`类，并实现必要的接口。

#### 编写`Backend`类

```python
class Backend(template.Backend):
    """The Genesis backend."""

    name: typing.ClassVar[str] =            "genesis"
    friendly_name: typing.ClassVar[str] =   "Genesis (early development)"
    version: typing.ClassVar[str] =         "0.1.0"
    author: typing.ClassVar[list[str]] =    ["rgzz666", "XiangQinXi", "CodeCrafter"]

    WindowBase: type[WindowBase]
    LineBase: type[LineBase]
    ShapeBase: type[ShapeBase]
    TextureBase: type[TextureBase]

    def __init__(self):
        """APIs are aliased here."""
        super().__init__()
    
    def backend_init(self, **kwargs) -> None:
        return
```

- name: 后端的简写名称，通常用于命令行参数中指定后端。
- friendly_name: 后端的具体名称，通常用于显示在界面上。
- version: 后端的版本号，通常用于显示在界面上。
- author: 后端的作者列表，通常用于显示在界面上。

#### 编写`WindowSupportState`类

先注明自己支持哪些后端方法，从而防止开发时出现纰漏。如以下代码，在支持的方法名称前面标注了`True`，不支持的方法标注了`False`。如果你不确定是否支持某个方法，可以先标注为`False`，等后续实现后再改为`True`。
```python
class WindowSupportState(template.WindowSupportState):
    """Flags all supported window features."""
    set_title               : bool = True
    set_icon                : bool = True
    set_pos                 : bool = True
    set_size                : bool = True
    set_scale_mode          : bool = True
    set_background          : bool = True
    translucent             : bool = True
    backdrop                : type[WindowBackdropSupportState] = WindowBackdropSupportState
    set_state               : bool = True
    fullscreen              : bool = True
    customize_titlebar      : bool = False
```

#### 编写`WindowBase`类
这是后端使用的GUI窗口类接口，继承自`template.WindowBase`，并实现必要的接口。

```python
class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend

    def __init__(self, backend: template.Backend, charmy_window: _window.WindowEntity):
        """Creates a window.

        :param backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend, charmy_window)

        self.title: str = "Charmy SDL2 Window"
        self.size: tuple[int, int] = (540, 480)

        # Create window
        self.window: typing.Any = ...

        # Sync window pos to higher level stuff
        self.charmy_window._pos = ...


    def show(self) -> typing.Self:
        ...

    def update(self, redraw: bool | charmy_stuff.styles.shape.ShapeRange = True) -> typing.Self:
        ...

    def close(self):
        ...

```

首先第一步继承模板类，并设定Backend类属性为你刚刚编写的`Backend`类型，设定`supports`为你刚刚编写的`WindowSupportState`实例。
```python
class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend
```

那么你就已经完成了`GUI接口`的编写，下一步就是编写`图形接口`用于绘制窗口内部的图形。

### 编写图形后端接口
等待编写...