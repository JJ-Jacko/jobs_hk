"""Waiting related classes and functions"""

import random
import time


class Waiting:
    _large_cycle_time_min: int = None
    _large_cycle_time_max: int = None
    _small_cycle_time_min: int = None
    _small_cycle_time_max: int = None
    _small_cycle_min: int = None
    _small_cycle_max: int = None
    _small_cycle: int = None

    def __reload_small_cycle(cls):
        cls._small_cycle = random.randint(
            cls._small_cycle_min,
            cls._small_cycle_max
        )

    @classmethod
    def set_up(
            cls,
            large_cycle_time_min: int = 30 * 60,
            large_cycle_time_max: int = 60 * 60,
            small_cycle_time_min: int = 10,
            small_cycle_time_max: int = 20,
            small_cycle_min: int = 5,
            small_cycle_max: int = 15
    ):
        """Configure the waiting cycles 配置等待循环
        
        Args:
            large_cycle_time_min: Minimum interval for large cycle 大循环间隔的最小值
            large_cycle_time_max: Maximum interval for large cycle 大循环间隔的最大值
            small_cycle_time_min: Minimum interval for small cycle 小循环间隔的最小值
            small_cycle_time_max: Maximum interval for small cycle 小循环间隔的最大值
            small_cycle_min: Minimum number of small cycles 小循环次数的最小值
            small_cycle_max: Maximum number of small cycles 小循环次数的最大值
        """

        cls._large_cycle_time_min = large_cycle_time_min
        cls._large_cycle_time_max = large_cycle_time_max
        cls._small_cycle_time_min = small_cycle_time_min
        cls._small_cycle_time_max = small_cycle_time_max
        cls._small_cycle_min = small_cycle_min
        cls._small_cycle_max = small_cycle_max
        
        cls.__reload_small_cycle(cls)

    @classmethod
    def normal(
            cls,
            waiting_time: int,
            prompt: str = "Waiting in [n]s"
    ):
        """Output a countdown according to the prompt and wait for the specified time 按照提示词输出倒计时并等待

        Args:
            waiting_time: Countdown duration 倒计时长
            
        Examples:
            1.
            >>> Waiting.normal(3)
            Waiting in 3s
            Waiting in 2s
            Waiting in 1s
            
            2.
            >>> Waiting.normal(3, "[n] 秒后运行")
            3 秒后运行
            2 秒后运行
            1 秒后运行
        """
        
        i = prompt.find("[n]")
        for second in range(waiting_time, 0, -1):
            content = f"{prompt[:i]}{second}{prompt[i + 3:]}"
            print(content, end="\r")
            time.sleep(1)
            print(' ' * len(content), end="\r")

    @classmethod
    def random(cls):
        """Perform a random wait based on the configured cycles 按照提示词输出大小循环的倒计时并等待

        Args:
        
        Examples:
            1. Default configuration 默认配置
            >>> Waiting.random()
            Small cycle remaining 5 rounds waiting in 10s
            . . .
            Small cycle remaining 0 rounds waiting in 0s
            Large cycle waiting in 1800s
            Small cycle remaining 15 rounds waiting in 20s
            . . .
            Small cycle remaining 0 rounds waiting in 0s
            Large cycle waiting in 3600s
            . . . . . .
            
            2. Custom configuration 自定义配置
            >>> Waiting.set_up(
            ...     large_cycle_time_min=5 * 60,
            ...     large_cycle_time_max=10 * 60,
            ...     small_cycle_time_min=1,
            ...     small_cycle_time_max=5,
            ...     small_cycle_min=2,
            ...     small_cycle_max=5
            ... )
            >>> Waiting.random()
            Small cycle remaining 2 rounds waiting in 1s
            . . .
            Small cycle remaining 0 rounds waiting in 0s
            Large cycle waiting in 300s
            Small cycle remaining 2 rounds waiting in 5s
            . . .
            Small cycle remaining 0 rounds waiting in 0s
            Large cycle waiting in 600s
            . . . . . .
        """

        if cls._small_cycle is None:
            cls.set_up()
        
        if cls._small_cycle < 1:
            cls.__reload_small_cycle(cls)
            cls.normal(
                random.randint(cls._large_cycle_time_min, cls._large_cycle_time_max),
                "Large cycle waiting in [n]s"
            )
        
        cls._small_cycle -= 1
        cls.normal(
            random.randint(cls._small_cycle_time_min, cls._small_cycle_time_max),
            f"Small cycle remaining {cls._small_cycle} rounds waiting in [n]s"
        )
      
     