#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
条件节点模块

该模块提供了行为树常用的条件节点实现。
"""

from typing import Dict, List, Optional, Any, Callable
from psbtree.core import NodeStatus, TreeNode

from psbtree.nodes.action_node import ConditionNode


class IsValueNode(ConditionNode):
    """
    值判断节点类
    
    该类实现了判断输入值是否等于指定值的条件节点。
    """
    
    def __init__(self, name: str, value: Any, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class IsGreaterThanNode(ConditionNode):
    """
    大于判断节点类
    
    该类实现了判断输入值是否大于指定阈值的条件节点。
    """
    
    def __init__(self, name: str, threshold: Any, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class IsLessThanNode(ConditionNode):
    """
    小于判断节点类
    
    该类实现了判断输入值是否小于指定阈值的条件节点。
    """
    
    def __init__(self, name: str, threshold: Any, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class IsTrueNode(ConditionNode):
    """
    真值判断节点类
    
    该类实现了判断输入值是否为True的条件节点。
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class IsFalseNode(ConditionNode):
    """
    假值判断节点类
    
    该类实现了判断输入值是否为False的条件节点。
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class CustomConditionNode(ConditionNode):
    """
    自定义条件节点类
    
    该类实现了使用自定义函数作为条件的条件节点。
    """
    
    def __init__(self, name: str, condition_func: Callable[[Any], bool], config: Optional[Dict] = None) -> None: ...
    
    def tick(self) -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ... 