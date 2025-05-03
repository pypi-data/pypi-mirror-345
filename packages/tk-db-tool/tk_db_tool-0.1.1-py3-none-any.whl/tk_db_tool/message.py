import logging

class Message(object):
    def __init__(self, message_handler =None):
        if message_handler is None:
            logger = logging.getLogger(__name__)
            self.message_handler = logger
        else:
            self.message_handler = message_handler
    def debug(self, message: str):
        self.message_handler.debug(message)
    
    def info(self, message: str):
        self.message_handler.info(message)
    def warning(self, message: str):
        self.message_handler.warning(message)
    def error(self, message: str):
        self.message_handler.error(message)
    def critical(self, message: str):
        self.message_handler.critical(message)
    
    def set_logger_level(self, level: str):
        level_maps= {
            # 标准logging.Handler及其子类的映射
            logging.Handler:{
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL,
                "none": logging.NOTSET,
                "all": logging.DEBUG,
                "default": logging.INFO,
            }
        }
        temp_level_str = level.lower()
        # 根据handler类型选择合适的映射
        level_map = None
        handler_type = type(self.message_handler)
        
        # 1. 首先检查是否是标准logging handler
        if isinstance(self.message_handler, logging.Handler):
            level_map = level_maps[logging.Handler]
        
        # 检查是否正确获取到了映射
        if level_map is None:
            raise ValueError(f"没有正确配置日志器配置,handler 类型: {handler_type.__name__}")
        
        # 获取对应的级别值
        level_value = level_map.get(temp_level_str)
        if level_value is None:
            available_levels = ", ".join(level_map.keys())
            raise ValueError(
                f"无效的日志级别: {level},handler 类型: {handler_type.__name__}\n"
                f"可用级别: {available_levels}"
                )
        
        # 根据不同类型设置级别
        try:
            # 标准logging handler
            if isinstance(self.message_handler, logging.Handler):
                self.message_handler.setLevel(level_value)
            # 有setLevel方法的自定义handler
            elif hasattr(self.message_handler, "setLevel"):
                self.message_handler.setLevel(level_value)
            # 有level属性的自定义handler
            elif hasattr(self.message_handler, "level"):
                self.message_handler.level = level_value
            # 其他情况尝试直接设置属性
            else:
                raise  ValueError(f"无法设置日志级别 (handler类型: {handler_type.__name__})")
        except Exception as e:
            raise RuntimeError(
                f"设置日志级别失败 (handler类型: {handler_type.__name__}): {str(e)}"
            ) from e

    def set_message_handler(self, message_handler):
        self.message_handler = message_handler
    
    def set_message_config(self, config:dict):
        try:
            if isinstance(self.message_handler, logging.Handler):
                self.message_handler.basicConfig(**config)
            else:
                raise ValueError(f"暂不支持该类日志配置 (handler类型: {type(self.message_handler).__name__})")
        except Exception as e:
            raise RuntimeError(
                f"设置日志配置失败 (handler类型: {type(self.message_handler).__name__}): {str(e)}"
            ) from e

message = Message()
