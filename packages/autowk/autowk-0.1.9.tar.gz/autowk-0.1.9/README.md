## AutoWK 自动化浏览器框架
> 🚀 一个基于原生 WebKit二次开发的自动化浏览器框架，支持命令行参数控制窗口位置与代理配置，并通过 Python 客户端驱动自动操作浏览器。
<p align="center">
  <img src="icon.png" alt="AutoWK Logo" width="230">
</p>

## ✨ 项目亮点

- ✅ 🧠 基于 WebKit 源码构建，小而精致的浏览器内核
- ✅ 🛠️ 自动启动 WebKit 与 WebDriver 进程
- ✅ 📜 支持命令行传参（窗口位置、尺寸、代理类型、代理认证）
- ✅ 💪 网络改造，支持 HTTP/SOCKS5 等代理模式
- ✅ 📏 Python API 调用控制浏览器行为
- ✅ 🧪 人类行为模拟，底层行为重写，自定义行为动作都是isTrusted。
---


## 快速开始
> 🚀 交流群QQ：391116392
1. 安装依赖：

   ```bash
   pip install autowk==0.1.9
   ```

2. 编写代码，启动自动化：

### 示例代码 ：过steam的定制5s盾
```python
from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    client = AutoWK()
    try:
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())
        
        client.navigate(r"https://steamdb.info/")
        print("[URL]", client.get_current_url())

        time.sleep(10)
        #坐标直接用操作系统的截图，然后画板打开看x和y坐标
        client.click_pos_by_win(266,326)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(500)
        client.delete_session()
        client.close()
```
### 示例代码 ：过12306滑块验证码
```python
from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    """自动化1236滑块验证码"""
    client = AutoWK()
    try:
        client.create_session()

        print("[STATUS]", client.status())

        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())

        client.navigate(r"https://www.12306.cn/index/view/infos/ticket_check.html")
        print("[URL]", client.get_current_url())

        #输入座次
        input_ele=client.find_element_by_css_selector("input#ticket_check_trainNum").input("1462")

        time.sleep(3)
        #选择地点
        drap=client.find_element_by_css_selector("div.model-select-text")
        drap.set_attribute("data-value","TXP")
        print('attr:', drap.get_attribute("data-value"))
        print('选择完毕')

        time.sleep(3)
        #拖拽滑块验证码
        btn=client.find_element_by_css_selector("li a.btn.btn-primary").click()
        time.sleep(5)
        #拖拽滑块验证码，这里用的是拖拽模拟人类行为，所以用的是drag_and_drop_pos_human方法
        #坐标需要自己定位一下
        client.drag_and_drop_pos_human(525,436,848,436)
        print('拖拽完毕')


    except Exception as e:
        print(e)

    finally:
        time.sleep(5)
        client.delete_session()
        client.close()
```
### 示例代码 ：切换iframe
```html
<head>
    <title>Test Iframe</title>
</head>
<body>
    <h1>Main Page</h1>
    <iframe id="myFrame" srcdoc='
        <html>
        <body>
            <input type="text" id="innerInput" value="inside iframe"/>
        </body>
        </html>'></iframe>
</body>
```
```python
from autowk.AutoWkDriverClient import AutoWK
import time

if __name__ == "__main__":
    client = AutoWK()
    try:
        client.create_session()
        print("[STATUS]", client.status())

        # 设置超时
        client.set_timeouts({"pageLoad": 10000})
        print("[GET TIMEOUTS]", client.get_timeouts())

        # 访问本地文件路径
        client.navigate(r"file:///D:\Python\pycode\2025\autowk\test.html")
        print("[URL]", client.get_current_url())
        time.sleep(2)

        # 查找 iframe 元素
        iframe = client.find_element_by_xpath('//iframe[@id="myFrame"]')
        print("[IFRAME]", iframe)

        # 切换到 iframe
        print(client.switch_to_frame(iframe))

        # 查找 iframe 内部 input
        inner_input = client.find_element_by_xpath('//input[@id="innerInput"]')
        print("[IFRAME INPUT]", inner_input)

        # 操作元素
        inner_input.input("Hello from Python WebDriver!")

    except Exception as e:
        print(e)

    finally:
        time.sleep(500)
        client.delete_session()
        client.close()

```
---

## 支持的启动命令行参数（MiniBrowser.exe）

| 参数               | 示例                            | 说明                       |
|--------------------|----------------------------------|--------------------------|
| `--x=`             | `--x=100`                        | 设置窗口左上角 X 坐标             |
| `--y=`             | `--y=200`                        | 设置窗口左上角 Y 坐标             |
| `--width=`         | `--width=1280`                   | 设置窗口宽度                   |
| `--height=`        | `--height=720`                   | 设置窗口高度                   |
| `--proxyType=`     | `--proxyType=socks5`             | 代理类型：`HTTP` / `SOCKS5` 等 |
| `--proxyHost=`     | `--proxyHost=127.0.0.1`          | 代理服务器地址                  |
| `--proxyPort=`     | `--proxyPort=1080`               | 代理端口                     |
| `--proxyUsername=` | `--proxyUsername=admin`          | 代理认证用户名                  |
| `--proxyPassword=` | `--proxyPassword=123456`         | 代理认证密码                   |
```cmd
例子:minibrowser.exe --proxyType=SOCKS5  --proxyHost=1.1.1.1  --proxyPort=1000 --proxyUsername=ruyi  --proxyPassword=wifi --x=500 --y=100  --width=500 --height=500 
```
---

## 项目结构

```
.
├── main.py                  # 示例入口，演示自动化操作
├── AutoWKBase.py            # WebKit 与 WebDriver 启动控制逻辑
├── AutoWkDriverClient.py    # 封装 WebDriver API 自动化操作类
├── Element.py               # 元素封装类，支持属性、点击、输入等操作
├── scripts/
│   └── launch_driver.bat    # 启动 WebKit WebDriver 的批处理脚本
├── bin/
│   └── MiniBrowser.exe      # 编译好的 WebKit 浏览器
```


---

## TODO

- ✅ 支持代理认证
- ⏳ 支持 Cookie 持久化管理
- ⏳ 支持 Shadow DOM 元素查找
- ⏳ 完善窗口多开与进程隔离控制

---
