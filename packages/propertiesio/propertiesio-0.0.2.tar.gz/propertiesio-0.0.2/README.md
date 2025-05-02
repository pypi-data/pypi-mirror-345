本程序由chenxi开发，csdn：https://blog.csdn.net/chenxi1412
遵从GPL协议，github：https://github.com/zhangjiahuichenxi/propertiesio
使用实例：
#1.新建文件
```
import propertiesio
propertiesio.new_properties("文件路径")
```
#2.创建对象
```
import propertiesio
对象 = propertiesio.new("文件路径")
```
#3.判断文件是否为properties
```
import propertiesio
propertiesio.is_properties("文件路径")
```
#4.读取
```
import propertiesio
对象 = propertiesio.new("文件路径")
propertiesio.get(对象,"yourkey")
```
#5.判断key是否存在
```
import propertiesio
对象 = propertiesio.new("文件路径")
propertiesio.has(对象,"yourkey")
```
#6.写入
```
import propertiesio
对象 = propertiesio.new("文件路径")
propertiesio.put(对象,"yourkey",“值”)
```
