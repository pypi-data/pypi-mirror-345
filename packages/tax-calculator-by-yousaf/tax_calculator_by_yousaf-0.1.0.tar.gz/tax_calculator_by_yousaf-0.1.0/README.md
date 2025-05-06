# Indian Tax Calculator FY 2025-26

A simple calculator to compute income tax for India based on old and new regimes for Financial Year 2025-26.

## Features

- Calculate tax based on either monthly or yearly salary inputs
- Support for both old and new tax regimes
- Considers standard deduction, PF, LTA, HRA, and other components
- Calculate in-hand salary after tax deductions
- Easy-to-use command-line interface

## Installation

You can install the package directly from PyPI:

```bash
pip install tax_calculator_by_yousaf
```

Alternatively, you can install directly from GitHub:

```bash
pip install git+https://github.com/yousafkhamza/tax_calculator_by_yousaf.git
```

## Usage

After installation, you can run the calculator directly from the command line:

```bash
tax-calculator
```

Or you can use it in your Python code:

```python
from tax_calculator import calculate_tax_2025_26

calculate_tax_2025_26()
```

## Tax Calculation Details

### New Regime (Default)

- Standard Deduction: ₹75,000
- Tax Slabs:
  - Up to ₹3,00,000: No tax
  - ₹3,00,001 to ₹6,00,000: 5%
  - ₹6,00,001 to ₹9,00,000: 10%
  - ₹9,00,001 to ₹12,00,000: 15%
  - ₹12,00,001 to ₹15,00,000: 20%
  - Above ₹15,00,000: 30%
- Section 87A rebate up to ₹60,000 for income up to ₹12,00,000

### Old Regime

- Standard Deduction: ₹50,000
- Tax Slabs:
  - Up to ₹2,50,000: No tax
  - ₹2,50,001 to ₹5,00,000: 5%
  - ₹5,00,001 to ₹10,00,000: 20%
  - Above ₹10,00,000: 30%
- Section 87A rebate for income up to ₹5,00,000

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Yousaf Khamza
