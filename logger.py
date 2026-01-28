import logging
from logging.handlers import RotatingFileHandler

# ===================== 日志配置 =====================
def setup_logger():
    """配置日志器：输出到控制台和文件，按文件大小轮转"""
    # 日志器
    logger = logging.getLogger("AdvancedBBLogger")
    logger.setLevel(logging.DEBUG)  # 基础日志级别
    logger.propagate = False  # 防止重复输出

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只输出INFO及以上
    console_handler.setFormatter(formatter)

    # 2. 文件处理器（按大小轮转，最多保留5个日志文件，每个最大5MB）
    file_handler = RotatingFileHandler(
        'sql_manager.log',
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件记录DEBUG及以上
    file_handler.setFormatter(formatter)

    # 添加处理器
    if not logger.handlers:  # 避免重复添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# 初始化日志器
logger = setup_logger()