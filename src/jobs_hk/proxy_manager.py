import functools
import threading
from dataclasses import dataclass
from typing import List

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

    @thread_lock
    def get_proxy(self, user: str):
        """Get proxy `host` & `port` in a dict"""
        
        for node in self.nodes:
            if node.user == user:
                raise ValueError(f"The user, {user}, has used proxy in pool.")
            
            if node.user is None:
                node.user = user
                return {
                    "host": node.host,
                    "port": node.port
                }
        
        raise Exception("Need queue")
    
    @thread_lock
    def clear_proxy(self, user: str):
        """Clear proxy and increase the jamming level of the node"""
        
        for node in self.nodes:
            if node.user == user:
                node.user = None
                node.jamming_level += 10
                return
        
        raise ValueError(f"The user, {user}, is not used proxy in pool.")
    