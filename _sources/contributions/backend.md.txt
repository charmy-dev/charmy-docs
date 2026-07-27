# 后端开发指南

作为多后端的GUI库，Charmy支持使用多种后端来构建应用程序，为了统一接口并确保每个未被支持的功能都有对应的fallback，我们提供了一个可供继承的模板，通常您的后端应当基于此模板开发。以下是模板的基本结构和使用方法。


## 后端的基本结构
一个有效的Charmy后端主要应当包含以下几个部分：
1. `Backend`类：用于定义后端的基本接口和功能，以及后端的元信息（也就是您的署名处）。
2. 各种`*SupportState`类：用于标记当前后端是否支持某些特性。
3. 各种`*Base`类：用于定义对应后端的基本接口和功能。

至于细节可以参见{doc}`/api/backend/template`去查阅有哪些类，或者参见{doc}`/how_does_it_work/abstraction_layer`了解详细的介绍。

## 编写后端接口
我们将会基于Genesis后端的代码为基础，在本文中讲述如何为Charmy开发一个有效可用的后端。

> 如果你是扩展后端库开发者，建议使用`charmy-backend-xxx`作为库名。未来将支持自动搜索所有名称以`charmy-backend-`开头的包，并将其加入备选后端。

### 编写GUI后端接口
先要注明后端的基本信息，包括简写名称、具体名称、版本号和作者等。然后继承`template.Backend`类，并实现必要的接口。

#### 编写`Backend`类

```python
class Backend(template.Backend):
    """The Genesis backend."""

    name: typing.ClassVar[str] =            "genesis"
    friendly_name: typing.ClassVar[str] =   "Genesis"
    version: typing.ClassVar[str] =         "0.1.0"
    author: typing.ClassVar[list[str]] =    ...

    def __init__(self):
        """APIs are aliased here."""
        super().__init__()
    
    def backend_init(self, **kwargs) -> None:
        return
```

- name: 后端的名称，最好为字母+下划线这样的安全格式，用于标识，需确保唯一。
- friendly_name: 后端的用户友好名称，用于人类阅读，暂无实际用途。
- version: 后端的版本号，可能用于检查更新等，暂无实际用途。
- author: 后端的作者列表，暂无实际用途。

#### 编写`WindowSupportState`类

后端应当注明自己支持哪些后端方法，从而防止开发时出现纰漏。如以下代码，在支持的方法名称前面标注了`True`，不支持的方法标注了`False`。如果你不确定是否支持某个方法，可以先标注为`False`，等后续实现后再改为`True`。

如果Charmy的后续更新加入了新的后端特性，而您却没有跟进的话，也并不需要额外添加更新来标记新特性为不支持，因为它们会在模板中默认标记为`False`，然后被继承到您的后端里。

综上所述，具体的实现应当为：后端继承template中对应的`*SupportState`类，然后标记自身支持的特性为`True`，并（可选）标记自身明确不会支持的特性为`False`。

以下是一个例子，这个后端声明其支持为窗口设定标题与图标，但明确声明其不支持设定窗口在屏幕上的位置。而对于缩放模式等，后端并未明确进行声明，Charmy会将其视为不支持这些特性。

```python
class WindowSupportState(template.WindowSupportState):
    """Flags all supported window features."""
    set_title               : bool = True
    set_icon                : bool = True
    set_pos                 : bool = False
    set_size                : bool = True
    # set_scale_mode          : bool = False
```

#### 编写`WindowBase`类
这是后端使用的GUI窗口类接口，应当继承自`template.WindowBase`，并实现必要的功能。

```python
class WindowBase(template.WindowBase):
    """Window APIs implementation."""
    supports = WindowSupportState()
    Backend = Backend

    def __init__(self, backend: template.Backend, charmy_window: _window.WindowEntity):
        """Creates a window.

        :param backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend, charmy_window)

        self.window: typing.Any = ...

        self.charmy_window._pos = ...


    def show(self) -> typing.Self:
        ...

    def update(self, redraw: bool | charmy_stuff.styles.shape.ShapeRange = True) -> typing.Self:
        ...

    def close(self):
        ...

```

首先继承模板类，并设定Backend类属性为你刚刚编写的`Backend`类型，设定`supports`类属性为你刚刚编写的`WindowSupportState`实例。

```python
class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend
```

之后，编写一个`__init__`函数。这个初始化函数应当接收两个参数，分别为`backend`用于接收所使用的后端，和`window`用于接收Charmy控件层的窗口对象。您的初始化函数应当实现包括但不限于以下内容：为`super()`进行初始化、调用相关第三方包创建一个窗口、向Charmy控件层汇报窗口位置（透过设定`window`参数中传入的窗口的`_pos`属性）。

之后你需要实现`__init__`、`show`、`update`和`close`方法，具体实现方式可以参考其他后端的实现。本文将会持续补充这些内容。

如此，您便完成了窗口相关接口的开发。

### 编写图形后端接口
等待编写...

### 使用该接口
如果你是`charmy`的开发者，你只需重写`charmy/backend/loader.py`内容中`load_backend`函数，添加你刚刚编写的后端接口。

```python
def load_backend(name: str) -> type[Backend]:
    if name == "auto":
        # for auto backend
        name = "genesis"
    if name == "genesis":
        from . import genesis
        return genesis.Backend
    else:
        raise NotImplementedError(
            f"Other backends (including {name}) not supported yet in early dev."
            )
```

在其中添加你刚刚编写的后端接口的导入语句，并在`if name == "genesis":`中返回你刚刚编写的`Backend`类。

之后在 **导入charmy模块前** 使用`environ.set()`函数设定`CHARMY_BACKEND`值来设定应用程序使用的后端接口。例如：
```python
from os import environ
environ["CHARMY_BACKEND"] = "genesis"
```

对于这个可以参见{doc}`/getstarted/custom_app_settings`

---

如果你是`charmy`扩展库的开发者，你需要注明让使用者在 **创建窗口前** 实例化`CharmyManager`类，并传入你刚刚编写的后端接口类作为参数。

```python
from charmy_extension import YOUR_BACKEND_CLASS  # Your backend class should be imported from your extension package
from charmy.cmm import CharmyManager

Manage = CharmyManager(YOUR_BACKEND_CLASS)
```
