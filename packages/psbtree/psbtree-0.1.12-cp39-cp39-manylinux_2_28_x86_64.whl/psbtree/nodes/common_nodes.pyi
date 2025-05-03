#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通用节点模块

该模块提供了一系列通用的行为树节点，可以在不同的行为树中重复使用。
"""

import time
from typing import Any, Dict, List, Optional, Callable
from loguru import logger

from psbtree.core import NodeStatus, TreeNode
from psbtree.nodes.action_node import SimpleActionNode

class SleepNode(SimpleActionNode):
    """
    休眠节点
    
    该节点会在执行时休眠指定的时间，然后返回成功状态。
    可用于在行为树中引入延时。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: TreeNode) -> NodeStatus: ...


class LogNode(SimpleActionNode):
    """
    日志节点
    
    该节点会在执行时记录一条日志消息，然后返回成功状态。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: TreeNode) -> NodeStatus: ...


class SetBlackboardNode(SimpleActionNode):
    """
    设置黑板数据节点
    
    该节点会在执行时设置行为树黑板中的数据，然后返回成功状态。
    可用于在行为树中传递数据。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: TreeNode) -> NodeStatus: ...


class GetBlackboardNode(SimpleActionNode):
    """
    获取黑板数据节点
    
    该节点会在执行时从行为树黑板中获取数据，然后返回成功状态。
    可用于在行为树中读取数据。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: TreeNode) -> NodeStatus: ...


class ConditionNode(SimpleActionNode):
    """
    条件节点
    
    该节点会根据条件返回成功或失败状态。
    可用于在行为树中实现条件判断。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: TreeNode) -> NodeStatus: ...


class CounterNode(SimpleActionNode):
    """
    计数器节点
    
    该节点会维护一个计数器，每次执行时计数器加1，达到指定值后重置并返回成功状态。
    可用于在行为树中实现循环计数。
    """
    
    ports: List[Dict[str, str]]
    
    def __init__(self) -> None: ...
    
    def tick(self, node: TreeNode) -> NodeStatus: ...


class TimerNode(SimpleActionNode):
    """
    定时器节点
    
    该节点会在指定的时间后返回成功状态。
    可用于在行为树中实现定时操作。
    """
    
    ports: List[Dict[str, str]]
    
    def __init__(self) -> None: ...
    
    def tick(self, node: TreeNode) -> NodeStatus: ... 