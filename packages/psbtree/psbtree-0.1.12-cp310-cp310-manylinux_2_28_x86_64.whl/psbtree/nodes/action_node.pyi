#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行为树节点模块

该模块提供了行为树节点的基类和实现。
"""

from typing import Dict, List, Optional, Any, Type, Callable, Protocol, runtime_checkable
from psbtree.core import BehaviorTreeFactory, SyncActionNode, NodeStatus, \
    registerNodeType, NodeConfig, TreeNode, InputPort, BTreeData


@runtime_checkable
class ActionNodeProtocol(Protocol):
    """
    动作节点协议
    
    定义了所有行为树节点必须实现的接口。
    使用Protocol和runtime_checkable确保运行时类型检查。
    """
    
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: 'TreeNode') -> 'NodeStatus': ...


class SimpleActionNode:
    """
    简单动作节点基类
    
    该类是所有行为树节点的基类，提供了基本的节点功能。
    所有行为树节点类型（动作节点、条件节点、装饰器节点、控制节点）都继承自此类。
    
    属性:
        ports: 节点端口列表，用于定义节点的输入输出接口
    """
    ports: List[Dict[str, str]]
    
    @staticmethod
    def tick(node: 'TreeNode') -> 'NodeStatus': ...
    
    @classmethod
    def providedPorts(cls) -> List[Dict[str, str]]: ...


class ActionNode(SimpleActionNode):
    """
    动作节点类
    
    该类实现了基本的动作节点功能。
    """
    
    def __init__(self, name: str, config: Optional[NodeConfig] = None) -> None: ...
    
    @staticmethod
    def tick(node: 'TreeNode') -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class ConditionNode(SimpleActionNode):
    """
    条件节点类
    
    该类实现了基本的条件节点功能。
    """
    
    def __init__(self, name: str, config: Optional[NodeConfig] = None) -> None: ...
    
    @staticmethod
    def tick(node: 'TreeNode') -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class DecoratorNode(SimpleActionNode):
    """
    装饰器节点类
    
    该类实现了基本的装饰器节点功能。
    """
    
    def __init__(self, name: str, config: Optional[NodeConfig] = None) -> None: ...
    
    @staticmethod
    def tick(node: 'TreeNode') -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


class ControlNode(SimpleActionNode):
    """
    控制节点类
    
    该类实现了基本的控制节点功能。
    """
    
    def __init__(self, name: str, config: Optional[NodeConfig] = None) -> None: ...
    
    @staticmethod
    def tick(node: 'TreeNode') -> NodeStatus: ...
    
    @staticmethod
    def providedPorts() -> List[Dict[str, str]]: ...


def register_node(factory: BehaviorTreeFactory, node_class: Type[SimpleActionNode], node_name: str) -> None: ... 