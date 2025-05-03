#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
控制节点模块

该模块提供了行为树中常用的控制节点实现，包括序列节点、选择节点、并行节点等。
"""

from typing import List, Optional, Dict, Any, Callable
from psbtree.nodes.action_node import ControlNode, NodeStatus, TreeNode, NodeConfig

class SequenceNode(ControlNode):
    """序列节点
    
    按顺序执行所有子节点，直到某个子节点失败或所有子节点都成功。
    如果所有子节点都成功，则返回成功；如果某个子节点失败，则返回失败。
    """
    
    def __init__(self, name: str, children: List[TreeNode], config: Optional[NodeConfig] = None) -> None: ...
    
    def tick(self, tree_node: TreeNode) -> NodeStatus: ...


class FallbackNode(ControlNode):
    """选择节点
    
    按顺序执行所有子节点，直到某个子节点成功或所有子节点都失败。
    如果某个子节点成功，则返回成功；如果所有子节点都失败，则返回失败。
    """
    
    def __init__(self, name: str, children: List[TreeNode], config: Optional[NodeConfig] = None) -> None: ...
    
    def tick(self, tree_node: TreeNode) -> NodeStatus: ...


class ParallelNode(ControlNode):
    """并行节点
    
    同时执行所有子节点，根据成功和失败的阈值决定返回状态。
    """
    
    def __init__(self, name: str, children: List[TreeNode], success_threshold: int, failure_threshold: int, config: Optional[NodeConfig] = None) -> None: ...
    
    def tick(self, tree_node: TreeNode) -> NodeStatus: ...


class IfThenElseNode(ControlNode):
    """条件执行节点
    
    根据条件节点的执行结果决定执行then_node还是else_node。
    """
    
    def __init__(self, name: str, condition: TreeNode, then_node: TreeNode, else_node: TreeNode, config: Optional[NodeConfig] = None) -> None: ...
    
    def tick(self, tree_node: TreeNode) -> NodeStatus: ...


class WhileDoNode(ControlNode):
    """循环执行节点
    
    当条件节点成功时，循环执行do_node，直到条件节点失败或达到最大迭代次数。
    """
    
    def __init__(self, name: str, condition: TreeNode, do_node: TreeNode, max_iterations: int = -1, config: Optional[NodeConfig] = None) -> None: ...
    
    def tick(self, tree_node: TreeNode) -> NodeStatus: ... 