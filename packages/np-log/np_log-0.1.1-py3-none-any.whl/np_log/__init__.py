import datetime
import logging
import logging.handlers
import os
import sys

# 创建多级目录
def mkdir_dir(path):
    # 判断路径是否存在
    isExists = os.path.exists(path)

    if not isExists:
        # 如果不存在，则创建目录（多层）
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False

# 自定义过滤器，用于替换 filename 为绝对路径
class AbsolutePathFilter(logging.Filter):
    def filter(self, record):
        record.abspath = os.path.abspath(record.pathname)
        return True

# 自定义日志格式化器，用于添加颜色
class ColorFormatter(logging.Formatter):
    # 定义不同日志等级的颜色
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"  # Reset color

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        message = logging.Formatter.format(self, record)
        return f"{log_color}{message}{self.RESET}"

# 自定义日志文件名格式化器
class TimedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def doRollover(self):
        """
        重写 doRollover 方法，实现按照时间戳命名切分后的日志文件
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # 获取当前时间戳
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 构造新的日志文件名
        new_log_filename = f"{self.baseFilename}_{now}"
        # 重命名当前日志文件
        os.rename(self.baseFilename, new_log_filename)
        # 重新打开日志文件
        self.mode = 'a'
        self.stream = self._open()

# 创建日志
def setup_logging(name=None, is_logfile=True):
    # 如果没有传入 name，则获取调用者的文件名
    if name is None:
        frame = sys._getframe(1)  # 获取上一级调用的帧信息
        caller_filename = os.path.basename(frame.f_code.co_filename)
        name = os.path.splitext(caller_filename)[0]  # 去掉文件扩展名
    # 使用固定的日志器名称
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 清理现有处理器
    if logger.hasHandlers():
        logger.handlers.clear()

    # 创建流处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = ColorFormatter(
        "%(asctime)s [%(levelname)s] [ \"%(filename)s:%(lineno)d\" ] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 添加自定义过滤器
    logger.addFilter(AbsolutePathFilter())

    # 根据 is_logfile 参数决定是否创建文件处理器
    if is_logfile:
        now = datetime.datetime.now().strftime("%Y%m%d")
        log_dir = f'logs/{now}'
        mkdir_dir(log_dir)
        log_file = os.path.join(log_dir, f'{name}.log')
        # 创建 RotatingFileHandler，设置最大文件大小为 500MB
        fh = TimedRotatingFileHandler(log_file, maxBytes=500*1024*1024, backupCount=10)
        fh.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # 禁止日志传播
    logger.propagate = False

    return logger
