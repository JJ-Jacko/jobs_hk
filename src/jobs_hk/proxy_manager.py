import functools
import threading
from collections import Counter
from dataclasses import dataclass
from typing import List

from jobs_hk.exceptions import NeedWaiting
from jobs_hk.web import proxy_server_active


def thread_lock(func):
    @functools.wraps(func)
    def wrapper(self: "ProxyPool", *args, **kwargs):
        with self.lock:
            result = func(self, *args, **kwargs)
        return result
    return wrapper


@dataclass(init=False)
class Node:
    host: str
    port: int
    user: str | None
    jamming_level: int
    
    def __init__(
            self,
            host: str,
            port: int
    ):
        self.host = host
        self.port = port
        
        self.user = None
        self.jamming_level = 0


class ProxyPool:
    nodes: List[Node]
    lock: threading.Lock
    
    
    def __init__(
            self,
            host: str,
            port_start: int,
            offset: int,
            lock: threading.Lock
    ):
        self.nodes = []
        self.lock = lock
    
        for i in range(offset):
            port = port_start + i
            node = Node(host, port)
            
            if not proxy_server_active(host, port):
                continue
            
            self.nodes.append(node)

    def __repr__(self):
        counter_jl = Counter(
            node.jamming_level
            for node in self.nodes
        )
        
        total = len(self.nodes)
        busy = sum([
            1
            for node in self.nodes
            if node.user is not None
        ])
        usage_rate = busy / total if total else 0
        
        return (
            f"ProxyPool"
            f"(Usage: {usage_rate:.2%}, "
            f"Jamming-0: {counter_jl.get(0, 0)})"
        )

    @thread_lock
    def get_proxy(self, user: str):
        """
        Get proxy `host` & `port` in a dict

        Raises:
            ValueError: The user has used proxy in pool.
            NeedWaiting: When there is no node in proxy pool happen.
        """
        
        nodes_available: List[Node] = []
        for n in self.nodes:
            if n.user == user:
                raise ValueError(f"The user, {user}, has used proxy in pool.")
            
            if n.user is None:
                nodes_available.append(n)
        
        if not nodes_available:
            raise NeedWaiting
             
        node = min(nodes_available, key=lambda n: n.jamming_level)
        node.user = user
        return {
            "host": node.host,
            "port": node.port
        }
    
    @thread_lock
    def clear_proxy(self, user: str):
        """Clear proxy and increase the jamming level of the node"""
        
        for node in self.nodes:
            if node.user == user:
                node.user = None
                node.jamming_level += 10
                return
        
        raise ValueError(f"The user, {user}, is not used proxy in pool.")
    