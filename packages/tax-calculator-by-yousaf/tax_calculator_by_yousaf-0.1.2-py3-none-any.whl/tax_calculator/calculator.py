"""
Tax Calculator for FY 2025-26
A simple calculator to compute income tax for India based on old and new regimes.
"""

def calculate_tax_2025_26():
    """
    Main function to run the tax calculator interactively.
    Provides detailed breakdown of tax calculation for FY 2025-26.
    """
    print("\n===== Salary & Tax Calculator for FY 2025-26 =====\n")

    # Input Mode
    mode_choice = input("1 - Monthly\n2 - Yearly\nEnter your choice: ").strip()
    bonus = get_float_input("\nEnter Annual Bonus / Variable Pay (one-time): ")

    if mode_choice == "1":
        # Monthly inputs
        basic = get_float_input("Enter monthly Basic salary: ")
        hra = get_float_input("Enter monthly HRA: ")
        special_allowance = get_float_input("Enter monthly Special Allowance: ")
        lta = get_float_input("Enter monthly LTA: ")
        pf = get_float_input("Enter monthly PF Contribution: ")
        prof_tax = get_float_input("Enter monthly Professional Tax: ")
        lwf = get_float_input("Enter monthly Labor Welfare Fund: ")

        monthly_gross = basic + hra + special_allowance + lta
        monthly_deductions = pf + prof_tax + lwf

        gross_annual = (12 * monthly_gross) + bonus
        deductions_annual = 12 * monthly_deductions
        annual_lta = 12 * lta
    elif mode_choice == "2":
        # Annual inputs
        basic = get_float_input("Enter annual Basic salary: ")
        hra = get_float_input("Enter annual HRA: ")
        special_allowance = get_float_input("Enter annual Special Allowance: ")
        lta = get_float_input("Enter annual LTA: ")
        pf = get_float_input("Enter annual PF Contribution: ")

        gross_annual = basic + hra + special_allowance + lta + bonus
        deductions_annual = pf
        annual_lta = lta
    else:
        print("Invalid input. Please enter 1 or 2.")
        return

    # Regime selection
    regime = input("\nChoose tax regime (old/new): ").strip().lower()
    if not regime:
        regime = "new"

    standard_deduction = 50000 if regime == "old" else 75000

    # Gross info
    print(f"\nGross Annual Income (incl. Bonus): ₹{gross_annual:,.2f}")
    print(f"Annual Deductions (excl. Tax): ₹{deductions_annual:,.2f}")

    if regime == "old":
        taxable_income = gross_annual - standard_deduction - deductions_annual - annual_lta
        taxable_income = max(0, taxable_income)
        print(f"Taxable Income (Old Regime): ₹{taxable_income:,.2f}")
        tax = calculate_old_regime_tax(taxable_income)
    else:
        taxable_income = gross_annual - standard_deduction
        taxable_income = max(0, taxable_income)
        print(f"Taxable Income (New Regime): ₹{taxable_income:,.2f}")
        tax = calculate_new_regime_tax(taxable_income)

    monthly_tax = round(tax / 12, 2)

    if mode_choice == "1":
        in_hand_monthly = round(monthly_gross - monthly_deductions - monthly_tax, 2)
        print(f"\n👉 Monthly Tax Deduction (TDS): ₹{monthly_tax:,.2f}")
        print(f"💸 In-hand Monthly Salary: ₹{in_hand_monthly:,.2f}")
    else:
        in_hand_annual = round(gross_annual - deductions_annual - tax, 2)
        in_hand_monthly = round(in_hand_annual / 12, 2)
        print(f"\n👉 Total Tax Payable (Annual): ₹{tax:,.2f}")
        print(f"👉 Monthly Tax Deduction (TDS): ₹{monthly_tax:,.2f}")
        print(f"💸 In-hand Annual Salary: ₹{in_hand_annual:,.2f}")
        print(f"💸 In-hand Monthly Salary: ₹{in_hand_monthly:,.2f}")


def get_float_input(prompt):
    """
    Helper function to get float input from user.
    """
    user_input = input(prompt).strip()
    if user_input == "" or user_input == "0":
        return 0.0
    return float(user_input.replace(",", ""))


def calculate_old_regime_tax(income):
    """
    Calculate tax under the old regime.
    """
    tax = 0
    if income <= 250000:
        tax = 0
    elif income <= 500000:
        tax = (income - 250000) * 0.05
    elif income <= 1000000:
        tax = 12500 + (income - 500000) * 0.2
    else:
        tax = 12500 + 100000 + (income - 1000000) * 0.3

    # Section 87A rebate (₹12,500) for income <= ₹5L
    if income <= 500000:
        tax = 0

    return round(tax + tax * 0.04, 2)  # 4% cess


def calculate_new_regime_tax(income):
    """
    Calculate tax under the new regime.
    """
    slabs = [
        (300000, 0.0),
        (600000, 0.05),
        (900000, 0.10),
        (1200000, 0.15),
        (1500000, 0.20),
        (float("inf"), 0.30)
    ]

    tax = 0
    prev_limit = 0
    for limit, rate in slabs:
        if income > limit:
            tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax += (income - prev_limit) * rate
            break

    # Section 87A rebate up to ₹60,000 for income <= ₹12L
    if income <= 1200000:
        tax = max(0, tax - 60000)

    return round(tax + tax * 0.04, 2)  # 4% cess


def main():
    """
    Entry point for the command-line script.
    Handles exceptions gracefully and provides user-friendly error messages.
    """
    try:
        calculate_tax_2025_26()
    except KeyboardInterrupt:
        print("\nTax calculation canceled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()