# ============================================================
# day17/parallel_tool_call.py - 并行工具调用演示
# 串行 vs 并行！对比时间！
# ============================================================

import time
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# 我们的工具（模拟：每个工具要2秒！）
# ============================================================

def get_weather(city: str) -> str:
    """查询某个城市的天气（模拟耗时2秒！）"""
    time.sleep(2)  # 假装查询要2秒！
    return f"{city}今天晴，25度"


# ============================================================
# 模拟：大模型一次返回了3个工具调用请求！
# ============================================================

tool_calls = [
    {"name": "get_weather", "args": {"city": "北京"}},
    {"name": "get_weather", "args": {"city": "上海"}},
    {"name": "get_weather", "args": {"city": "广州"}},
]


# ============================================================
# 串行执行
# ============================================================

def run_serial():
    results = []
    for tc in tool_calls:
        result = get_weather(tc["args"]["city"])
        results.append(result)
        print(f"  执行{tc['name']}({tc['args']['city']}) → {result}")
    return results


# ============================================================
# 并行执行
# ============================================================

def run_parallel():
    def do_one(tc):
        return get_weather(tc["args"]["city"])
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(do_one, tool_calls))
    for tc, result in zip(tool_calls, results):
        print(f"  执行{tc['name']}({tc['args']['city']}) → {result}")
    return results


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 50)
    print("并行工具调用演示")
    print("=" * 50)
    
    print("模拟：大模型一次返回了3个工具调用请求！")
    for tc in tool_calls:
        print(f"  {tc['name']}({tc['args']['city']})")
    print()
    
    # 1. 串行执行！
    print("【串行执行】一个一个来！")
    start = time.time()
    run_serial()
    serial_time = time.time() - start
    print(f"  串行耗时：{serial_time:.1f}秒")
    print()
    
    # 2. 并行执行！
    print("【并行执行】同时执行！")
    start = time.time()
    run_parallel()
    parallel_time = time.time() - start
    print(f"  并行耗时：{parallel_time:.1f}秒")
    print()
    
    # 3. 对比！
    print("=" * 50)
    print("对比结果：")
    print("=" * 50)
    print(f"  串行：{serial_time:.1f}秒")
    print(f"  并行：{parallel_time:.1f}秒")
    print(f"  省了：{serial_time - parallel_time:.1f}秒！")
    print()
    print("为什么能并行？")
    print("因为3个工具调用互不依赖！查北京天气不需要等上海天气的结果！")
    print()
    print("注意：")
    print("1. 有些模型支持一次返回多个请求（并行）！")
    print("2. 有些模型是串行的（如glm-4-flash）！一轮一个！")
    print("3. 并行执行的前提是：工具之间互不依赖！")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    main()
