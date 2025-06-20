# -*- coding: utf-8 -*-

# 定义计费系统中的常量
BASE_RENT = 25.0
RATE_PER_MINUTE = 0.15

def calculate_telecom_fee(call_minutes, late_payments):
    """
    根据通话时长和欠费次数计算电信费用。

    Args:
        call_minutes (int): 当月通话总分钟数。
        late_payments (int): 本年度至本月的累计未按时缴费次数。

    Returns:
        dict: 包含计算状态和详细费用的字典。
    """
    # 1. 验证输入值的有效性
    if not isinstance(call_minutes, int) or not isinstance(late_payments, int):
        return {'status': 'error', 'message': '非法输入：通话分钟和缴费次数必须为整数。'}
    if call_minutes < 0 or late_payments < 0:
        return {'status': 'error', 'message': '非法输入：通话分钟和缴费次数不能为负数。'}

    # 2. 根据通话时长确定折扣率和允许的欠费次数
    discount_rate = 0.0
    allowed_late_payments = 0

    if 0 < call_minutes <= 60:
        allowed_late_payments = 1
        discount_rate = 0.01
    elif 60 < call_minutes <= 120:
        allowed_late_payments = 2
        discount_rate = 0.015
    elif 120 < call_minutes <= 180:
        allowed_late_payments = 3
        discount_rate = 0.02
    elif 180 < call_minutes <= 300:
        allowed_late_payments = 3
        discount_rate = 0.025
    elif call_minutes > 300:
        allowed_late_payments = 6
        discount_rate = 0.03
    # 如果 call_minutes 为 0, discount_rate 保持 0.0, 逻辑正确

    # 3. 检查实际欠费次数是否超过允许值，若超过则取消折扣
    final_discount_rate = discount_rate
    if late_payments > allowed_late_payments:
        final_discount_rate = 0.0

    # 4. 计算各项费用
    raw_call_fee = call_minutes * RATE_PER_MINUTE
    discount_amount = raw_call_fee * final_discount_rate
    final_call_fee = raw_call_fee - discount_amount
    total_fee = BASE_RENT + final_call_fee

    return {
        'status': 'success',
        'call_minutes': call_minutes,
        'late_payments': late_payments,
        'base_rent': BASE_RENT,
        'raw_call_fee': round(raw_call_fee, 2),
        'applied_discount_rate': final_discount_rate,
        'final_call_fee': round(final_call_fee, 2),
        'total_fee': round(total_fee, 2),
        'message': '计算成功'
    }

# --- 用于直接运行文件时的测试用例 ---
if __name__ == '__main__':
    print("--- 电信收费计算模块测试 ---")

    # 示例1: 享受折扣
    # 50分钟通话, 1次欠费. 属于第一档(允许1次), 享受1.0%折扣
    print(f"输入 (分钟:50, 欠费:1) -> {calculate_telecom_fee(50, 1)}")
    # 预期: raw_call_fee=7.5, final_call_fee=7.42, total_fee=32.42

    # 示例2: 因欠费过多而失去折扣
    # 50分钟通话, 2次欠费. 属于第一档(允许1次), 失去折扣
    print(f"输入 (分钟:50, 欠费:2) -> {calculate_telecom_fee(50, 2)}")
    # 预期: raw_call_fee=7.5, final_call_fee=7.5, total_fee=32.5

    # 示例3: 第三档, 享受折扣
    # 150分钟通话, 3次欠费. 属于第三档(允许3次), 享受2.0%折扣
    print(f"输入 (分钟:150, 欠费:3) -> {calculate_telecom_fee(150, 3)}")
    # 预期: raw_call_fee=22.5, final_call_fee=22.05, total_fee=47.05
    
    # 示例4: 第五档, 因欠费过多失去折扣
    # 400分钟通话, 7次欠费. 属于第五档(允许6次), 失去折扣
    print(f"输入 (分钟:400, 欠费:7) -> {calculate_telecom_fee(400, 7)}")
    # 预期: raw_call_fee=60, final_call_fee=60, total_fee=85.0

    # 示例5: 0分钟通话
    print(f"输入 (分钟:0, 欠费:0) -> {calculate_telecom_fee(0, 0)}")
    # 预期: total_fee=25.0

    # 示例6: 非法输入
    print(f"输入 (分钟:-10, 欠费:0) -> {calculate_telecom_fee(-10, 0)}") 