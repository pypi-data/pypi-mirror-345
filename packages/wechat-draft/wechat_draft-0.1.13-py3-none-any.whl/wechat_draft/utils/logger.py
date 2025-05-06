# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/21 19:54
# 文件名称： logger.py
# 项目描述： 日志
# 开发工具： PyCharm
import logging


def setup_logger(log_level: str = 'INFO') -> logging.Logger:
    """
    设置日志记录器

    :param log_level: 日志记录器日志级别
    :return: 日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger('wechat_draft')
    logger.setLevel(log_level)  # 设置日志级别

    # 创建控制台输出流
    console_handler = logging.StreamHandler()

    # 设置日志输出格式
    formatter = logging.Formatter('%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    # 将处理器添加到记录器中
    logger.addHandler(console_handler)
    return logger


# 日志logger
log = setup_logger("INFO")


def set_log_level(log_level: str = 'INFO', logger: logging.Logger = log):
    """
    设置日志记录器日志级别
    :param log_level: 日志记录器日志级别
    :param logger: 日志记录器
    :return: 日志记录器
    """
    try:
        logger.setLevel(log_level)
    except ValueError as e:
        logger.error(f"设置日志记录器日志级别失败，错误信息：{e}")

    return logger
