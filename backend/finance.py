import pandas as pd

def calculate_repayment(data):
    principal = data.loan_amount
    interest = (data.interest_rate / 100) * principal
    total = principal + interest
    periods = data.months * (4 if data.frequency == "weekly" else 1)
    repayment = round(total / periods, 2)

    schedule = []
    remaining = total
    for i in range(1, periods + 1):
        remaining = round(remaining - repayment, 2)
        schedule.append({"period": i, "repayment": repayment, "remaining_balance": max(remaining, 0)})

    df = pd.DataFrame(schedule)
    return {
        "repayment_per_period": repayment,
        "total_interest": round(interest, 2),
        "schedule": df.to_dict(orient="records"),
        "net_salary": round(data.salary - repayment, 2),
        "frequency": data.frequency,
    }
