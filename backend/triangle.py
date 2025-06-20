def is_triangle(a, b, c):
    """
    判断三边是否能构成三角形
    三角形任意两边之和大于第三边
    """
    return a + b > c and b + c > a and a + c > b

def triangle_type(a, b, c):
    """
    判断三角形类型
    返回：'一般三角形'、'等腰三角形'、'等边三角形'或'非三角形'
    """
    # 检查输入值是否为正数
    if not (a > 0 and b > 0 and c > 0):
        return '非三角形'
    
    # 首先判断是否为三角形
    if not is_triangle(a, b, c):
        return '非三角形'
    
    # 判断是否为等边三角形
    if a == b == c:
        return '等边三角形'
    
    # 判断是否为等腰三角形
    if a == b or b == c or a == c:
        return '等腰三角形'
    
    # 其他情况为一般三角形
    return '一般三角形'

def main():
    # 测试用例
    test_cases = [
        (3, 4, 5),    # 一般三角形
        (5, 5, 3),    # 等腰三角形
        (4, 4, 4),    # 等边三角形
        (1, 2, 3),    # 非三角形 (两边之和不大于第三边)
        (0, 4, 5),    # 非三角形 (输入值超出范围)
        (101, 100, 99), # 非三角形 (输入值超出范围)
    ]
    
    for a, b, c in test_cases:
        result = triangle_type(a, b, c)
        print(f"边长 {a}, {b}, {c} 的三角形类型是：{result}")

if __name__ == "__main__":
    main() 