def calculate_employee_score(sales, work_hours, leaves, level):
    """
    根据给定的公式计算员工的考评等级分数。

    公式:
    Score = clamp(
        Base(sales)
      + (hours ≥ 20 ? 1 : 0)
      - (leaves ≥ 15 ? 2 : leaves ≥ 10 ? 1 : 0)
      + (level = 1  ? 1 : 0)
    , 1, 5)

    Base(sales):
    1 if sales < 200
    2 if 200 ≤ sales < 300
    3 if 300 ≤ sales < 400
    4 if 400 ≤ sales < 500
    5 if sales ≥ 500

    Args:
        sales (float or int): 年度销售总额。
        work_hours (float or int): 工作时长（单位由业务定义，可能是年/月/小时等）。
        leaves (int): 请假天数。
        level (int): 员工级别。

    Returns:
        int: 最终考评得分 (范围在1-5分)。
    """

    # 1. 计算 Base(sales)
    if sales < 200:
        base_score = 1
    elif 200 <= sales < 300:
        base_score = 2
    elif 300 <= sales < 400:
        base_score = 3
    elif 400 <= sales < 500:
        base_score = 4
    else:  # sales >= 500
        base_score = 5

    # 2. 计算工时奖励 (hours ≥ 20 ? 1 : 0)
    hours_bonus = 1 if work_hours >= 20 else 0

    # 3. 计算请假惩罚 (leaves ≥ 15 ? 2 : leaves ≥ 10 ? 1 : 0)
    if leaves >= 15:
        leaves_penalty = 2
    elif leaves >= 10:
        leaves_penalty = 1
    else:
        leaves_penalty = 0

    # 4. 计算级别奖励 (level = 1 ? 1 : 0)
    level_bonus = 1 if level == 1 else 0

    # 5. 计算原始总分
    raw_score = base_score + hours_bonus - leaves_penalty + level_bonus

    # 6. 使用 clamp 函数将分数限制在 [1, 5] 区间
    final_score = max(1, min(raw_score, 5))

    return final_score
