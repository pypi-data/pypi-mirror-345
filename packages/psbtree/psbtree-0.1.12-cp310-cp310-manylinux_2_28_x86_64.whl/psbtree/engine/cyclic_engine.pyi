#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
循环引擎模块

该模块实现了循环版本的B树引擎，在后台线程中循环执行tick_once操作。
"""

import os
import time
import threading
from typing import Any, Dict, List, Optional, Type, Callable
from loguru import logger

from psbtree.core import (
    BehaviorTreeFactory,     
    NodeStatus, 
    TreeNode
)

from psbtree.nodes.action_node import SimpleActionNode
from psbtree import check_authorization

class CyclicEngine:
    """
    循环B树引擎类
    
    该类实现了循环版本的B树操作，在后台线程中循环执行tick_once操作。
    """
    
    def __init__(self) -> None: ...
    
    def _check_tree_exists(self) -> None: ...
    
    def _tree_thread_func(self) -> None: ...
    
    def start_tree_thread(self) -> None: ...
    
    def stop_tree_thread(self) -> None: ...
    
    def register_action_behavior(self, action_id: str, tick_functor: Callable[[TreeNode], NodeStatus], 
                              ports_list: List[Dict[str, str]]) -> None: ...
    
    def register_action_class(self, action_class: Type[SimpleActionNode], action_id: Optional[str] = None) -> None: ...
    
    def create_tree_from_text(self, xml_text: str) -> Any: ...
    
    def create_tree_from_file(self, file_path: str) -> Any: ...
    
    def get_tree(self) -> Any: ...
    
    def reset_tree(self) -> None: ...
    
    def get_tree_status(self) -> Dict[str, Any]: ...
    
    def get_blackboard_data(self, key: str) -> Any: ...
    
    def set_blackboard_data(self, key: str, value: Any) -> None: ...
    
    def get_all_blackboard_data(self) -> Dict[str, Any]: ... 