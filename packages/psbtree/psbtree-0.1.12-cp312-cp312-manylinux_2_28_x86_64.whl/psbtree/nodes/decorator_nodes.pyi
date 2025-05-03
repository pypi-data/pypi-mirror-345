#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
装饰器节点模块

该模块提供了行为树常用的装饰器节点实现。
"""

from typing import Dict, List, Optional, Any, Callable
from psbtree.core import NodeStatus, TreeNode

from psbtree.nodes.action_node import DecoratorNode


class InverterNode(DecoratorNode):
    """
    反转节点类
    
    该类实现了反转子节点执行结果的装饰器节点。
    如果子节点返回成功，则返回失败；如果子节点返回失败，则返回成功。
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...


class RetryNode(DecoratorNode):
    """
    重试节点类
    
    该类实现了重试子节点的装饰器节点。
    当子节点失败时，会重试指定次数。
    """
    
    def __init__(self, name: str, max_attempts: int = 3, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...


class RepeatNode(DecoratorNode):
    """
    重复节点类
    
    该类实现了重复执行子节点的装饰器节点。
    会重复执行子节点指定次数。
    """
    
    def __init__(self, name: str, num_cycles: int = 1, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...


class TimeoutNode(DecoratorNode):
    """
    超时节点类
    
    该类实现了超时控制的装饰器节点。
    如果子节点在指定时间内未完成，则返回失败。
    """
    
    def __init__(self, name: str, timeout_ms: int = 1000, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...


class AlwaysSuccessNode(DecoratorNode):
    """
    始终成功节点类
    
    该类实现了始终返回成功的装饰器节点。
    无论子节点的执行结果如何，都返回成功。
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...


class AlwaysFailureNode(DecoratorNode):
    """
    始终失败节点类
    
    该类实现了始终返回失败的装饰器节点。
    无论子节点的执行结果如何，都返回失败。
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ... 