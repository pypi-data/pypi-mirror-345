import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import LLMConfig
from .cache import LLMCache
from .logger import LLMLogger

class LLMClient:
    """轻量级LLM API客户端
    
    提供简单易用的LLM API调用接口，支持缓存、重试和日志记录
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, **kwargs):
        """初始化LLM客户端
        
        Args:
            config: LLM配置对象，如果为None则创建默认配置
            **kwargs: 配置参数，将覆盖config中的同名参数
        """
        # 初始化配置
        self.config = config or LLMConfig()
        if kwargs:
            self.config.update(**kwargs)
        
        # 初始化日志
        self.logger = LLMLogger(
            debug_enabled=self.config.debug_enabled,
            debug_dir=self.config.debug_dir
        )
        self.log = self.logger.get_logger()
        
        # 初始化缓存
        if self.config.cache_enabled:
            self.cache = LLMCache(
                cache_path=self.config.cache_path,
                expiry_days=self.config.cache_expiry_days
            )
        else:
            self.cache = None
        
        self.log.info(f"LLMClient初始化完成，模型: {self.config.model}")
        if self.config.cache_enabled:
            self.log.info(f"缓存已启用，路径: {self.config.cache_path}")
        if self.config.debug_enabled:
            self.log.info(f"调试模式已启用，日志目录: {self.config.debug_dir}")
    
    def _call_api(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """调用LLM API
        
        Args:
            messages: 消息列表
            **kwargs: 其他API参数
            
        Returns:
            API响应JSON
        """
        # 在方法内部使用配置值
        retry_stop = stop_after_attempt(self.config.retry_attempts)
        retry_wait = wait_exponential(multiplier=1, 
                                    min=self.config.retry_min_wait, 
                                    max=self.config.retry_max_wait)
        
        @retry(stop=retry_stop, wait=retry_wait)
        def _make_request():
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature)
            }
            
            # 添加其他可能的参数
            for key, value in kwargs.items():
                if key not in data and key not in ["source"]:
                    data[key] = value
            
            self.log.info(f"发送API请求到 {self.config.api_base}...")
            response = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout  # 添加超时设置
            )
            
            response.raise_for_status()
            return response.json()
            
        # 调用内部函数并返回结果
        return _make_request()
    
    def completion(self, prompt: str, source: str = "", **kwargs) -> str:
        """发送单轮对话请求
        
        Args:
            prompt: 提示文本
            source: 请求来源标识，用于调试日志
            **kwargs: 其他API参数
            
        Returns:
            API响应文本
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, source, **kwargs)
    
    def chat_completion(self, messages: List[Dict[str, str]], source: str = "", **kwargs) -> str:
        """发送多轮对话请求
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}]
            source: 请求来源标识，用于调试日志
            **kwargs: 其他API参数
            
        Returns:
            API响应文本
        """
        # 准备请求数据，用于缓存键计算
        request_data = {
            "messages": messages,
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }
        
        # 尝试从缓存获取响应
        if self.cache and self.config.cache_enabled:
            cached_response = self.cache.get(request_data, self.config.model)
            if cached_response:
                self.log.info(f"从缓存获取响应，模型: {self.config.model}")
                
                # 即使是缓存命中，如果开启了调试模式，也记录请求和响应
                if self.config.debug_enabled:
                    prompt = messages[-1]["content"] if messages else ""
                    self.logger.log_api_request(prompt, cached_response, self.config.model, f"{source}_cache_hit")
                    
                return cached_response
        
        # 缓存未命中，调用API
        try:
            self.log.info(f"缓存未命中，准备调用LLM模型: {self.config.model}")
            result = self._call_api(messages, **kwargs)
            
            # 获取响应内容
            content = result['choices'][0]['message']['content']
            
            # 将响应存入缓存
            if self.cache and self.config.cache_enabled:
                self.cache.set(request_data, content, self.config.model)
            
            # 如果开启了调试模式，记录请求和响应
            if self.config.debug_enabled:
                prompt = messages[-1]["content"] if messages else ""
                self.logger.log_api_request(prompt, content, self.config.model, source)
            
            self.log.info("LLM API请求成功")
            return content
        except Exception as e:
            self.log.error(f"调用LLM API失败: {e}")
            raise
    
    def clear_cache(self, days: Optional[int] = None) -> int:
        """清理过期缓存
        
        Args:
            days: 保留最近几天的缓存，如果为None则使用配置中的过期天数
            
        Returns:
            删除的缓存条目数
        """
        if self.cache and self.config.cache_enabled:
            return self.cache.clear(days)
        return 0
    
    def set_debug(self, enabled: bool) -> None:
        """设置调试模式
        
        Args:
            enabled: 是否启用调试模式
        """
        self.config.debug_enabled = enabled
        self.logger.set_debug(enabled)
        self.log.info(f"调试模式已{'启用' if enabled else '禁用'}")
    
    def get_token_count(self, text: str) -> int:
        """估算文本的token数量
        
        Args:
            text: 要估算的文本
            
        Returns:
            估算的token数量
        """
        # 简单估算方法：1个token ≈ 4个英文字符或1个中文字符
        chinese_chars = sum('\u4e00' <= char <= '\u9fff' for char in text)
        other_chars = len(text) - chinese_chars
        # 对于中文文本，每个字符算作一个token
        return chinese_chars + max(1, other_chars // 4)