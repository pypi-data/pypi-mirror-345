#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
顺序引擎模块

该模块实现了顺序版本的B树引擎，适用于不需要并行处理的场景。
"""

import os
import time
from typing import Any, Dict, List, Optional, Type, Callable
from loguru import logger

from psbtree.core import (
    BehaviorTreeFactory,     
    NodeStatus, 
    TreeNode
)

from psbtree.nodes.action_node import SimpleActionNode
from psbtree import check_authorization

class SequentialEngine:
    """
    顺序B树引擎类
    
    该类实现了顺序版本的B树操作，所有操作都在主线程中顺序执行。
    """
    
    def __init__(self) -> None: ...
    
    def _check_tree_exists(self) -> None: ...
    
    def register_action_behavior(self, action_id: str, tick_functor: Callable[[TreeNode], NodeStatus], 
                              ports_list: List[Dict[str, str]]) -> None: ...
    
    def register_action_class(self, action_class: Type[SimpleActionNode], action_id: Optional[str] = None) -> None: ...
    
    def create_tree_from_text(self, xml_text: str) -> Any: ...
    
    def create_tree_from_file(self, file_path: str) -> Any: ...
    
    def get_tree(self) -> Any: ...
    
    def reset_tree(self) -> None: ...
    
    def get_tree_status(self) -> Dict[str, Any]: ...
    
    def tick_once(self) -> NodeStatus: ...
    
    def tick_until_failure(self) -> int: ...
    
    def tick_until_success(self) -> int: ...
    
    def tick_n_times(self, n: int) -> List[NodeStatus]: ...
    
    def get_blackboard_data(self, key: str) -> Any: ...
    
    def set_blackboard_data(self, key: str, value: Any) -> None: ...
    
    def get_all_blackboard_data(self) -> Dict[str, Any]: ... 