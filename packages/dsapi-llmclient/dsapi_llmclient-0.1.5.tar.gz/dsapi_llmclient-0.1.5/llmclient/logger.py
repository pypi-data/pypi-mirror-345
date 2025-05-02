import os
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class LLMLogger:
    """LLM API日志管理类
    
    提供详细的API请求和响应日志记录功能
    """
    
    def __init__(self, debug_enabled: bool = False, debug_dir: Optional[str] = None):
        """初始化日志管理器
        
        Args:
            debug_enabled: 是否启用调试日志
            debug_dir: 调试日志目录
        """
        self.debug_enabled = debug_enabled
        self.debug_dir = debug_dir or str(Path.home() / '.llmclient' / 'logs')
        self.call_counter = 0
        
        # 确保日志目录存在
        if self.debug_enabled and self.debug_dir:
            os.makedirs(self.debug_dir, exist_ok=True)
        
        # 配置基本日志
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """配置日志记录器"""
        logger = logging.getLogger('llmclient')
        
        # 如果已经有处理器，不重复添加
        if logger.handlers:
            return
            
        # 设置日志级别
        logger.setLevel(logging.DEBUG if self.debug_enabled else logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 如果启用调试，添加文件处理器
        if self.debug_enabled:
            log_file = os.path.join(self.debug_dir, f"llmclient_{datetime.datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    def log_api_request(self, prompt: str, response: str, model: str, source: str = "") -> None:
        """记录API请求和响应到文件
        
        Args:
            prompt: API请求提示
            response: API响应
            model: 使用的模型
            source: 请求来源标识
        """
        if not self.debug_enabled:
            return
        
        try:
            self.call_counter += 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            source_tag = f"_{source}" if source else ""
            log_file = os.path.join(self.debug_dir, f"api_log_{timestamp}_{self.call_counter:03d}{source_tag}.txt")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== LLM API请求 #{self.call_counter} ===\n")
                f.write(f"=== 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"=== 来源: {source} ===\n") if source else None
                f.write(f"=== 模型: {model} ===\n\n")
                f.write("=== 提示 ===\n")
                f.write(prompt)
                f.write("\n\n=== 响应 ===\n")
                f.write(response)
            
            logging.getLogger('llmclient').info(f"API请求日志已保存到: {log_file}")
        except Exception as e:
            logging.getLogger('llmclient').error(f"保存API请求日志失败: {str(e)}")
    
    def get_logger(self) -> logging.Logger:
        """获取配置好的日志记录器
        
        Returns:
            配置好的Logger实例
        """
        return logging.getLogger('llmclient')
    
    def set_debug(self, enabled: bool) -> None:
        """设置调试模式
        
        Args:
            enabled: 是否启用调试模式
        """
        self.debug_enabled = enabled
        logger = logging.getLogger('llmclient')
        logger.setLevel(logging.DEBUG if enabled else logging.INFO)
        
        # 如果启用调试且没有文件处理器，添加一个
        if enabled:
            has_file_handler = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
            if not has_file_handler:
                log_file = os.path.join(self.debug_dir, f"llmclient_{datetime.datetime.now().strftime('%Y%m%d')}.log")
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)