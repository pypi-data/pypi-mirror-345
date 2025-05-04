from typing import Dict, List, Tuple, Optional
from collections import deque
from nonebot import logger
from .config import plugin_config

# 消息类型定义
Message = Tuple[str, str]  # (发送者, 消息内容)

class GroupMessageQueue:
    """群聊消息队列管理类"""
    
    def __init__(self):
        # 群组ID -> 消息队列的映射
        self._group_queues: Dict[str, deque[Message]] = {}
        self._max_length = plugin_config.max_history_length
    
    def add_message(self, group_id: str, sender: str, content: str) -> None:
        """添加消息到指定群聊的消息队列
        
        Args:
            group_id: 群聊ID
            sender: 发送者名称或ID
            content: 消息内容
        """
        if group_id not in self._group_queues:
            self._group_queues[group_id] = deque(maxlen=self._max_length)
        
        self._group_queues[group_id].append((sender, content))
        logger.debug(f"Added message to group {group_id}: {sender}: {content}")
    
    def get_history(self, group_id: str) -> List[Message]:
        """获取指定群聊的历史消息
        
        Args:
            group_id: 群聊ID
            
        Returns:
            历史消息列表，如果群聊不存在则返回空列表
        """
        if group_id not in self._group_queues:
            return []
        
        return list(self._group_queues[group_id])
    
    def clear_history(self, group_id: str) -> None:
        """清空指定群聊的历史消息
        
        Args:
            group_id: 群聊ID
        """
        if group_id in self._group_queues:
            self._group_queues[group_id].clear()
            logger.info(f"Cleared message history for group {group_id}")

# 全局消息队列实例
message_queue = GroupMessageQueue()