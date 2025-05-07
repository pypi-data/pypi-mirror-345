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

    if mode_choice == "1":
        # Monthly inputs
        basic = get_float_input("\nEnter monthly Basic salary: ")
        hra = get_float_input("Enter monthly HRA: ")
        special_allowance = get_float_input("Enter monthly Special Allowance: ")
        lta = get_float_input("Enter monthly LTA: ")
        pf = get_float_input("Enter monthly PF Contribution: ")
        prof_tax = get_float_input("Enter monthly Professional Tax: ")
        lwf = get_float_input("Enter monthly Labor Welfare Fund: ")
        additional_incentives = get_float_input("Enter monthly Additional Incentives/Allowances (total): ")

        monthly_gross = basic + hra + special_allowance + lta + additional_incentives
        monthly_deductions = pf + prof_tax + lwf

        # No bonus in monthly mode
        gross_annual = (12 * monthly_gross)
        deductions_annual = 12 * monthly_deductions
        annual_lta = 12 * lta
    elif mode_choice == "2":
        # Annual inputs
        bonus = get_float_input("\nEnter Annual Bonus / Variable Pay (one-time): ")
        basic = get_float_input("Enter annual Basic salary: ")
        hra = get_float_input("Enter annual HRA: ")
        special_allowance = get_float_input("Enter annual Special Allowance: ")
        lta = get_float_input("Enter annual LTA: ")
        pf = get_float_input("Enter annual PF Contribution: ")
        # No prof_tax or lwf in yearly mode

        gross_annual = basic + hra + special_allowance + lta + bonus
        deductions_annual = pf
        annual_lta = lta
    else:
        print("Invalid input. Please enter 1 or 2.")
        return

    # Additional tax-saving deductions for old regime
    if regime := input("\nChoose tax regime (old/new): ").strip().lower() or "new":
        if regime == "old":
            print("\n--- Additional deductions (applicable only for old regime) ---")
            medical_insurance = get_float_input("Enter Medical Insurance Premium (80D): ")
            education_loan = get_float_input("Enter Education Loan Interest (80E): ")
            investment_80c = get_float_input("Enter Investment Deductions (80C): ")
            
            additional_deductions = medical_insurance + education_loan + investment_80c
        else:
            additional_deductions = 0
    else:
        regime = "new"
        additional_deductions = 0

    # Standard deduction amount depends on regime
    standard_deduction = 50000 if regime == "old" else 75000

    # Gross info
    print(f"\nGross Annual Income (incl. Bonus): ₹{gross_annual:,.2f}")
    print(f"Annual Deductions (excl. Tax): ₹{deductions_annual:,.2f}")
    
    if regime == "old":
        if additional_deductions > 0:
            print(f"Additional Tax Saving Deductions: ₹{additional_deductions:,.2f}")
        
        taxable_income = gross_annual - standard_deduction - deductions_annual - annual_lta - additional_deductions
        taxable_income = max(0, taxable_income)
        print(f"Taxable Income (Old Regime): ₹{taxable_income:,.2f}")
        tax = calculate_old_regime_tax(taxable_income)
    else:
        taxable_income = gross_annual - standard_deduction - deductions_annual
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
    Calculate tax under the old regime for FY 2025-26.
    """
    # Old regime tax slabs remain unchanged
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
        tax = max(0, tax - 12500)

    return round(tax + tax * 0.04, 2)  # 4% cess


def calculate_new_regime_tax(income):
    """
    Calculate tax under the new regime for FY 2025-26.
    """
    # Updated new regime tax slabs for FY 2025-26
    tax = 0
    
    if income <= 400000:
        tax = 0
    elif income <= 800000:
        tax = (income - 400000) * 0.05
    elif income <= 1200000:
        tax = 20000 + (income - 800000) * 0.10
    elif income <= 1600000:
        tax = 20000 + 40000 + (income - 1200000) * 0.15
    elif income <= 2000000:
        tax = 20000 + 40000 + 60000 + (income - 1600000) * 0.20
    elif income <= 2400000:
        tax = 20000 + 40000 + 60000 + 80000 + (income - 2000000) * 0.25
    else:
        tax = 20000 + 40000 + 60000 + 80000 + 100000 + (income - 2400000) * 0.30

    # Section 87A rebate up to ₹60,000 for income <= ₹12L
    if income <= 1200000:
        tax = max(0, tax - 60000)

    return round(tax + tax * 0.04, 2)  # 4% cess


def calculate_surcharge(income, tax):
    """
    Calculate surcharge based on income level.
    """
    if income > 5000000:  # > 5 crore
        surcharge_rate = 0.25 if regime == "new" else 0.37
        return tax * surcharge_rate
    elif income > 2000000:  # > 2 crore
        return tax * 0.25
    elif income > 1000000:  # > 1 crore
        return tax * 0.15
    elif income > 500000:   # > 50 lakh
        return tax * 0.10
    else:
        return 0


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