
---

# 日志配置模块

## 模块功能
本模块提供了一个灵活的日志配置功能，支持以下特性：
- **日志颜色显示**：不同日志等级以不同颜色显示，便于区分。
- **日志文件自动切分**：当日志文件大小超过指定阈值时，自动切分日志文件，并按时间戳命名切分后的文件。
- **可选的日志文件生成**：根据参数决定是否生成日志文件，方便调试和生产环境使用。
- **绝对路径记录**：日志中记录代码的绝对路径，便于快速定位问题。

## 使用方法

### 安装依赖
本模块仅使用 Python 标准库，无需额外安装第三方库。

### 导入模块
```python
from np_log import setup_logging
```

### 配置日志
```python
# 默认生成日志文件   日志名默认为 logs/时间/文件名.log
logger = setup_logging()
# 默认生成日志文件   日志名默认为 logs/时间/test.log
logger = setup_logging("test")

# 不生成日志文件
logger = setup_logging(is_logfile=False)
```

### 使用日志
```python
logger.debug('这是一个 debug 日志')
logger.info('这是一个 info 日志')
logger.warning('这是一个 warning 日志')
logger.error('这是一个 error 日志')
logger.critical('这是一个 critical 日志')
```

## 日志格式
日志格式如下：
```
[时间] [日志等级] [文件路径:行号] 日志内容
```
- **时间**：日志记录的时间，格式为 `YYYY-MM-DD HH:MM:SS`。
- **日志等级**：日志的等级，如 `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。
- **文件路径**：记录日志的代码文件的绝对路径。
- **行号**：记录日志的代码所在的行号。
- **日志内容**：用户自定义的日志内容。

## 日志颜色
不同日志等级对应的颜色如下：
- `DEBUG`：青色（Cyan）
- `INFO`：绿色（Green）
- `WARNING`：黄色（Yellow）
- `ERROR`：红色（Red）
- `CRITICAL`：品红色（Magenta）

## 日志文件切分
- **切分条件**：日志文件大小超过 500MB。
- **切分后的文件命名**：原文件名加上时间戳，格式为 `原文件名_YYYYMMDD_HHMMSS`。

## 示例代码
```python
if __name__ == '__main__':
    # 测试生成日志文件
    logger1 = setup_logging()
    logger1.debug('debug')
    logger1.info('info')
    logger1.warning('warning')
    logger1.error('error')
    logger1.critical('critical')

    # 测试不生成日志文件
    logger2 = setup_logging(is_logfile=False)
    logger2.debug('debug')
    logger2.info('info')
    logger2.warning('warning')
    logger2.error('error')
    logger2.critical('critical')
```

## 注意事项
- 本模块在 Windows 系统上可能需要额外配置以支持终端颜色显示。
- 日志文件会保存在 `logs/YYYYMMDD` 目录下，其中 `YYYYMMDD` 是日志文件创建的日期。

---

将以上内容保存为 `README.md` 文件即可。