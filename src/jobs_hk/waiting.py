import random
import time


class Waiting:
    """等待相关的类"""
    
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
        """配置
        
        Args:
            large_cycle_time_min (int): 大循环间隔的最小值
            large_cycle_time_max (int): 大循环间隔的最大值
            small_cycle_time_min (int): 小循环间隔的最小值
            small_cycle_time_max (int): 小循环间隔的最大值
            small_cycle_min (int): 小循环次数的最小值
            small_cycle_max (int): 小循环次数的最大值
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
            prompt: str = "等待 [n] 秒"
    ):
        """按照提示词输出倒计时并等待

        Args:
            waiting_time (int): 倒计时长
            prompt (str): 提示词
            
        Examples:
            1.
            >>> Waiting.normal(3)
            等待 3 秒
            等待 2 秒
            等待 1 秒
            
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
        """按照提示词输出大小循环的倒计时并等待

        Args:
        
        Examples:
            1. 默认
            >>> Waiting.random()
            小循环 剩余 5 轮 等待 10 秒
            . . .
            小循环 剩余 0 轮 等待 0 秒
            大循环 等待 1800 秒
            小循环 剩余 15 轮 等待 20 秒
            . . .
            小循环 剩余 0 轮 等待 0 秒
            大循环 等待 3600 秒
            . . . . . .
            
            2. 使用配置
            >>> Waiting.set_up(
            ...     large_cycle_time_min=5 * 60,
            ...     large_cycle_time_max=10 * 60,
            ...     small_cycle_time_min=1,
            ...     small_cycle_time_max=5,
            ...     small_cycle_min=2,
            ...     small_cycle_max=5
            ... )
            >>> Waiting.random()
            小循环 剩余 2 轮 等待 1 秒
            . . .
            小循环 剩余 0 轮 等待 0 秒
            大循环 等待 300 秒
            小循环 剩余 2 轮 等待 5 秒
            . . .
            小循环 剩余 0 轮 等待 0 秒
            大循环 等待 600 秒
            . . . . . .
        """

        if cls._small_cycle is None:
            cls.set_up()
        
        if cls._small_cycle < 1:
            cls.__reload_small_cycle(cls)
            cls.normal(
                random.randint(cls._large_cycle_time_min, cls._large_cycle_time_max),
                "大循环 等待 [n] 秒"
            )
        
        cls._small_cycle -= 1
        cls.normal(
            random.randint(cls._small_cycle_time_min, cls._small_cycle_time_max),
            f"小循环 剩余 {cls._small_cycle} 轮 等待 [n] 秒"
        )
      
     