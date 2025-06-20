# -*- coding: utf-8 -*-

# 定义产品单价和月度销售上限常量
HOST_PRICE = 25
MONITOR_PRICE = 30
PERIPHERAL_PRICE = 45

MAX_HOSTS_PER_MONTH = 70
MAX_MONITORS_PER_MONTH = 80
MAX_PERIPHERALS_PER_MONTH = 90

def calculate_sales_and_commission(hosts_sold, monitors_sold, peripherals_sold):
    """
    根据销量计算总销售额和佣金。

    Args:
        hosts_sold (int): 售出的主机数量。
        monitors_sold (int): 售出的显示器数量。
        peripherals_sold (int): 售出的外设数量。

    Returns:
        dict: 包含计算状态、销售额、佣金和消息的字典。
              成功时: {'status': 'success', 'sales': float, 'commission': float}
              失败时: {'status': 'error', 'message': str}
    """
    # 1. 验证输入是否为非负整数
    if not all(isinstance(val, int) and val >= 0 for val in [hosts_sold, monitors_sold, peripherals_sold]):
        return {
            'status': 'error',
            'sales': 0,
            'commission': 0,
            'message': '非法输入'
        }

    # 2. 验证是否满足每月最低销量要求
    if hosts_sold < 1 or monitors_sold < 1:
        return {
            'status': 'error',
            'sales': 0,
            'commission': 0,
            'message': '非法输入'
        }
        
    # 3. 验证是否超过产品月度销售上限
    if hosts_sold > MAX_HOSTS_PER_MONTH:
        return {
            'status': 'error',
            'sales': 0,
            'commission': 0,
            'message': '非法输入'
        }
    if monitors_sold > MAX_MONITORS_PER_MONTH:
        return {
            'status': 'error',
            'sales': 0,
            'commission': 0,
            'message': '非法输入'
        }
    if peripherals_sold > MAX_PERIPHERALS_PER_MONTH:
        return {
            'status': 'error',
            'sales': 0,
            'commission': 0,
            'message': '非法输入'
        }

    # 4. 计算总销售额
    total_sales = (hosts_sold * HOST_PRICE) + \
                  (monitors_sold * MONITOR_PRICE) + \
                  (peripherals_sold * PERIPHERAL_PRICE)

    # 5. 根据销售额分级计算佣金
    if total_sales <= 1000:
        commission_rate = 0.10
    elif total_sales <= 1800: # 隐含了 total_sales > 1000
        commission_rate = 0.15
    else:  # total_sales > 1800
        commission_rate = 0.20
    
    commission = total_sales * commission_rate

    return {
        'status': 'success',
        'sales': total_sales,
        'commission': round(commission, 2),
        'message': '计算成功'
    }
