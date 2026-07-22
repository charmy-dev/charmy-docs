# 组件开发
组件是指在应用程序中可重用的独立功能模块。它们通常封装了特定的功能和界面元素，使得开发者可以在不同的地方使用相同的组件，而无需重复编写代码。组件化开发有助于提高代码的可维护性、可扩展性和复用性。

## 自定义组件
在此将学习如何开发你的自定义组件，我们先从简单的`Button`组件开始。

首先继承`Widget`类，并实现`__init__`方法来初始化组件的属性。

```python
class Button(Widget):
    def __init__(self, 
                 parent=None,
                 text: str = "Button",
                 on_click: typing.Callable = lambda: None,
                 style=None,
                 *args, **kwargs):
        super().__init__(parent, style)
        self.text: str = text
        self.on_click: typing.Callable = on_click
        self.theme: typing.Optional[Theme] = None
        self.state: str = "normal"

        self._components: tuple[DrawnShape, DrawnText] = (
            DrawnShape(
                self.root_container, 
                Rect((0, 0), (0, 0)), 
                None
                ), 
            DrawnText(
                self.root_container, 
                self.text, TextStyle.sys_default, 
                None
                ), 
            )

        self.bind(
            _event_types.MouseClick, 
            lambda _: self.on_click(), {"button": 0}, _is_internal=True
            )
        self.bind(
            _event_types.MouseEnter, 
            lambda _: self.config(state="hover"), _is_internal=True
            )
        self.bind(
            _event_types.MouseLeave, 
            lambda _: self.config(state="normal"), _is_internal=True
            )
```

先写入一些基础的参数数据，按钮自然需要带上`text`和`on_click`参数，`text`是按钮上显示的文字，`on_click`是按钮被点击时触发的回调函数。
```python
class Button(Widget):
    def __init__(self, 
                 parent=None,
                 text: str = "Button",
                 on_click: typing.Callable = lambda: None,
                 style=None,
                 *args, **kwargs):
        super().__init__(parent, style)
        self.text: str = text
        self.on_click: typing.Callable = on_click
```

然后记录下按钮的主题与状态，主题用于设置按钮的样式，状态用于记录按钮当前的交互状态（如正常、悬停、按下等）。
```python
        self.theme: typing.Optional[Theme] = None
        self.state: str = "normal"
```

### 组件内部元素设定

为了开发者快速开发组件，而不接触底层绘制方法，于是采用`components`参数来存储组件的绘制对象，`DrawnShape`用于绘制按钮的形状，`DrawnText`用于绘制按钮上的文字，其余请参考 {doc}`/api/graphics`。

将你需要绘制的元素按序存入`_components`中，之后将可以直接使用该组件，能看到绘制出的那些元素。

```python
        self._components: tuple[DrawnShape, DrawnText] = (
            DrawnShape(
                self.root_container, 
                Rect((0, 0), (0, 0)), 
                None
                ), 
            DrawnText(
                self.root_container, 
                self.text, TextStyle.sys_default, 
                None
                ), 
            )
```

基本元素中，第一个参数为绘制的容器，也就是窗口实例，一般填写`self.root_container`，将指向该组件所在的窗口实例。剩下具体的参数请参考 {doc}`/api/graphics`。

```python
class DrawnObject(CharmyObject):
    """Base class of drawn objects in Charmy."""

    def __init__(self, window: WindowEntity):
        ...
```

例如`DrawnShape`元素，用于绘制预设的形状，第二个参数为形状类型实例（请参考{doc}`/api/styles/shape`），第三个参数为样式。

例子中`Rect`是矩形形状，传入两个参数，分别为左上角坐标和右下角坐标，均为元组类型。初始化的适合可以默认输入这个，后续重写更新方法时再根据布局设定位置、大小。

```python
DrawnShape(
    self.root_container, 
    Rect((0, 0), (0, 0)), 
    None
    ), 
```

### 组件事件绑定
接下来需要使用`bind`来绑定事件，从而触发`点击`事件，或触发`碰到鼠标`更新`state`以刷新样式，更多请参阅{doc}`api/event`。

```python
        self.bind(
            MouseClick, 
            lambda _: self.on_click(), {"button": 0}, _is_internal=True
            )
        self.bind(
            MouseEnter, 
            lambda _: self.config(state="hover"), _is_internal=True
            )
        self.bind(
            MouseLeave, 
            lambda _: self.config(state="normal"), _is_internal=True
            )
```

第一个参数为事件类型，请参阅{doc}`api/utils/event_types`。

第二个参数为事件回调函数，当触发该事件类型时就调用该方法，需填入参数以接收回调参数。这里`self.config(state="hover")`用于更新组件状态

`multithread`是用来选择是否将事件放入额外线程中，而不是主线程。

```python
    def bind(
        self,
        event_type: type[event_types.Event], 
        target: typing.Callable | typing.Iterable[typing.Callable], 
        conditions: typing.Optional[dict] = None, 
        multithread: bool = False, 
        _is_internal: bool = False, 
        task_obj_receiver: typing.Optional[var.Var[EventTask]] = None, 
        return_task: bool = True
    ) -> EventTask | typing.Self:
```


### 组件更新部分
组件的更新部分是组件开发中最重要的一环，组件的更新方法会在组件状态发生变化时被调用，用于重新设定元素的参数以重绘组件。

```python
    def _update_components(self) -> typing.Tuple[DrawnObject, ...]:
        """Components (drawn objects) that make up the button."""
        # Make background shape
        self._components[0].shape = \
            AnyShape.from_json(
                self.profiles[self._negotiate_profile_state(self.state, "shape")].shape
                )
        self._components[0].texture = \
            Texture.from_json(curr_style["background"])
        self._components[0].border_width = \
            curr_style["border_width"]
        self._components[0].border_texture = \
            Texture.from_json(curr_style["border_texture"])
        self._components[0].offset = \
            self.abs_pos
        # Drawn text
        self._components[1].text = \
            self.text
        self._components[1].style = \
            TextStyle.from_json(curr_style["text_style"])
        self._components[1].texture = \
            Texture.from_json(curr_style["text_texture"])
        self._components[1].offset = \
            (self.abs_pos[0] + ((self.width - self._components[1].boundary[1][0]) // 2), 
             self.abs_pos[1] + ((self.height - self._components[1].boundary[1][1]) // 2))
        return self._components
```

在该方法里直接设定对应元素的属性，为当前状态对应的样式。

...开发中，未完待续