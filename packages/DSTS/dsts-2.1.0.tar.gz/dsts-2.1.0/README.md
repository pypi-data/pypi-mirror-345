# Doubly Structured Data Synthesis for Time-series Energy Use Data

This repository contains the official Python package implementation of the "Doubly Structured Data Synthesis for Time-series Energy Use Data" 

## Installation
To install the package, you can use `pip`. Run the following command in your terminal:

```bash
pip install DSTS
```

## How to use
Here is a simple example to get you started with the DSTS package.

### Importing the Package

```bash
from DSTS import dsts
import pandas as pd
import numpy as np
```

### Loading Your Dataset
```bash
data = ...
```

### 1. Use GMM(n_comp=2) and sorting method
```bash
model = dsts(data)
synth = model.generate(aug=5, n_comp=2, sort=True)
```
Note that aug parameter is the multiplier for the size of the synthesized data relative to the original data.

### 2. Use conditional GMM(n_comp=2)
```bash
model = dsts(data)
synth = model.generate(aug=5, n_comp=2, sort=False, condGMM=True)
```

### 3. Use linear regression
```bash
model = dsts(data)
synth = model.generate(aug=5, n_comp=2, sort=False, LR=True)
```