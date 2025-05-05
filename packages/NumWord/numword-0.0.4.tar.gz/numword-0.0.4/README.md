# NumWord

![Manual Test](https://github.com/HarshitDalal/numword/actions/workflows/manual_test.yml/badge.svg)
![Daily Test](https://github.com/HarshitDalal/numword/actions/workflows/daily_test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/NumWord)
![PyPI Downloads](https://img.shields.io/pypi/dm/NumWord)
![License MIT](https://img.shields.io/github/license/HarshitDalal/numword)
![codecov](https://codecov.io/gh/HarshitDalal/NumWord/graph/badge.svg?token=3DAOLLEYO3)

**NumWord** is a Python package that converts numbers written in words to their numeric representation and vice versa.

---

## Features

- Convert words to numbers (supports decimals and large values).
- Convert numbers to words.
- Language support:
  - English (`en`)
  - Hindi (`hi`)
  - French (`fr`)
- Convert numbers to humanized formats:
  - `1500000` → `1.5M`
  - `1.5M` → `10L` / `10 लाख`
- Convert currencies from one to another (using live exchange rates).

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

### 🔢 Convert word to number

```python
from NumWord import WordToNumber

word_to_num_converter = WordToNumber()

# English
print(word_to_num_converter.convert("one hundred twenty three point four five six"))
# Output: 123.456

# Hindi
print(word_to_num_converter.convert("एक सौ तेईस दशमलव चार पांच छह", lang='hi'))
# Output: 123.456

# French
print(word_to_num_converter.convert("cent vingt-trois virgule quatre cinq six", lang="fr"))
# Output: 123.456
```

---

### 🗣️ Convert number to word

```python
from NumWord import NumberToWord

num_to_word_converter = NumberToWord()

# English
print(num_to_word_converter.convert(123.456))
# Output: one hundred twenty-three point four five six

# Hindi
print(num_to_word_converter.convert(123.456, lang='hi'))
# Output: एक सौ तेईस दशमलव चार पांच छह

# French
print(num_to_word_converter.convert(123.456, lang='fr'))
# Output: cent vingt-trois virgule quatre cinq six
```

---

### 📏 Convert to/from humanized number formats

```python
from NumWord import HumanizeNumber

humanize_number = HumanizeNumber()

# Convert to humanized format in English
print(humanize_number.convert(1500000, lang='en'))
# Output: 1.5M

# Convert to Hindi format
print(humanize_number.convert("1.5M", lang="en", to_lang="hi"))
# Output: 15 लाख

# Convert to shorthand Indian format
print(humanize_number.convert("1.5M", lang="en", to_lang="en-hi"))
# Output: 15L
```

---

### 💱 Currency conversion

```python
from NumWord import Currency

currency = Currency()

# Convert USD to EUR
print(currency.convert(100, "USD", "EUR", with_symbol=False))
# Output: 88.37 EUR 

# Convert EUR to INR with currency symbol
print(currency.convert(50, "EUR", "INR", with_symbol=True))
# Output: ₹ 4781.83

# Note: Currency exchange rates update once per day
```

---

## 🧪 Running Tests

```bash
python -m unittest discover tests
```

---

## 📄 License

This project is licensed under the MIT License – see the `LICENSE` file for details.