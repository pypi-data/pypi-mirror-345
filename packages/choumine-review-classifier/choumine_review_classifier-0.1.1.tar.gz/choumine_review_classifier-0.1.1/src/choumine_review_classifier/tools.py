# tools.py
from .common import app


@app.tool()
async def choumine_add(a: int = 2, b: int = 3) -> int:
    """
    执行两个整数的加法运算
    
    参数:
        a (int): 第一个加数
        b (int): 第二个加数
    
    返回:
        int: 两个参数的和
    """
    return a + b
