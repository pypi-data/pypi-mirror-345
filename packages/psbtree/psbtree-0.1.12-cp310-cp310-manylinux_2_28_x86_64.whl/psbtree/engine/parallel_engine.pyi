#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
并行引擎模块

该模块实现了并行版本的B树引擎，适用于需要并行处理的场景。
每个行为树在独立的进程中运行，提高处理效率。
"""

import os
import time
import multiprocessing
from typing import Any, Dict, List, Optional, Type, Callable, Tuple
from loguru import logger

from psbtree.core import (
    BehaviorTreeFactory,     
    NodeStatus, 
    TreeNode
)

from psbtree.nodes.action_node import SimpleActionNode
from psbtree.engine.sequential_engine import SequentialEngine

class TreeProcess(multiprocessing.Process):
    """
    行为树进程类
    
    该类封装了单个行为树的处理进程，负责在独立进程中运行行为树。
    """
    
    def __init__(self, tree_id: str, xml_text: str, action_registrations: List[Tuple[str, Callable, List[Dict[str, str]]]], 
                 command_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue) -> None: ...
    
    def run(self) -> None: ...
    
    def _process_command(self, command: Dict[str, Any]) -> None: ...

class ParallelEngine:
    """
    并行B树引擎类
    
    该类实现了并行版本的B树操作，每个行为树在独立的进程中运行。
    """
    
    def __init__(self) -> None: ...
    
    def register_action_behavior(self, action_id: str, tick_functor: Callable[[TreeNode], NodeStatus], 
                              ports_list: List[Dict[str, str]]) -> None: ...
    
    def register_action_class(self, action_class: Type[SimpleActionNode], action_id: Optional[str] = None) -> None: ...
    
    def create_tree_from_text(self, xml_text: str, tree_id: Optional[str] = None) -> str: ...
    
    def create_tree_from_file(self, file_path: str, tree_id: Optional[str] = None) -> str: ...
    
    def _check_tree_exists(self, tree_id: str) -> None: ...
    
    def get_tree_ids(self) -> List[str]: ...
    
    def _send_command(self, tree_id: str, command_type: str, params: Dict[str, Any] = None) -> Any: ...
    
    def tick_once(self, tree_id: str) -> NodeStatus: ...
    
    def tick_until_failure(self, tree_id: str) -> int: ...
    
    def tick_until_success(self, tree_id: str) -> int: ...
    
    def tick_n_times(self, tree_id: str, n: int) -> List[NodeStatus]: ...
    
    def get_tree_status(self, tree_id: str) -> Dict[str, Any]: ...
    
    def get_blackboard_data(self, tree_id: str, key: str) -> Any: ...
    
    def set_blackboard_data(self, tree_id: str, key: str, value: Any) -> None: ...
    
    def get_all_blackboard_data(self, tree_id: str) -> Dict[str, Any]: ...
    
    def reset_tree(self, tree_id: str) -> None: ...
    
    def stop_tree(self, tree_id: str) -> None: ...
    
    def stop_all_trees(self) -> None: ...
    
    def __del__(self) -> None: ... 