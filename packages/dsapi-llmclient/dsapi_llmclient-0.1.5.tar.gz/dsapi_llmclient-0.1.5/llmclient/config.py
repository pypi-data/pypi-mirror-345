import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class LLMConfig:
    """LLM API配置管理类
    
    用于管理LLM API的配置参数，支持从环境变量加载配置
    
    作者: Leo <marticle.ios@gmail.com>
    """
    
    def __init__(self, 
                 api_base: Optional[str] = None,
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None,
                 cache_enabled: Optional[bool] = None,
                 cache_path: Optional[str] = None,
                 cache_expiry_days: Optional[int] = None,
                 debug_enabled: Optional[bool] = None,
                 debug_dir: Optional[str] = None,
                 retry_attempts: Optional[int] = None,
                 retry_min_wait: Optional[int] = None,
                 retry_max_wait: Optional[int] = None,
                 load_env: bool = True):
        """初始化LLM配置
        
        Args:
            api_base: API基础URL
            api_key: API密钥
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
            cache_enabled: 是否启用缓存
            cache_path: 缓存数据库路径
            cache_expiry_days: 缓存过期天数
            debug_enabled: 是否启用调试
            debug_dir: 调试日志目录
            retry_attempts: 重试次数
            retry_min_wait: 最小重试等待时间(秒)
            retry_max_wait: 最大重试等待时间(秒)
            load_env: 是否加载.env文件
        """
        # 加载环境变量
        if load_env:
            load_dotenv()
            
        # API配置
        self.api_base = api_base or os.getenv('LLM_API_BASE')
        self.api_key = api_key or os.getenv('LLM_API_KEY')
        self.model = model or os.getenv('LLM_MODEL')
        self.max_tokens = max_tokens or int(os.getenv('LLM_MAX_TOKENS', '8000'))
        self.temperature = temperature or float(os.getenv('LLM_TEMPERATURE', '1.0'))
        
        # 缓存配置
        self.cache_enabled = cache_enabled if cache_enabled is not None else \
                            os.getenv('LLM_CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_path = cache_path or os.getenv('LLM_CACHE_PATH') or \
                         str(Path.home() / '.llmclient' / 'cache.db')
        self.cache_expiry_days = cache_expiry_days or int(os.getenv('LLM_CACHE_EXPIRY_DAYS', '30'))
        
        # 调试配置
        self.debug_enabled = debug_enabled if debug_enabled is not None else \
                           os.getenv('LLM_DEBUG', 'false').lower() == 'true'
        self.debug_dir = debug_dir or os.getenv('LLM_DEBUG_DIR') or \
                       str(Path.home() / '.llmclient' / 'logs')
        
        # 重试配置
        self.retry_attempts = retry_attempts or int(os.getenv('LLM_RETRY_ATTEMPTS', '3'))
        self.retry_min_wait = retry_min_wait or int(os.getenv('LLM_RETRY_MIN_WAIT', '2'))
        self.retry_max_wait = retry_max_wait or int(os.getenv('LLM_RETRY_MAX_WAIT', '10'))
        self.timeout = int(os.getenv("LLM_TIMEOUT", 30))  # 默认30秒
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典
        
        Returns:
            包含所有配置的字典
        """
        return {
            'api_base': self.api_base,
            'api_key': self.api_key,
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'cache_enabled': self.cache_enabled,
            'cache_path': self.cache_path,
            'cache_expiry_days': self.cache_expiry_days,
            'debug_enabled': self.debug_enabled,
            'debug_dir': self.debug_dir,
            'retry_attempts': self.retry_attempts,
            'retry_min_wait': self.retry_min_wait,
            'retry_max_wait': self.retry_max_wait
        }
    
    def update(self, **kwargs) -> None:
        """更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)