**propgrid** is a lightweight wxPython class to show/config data
1. Install
```bash
$pip install propgrid
```
2. Usage
```python
    ...
    g = pg.PropGrid(self)
    # Separator
    g.Insert(PropSeparator().Label('general'))
    # Text
    g.Insert(PropText().Label('string').Value('hello world!').Indent(1))
```
See the **demo.py** for more details.

<img src="https://github.com/tianzhuqiao/propgrid/raw/master/doc/images/demo.png"  width="600"></img>
