# PyCUI

A Python library for managing Controlled Unclassified Information (CUI) categories and their metadata.

## Overview

PyCUI provides easy access to CUI category information, including category codes, names, descriptions, and marking formats. It enables filtering categories by organization and type (basic or special).

## Installation

```bash
pip install pycui
```

## Requirements

- Python 3.9+

## Basic Usage

```python
from pycui-utils import categories, basic_categories, special_categories, organizations

# Access all categories
all_categories = categories.all()

# Get a specific category (Chemical-terrorism Vulnerability Information) marking
privacy_cat = categories.get_by_marking("CVI")

# Get basic (non-specified) categories
basic_cats = basic_categories.all()

# Get special (specified) categories
special_cats = special_categories.all()

# Get all organization codes
org_codes = organizations.all()

# Get categories for a specific organization
dhs_cats = organizations.categories("Nuclear")
```
