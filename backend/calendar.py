def is_leap(year):
    """
    判断指定的年份是否为闰年。
    - 能被4整除但不能被100整除。
    - 或者能被400整除。
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def calculate_next_day(year, month, day):
    """
    计算给定日期的下一天。
    - 年份范围: 1800-2200
    - 月份范围: 1-12
    - 日期范围: 根据月份和是否闰年动态判断
    """
    # 输入类型校验
    if not all(isinstance(arg, int) for arg in [year, month, day]):
        return "无效日期"
    
    # 年月范围校验
    if not 1800 <= year <= 2200:
        return "无效日期"
    if not 1 <= month <= 12:
        return "无效日期"
        
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    if is_leap(year):
        days_in_month[2] = 29
        
    # 日期范围校验
    if not 1 <= day <= days_in_month[month]:
        return "无效日期"
        
    # 计算下一天
    if day < days_in_month[month]:
        next_day = day + 1
        next_month = month
        next_year = year
    else:  # 月末
        next_day = 1
        if month < 12:
            next_month = month + 1
            next_year = year
        else:  # 年末
            next_month = 1
            next_year = year + 1

    # 检查计算后的日期是否超出范围
    if next_year > 2200:
        return "无效日期"
        
    return f"{next_year}.{next_month}.{next_day}" 