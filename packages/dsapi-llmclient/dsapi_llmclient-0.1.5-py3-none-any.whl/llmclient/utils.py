import re
import json
from typing import Dict, Any, List, Optional, Union

def format_prompt(template: str, **kwargs) -> str:
    """格式化提示模板
    
    Args:
        template: 提示模板字符串，使用{key}作为占位符
        **kwargs: 要替换的变量
        
    Returns:
        格式化后的提示字符串
    """
    return template.format(**kwargs)

def extract_json(text, schema=None):
    """从文本中提取JSON数据
    
    Args:
        text: 包含JSON数据的文本
        schema: 可选的JSON Schema，用于验证提取的数据
        
    Returns:
        提取的JSON数据，如果提取失败则返回None
    """
    import re
    import json
    from jsonschema import validate, ValidationError
    
    # 尝试查找JSON块
    json_pattern = r'```json\s*([\s\S]*?)\s*```|{[\s\S]*?}'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            # 清理匹配文本
            json_str = match.strip()
            if not json_str:
                continue
                
            # 确保是有效的JSON格式
            if not (json_str.startswith('{') and json_str.endswith('}')):
                continue
                
            # 解析JSON
            data = json.loads(json_str)
            
            # 如果提供了schema，验证数据
            if schema:
                try:
                    validate(instance=data, schema=schema)
                except ValidationError:
                    continue
                    
            return data
        except json.JSONDecodeError:
            continue
    
    # 如果没有找到有效的JSON，尝试直接解析整个文本
    try:
        data = json.loads(text)
        
        # 如果提供了schema，验证数据
        if schema:
            try:
                validate(instance=data, schema=schema)
                return data
            except ValidationError:
                pass
        else:
            return data
    except json.JSONDecodeError:
        pass
        
    return None

def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """将长文本分割成小块
    
    Args:
        text: 要分割的文本
        chunk_size: 每块的最大字符数
        overlap: 相邻块之间的重叠字符数
        
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # 如果不是最后一块，尝试在一个自然的断点处分割
        if end < len(text):
            # 尝试在段落、句子或空格处分割
            for separator in ['\n\n', '\n', '. ', ' ']:
                pos = text.rfind(separator, start, end)
                if pos > start:
                    end = pos + len(separator)
                    break
        
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
    
    return chunks