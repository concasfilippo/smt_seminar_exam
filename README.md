# Counting Game — Exam Implementation Notes

This document explains how the exercise was developed, the key modeling choices, and how to run the solutions.

## Overview

The exercise models the “Counting Game” with Z3. Given 6 numbers and a target goal, the solver must build a sequence of arithmetic operations (+, -, *, /) using each number at most once, to get as close as possible to the goal. Two variants are implemented:

- **CountingStrategy**: standard version, minimizing distance to the goal and (secondarily) the number of used numbers.
- **CountingStrategyResilient**: "adversarial" version, where an attacker replaces the last chosen number with a value from 1..10 to maximize the distance from the goal; the solver minimizes that worst‑case distance.

## Design Choices and Rationale

- **State-based modeling**: each state stores
  - the six initial numbers,
  - a usage counter vector (`used`),
  - the current result (`res`),
  - the number of used numbers (`n_used`).
  This makes constraints explicit and simplifies checking “use at most once.”

- **Programmatic transitions**: transitions are generated with loops over all operand choices and operations, avoiding a massive hand-written `Or(...)` block and keeping the model parametric.

- **Optimization with `Optimize`**:
  - primary objective: minimize `abs(res - goal)`
  - secondary objective: minimize the number of used numbers
  This matches the problem statement: exact solutions are preferred, and among them the shortest one is chosen.

- **Division guards**: division by zero is prevented by explicit constraints.

- **Resilient variant (min–max)**:
  the attacker chooses the worst possible replacement (1..10). The model enumerates the 10 attacks and minimizes the maximum distance. This avoids using quantifiers, which are not reliably supported with `Optimize` (a "WARNING" message would appear).

- **Non‑negative intermediate results**:
  an optional constraint forbids negative intermediate results to keep solutions closer to the intended arithmetic game.


## Requirements

- Python 3.8+
- `z3-solver`

Install:

```bash
pip3 install z3-solver
```

## Usage

Run the extended version (standard + resilient, with timing):

```bash
python3 Exercises/exam_sol.py
```

You can also call the functions directly:

```python
CountingStrategy([1, 3, 5, 8, 10, 50], 462, k=6)
CountingStrategyResilient([1, 3, 5, 8, 10, 50], 462, k=6)
```

## Examples
It was not necessary but I implemented an elapsed time indicator
```
Case: numbers=[3, 5, 6, 8, 9, 10], goal=317
Initial number: 10
Step 1: operation + with number 9 -> result 19
Step 2: operation * with number 6 -> result 114
Step 3: operation + with number 5 -> result 119
Step 4: operation * with number 8 -> result 952
Step 5: operation / with number 3 -> result 317
Final number: 317
Distance from goal: 0
Time: 198.922s
---
Resilient case: numbers=[3, 5, 6, 8, 9, 10], goal=317
Initial number: 5
Step 1: operation * with number 9 -> result 45
Step 2: operation + with number 10 -> result 55
Step 3: operation - with number 3 -> result 52
Step 4: operation * with number 6 -> result 312
Step 5: operation + with number 8 -> result 320
Final number: 320
Distance from goal after attack: 5
Time: 3194.222s
```

## Notes

- `k` counts **states**, so `k = 6` corresponds to 5 operations (maximum when using all 6 numbers).
- For hard instances, you can raise `k` or add bounds on `res` to speed up the solver, but I don't think it's necessary. 


## Other examples

```
Case: numbers=[1, 3, 5, 8, 10, 50], goal=462
Initial number: 5
Step 1: operation - with number 50 -> result 45
Step 2: operation * with number 10 -> result 450
Step 3: operation + with number 3 -> result 453
Step 4: operation + with number 1 -> result 454
Step 5: operation + with number 8 -> result 462
Final number: 462
Distance from goal: 0
Time: 164.278s
---
Case: numbers=[3, 5, 6, 8, 9, 10], goal=317
Initial number: 10
Step 1: operation + with number 9 -> result 19
Step 2: operation * with number 6 -> result 114
Step 3: operation + with number 5 -> result 119
Step 4: operation * with number 8 -> result 952
Step 5: operation / with number 3 -> result 317
Final number: 317
Distance from goal: 0
Time: 198.922s
---
Case: numbers=[2, 4, 7, 9, 25, 50], goal=463
Initial number: 2
Step 1: operation / with number 25 -> result 12
Step 2: operation * with number 50 -> result 600
Step 3: operation - with number 4 -> result 596
Step 4: operation * with number 7 -> result 4172
Step 5: operation / with number 9 -> result 463
Final number: 463
Distance from goal: 0
Time: 326.244s
---
Case: numbers=[1, 6, 8, 12, 25, 75], goal=952
Initial number: 12
Step 1: operation + with number 1 -> result 13
Step 2: operation * with number 75 -> result 975
Step 3: operation - with number 25 -> result 950
Step 4: operation + with number 8 -> result 958
Step 5: operation - with number 6 -> result 952
Final number: 952
Distance from goal: 0
Time: 256.177s
---
Case: numbers=[1, 2, 3, 4, 6, 8], goal=999
Initial number: 3
Step 1: operation + with number 2 -> result 5
Step 2: operation * with number 6 -> result 30
Step 3: operation + with number 1 -> result 31
Step 4: operation * with number 8 -> result 248
Step 5: operation * with number 4 -> result 992
Final number: 992
Distance from goal: 7
Time: 404.837s
---
Case: numbers=[2, 3, 5, 7, 11, 13], goal=997
Initial number: 3
Step 1: operation + with number 2 -> result 5
Step 2: operation + with number 13 -> result 18
Step 3: operation * with number 5 -> result 90
Step 4: operation * with number 11 -> result 990
Step 5: operation + with number 7 -> result 997
Final number: 997
Distance from goal: 0
Time: 177.538s
---
Case: numbers=[1, 4, 6, 7, 8, 9], goal=503
Initial number: 4
Step 1: operation / with number 6 -> result 0
Step 2: operation - with number 7 -> result 7
Step 3: operation * with number 8 -> result 56
Step 4: operation * with number 9 -> result 504
Step 5: operation - with number 1 -> result 503
Final number: 503
Distance from goal: 0
Time: 128.549s
---
Case: numbers=[2, 4, 6, 8, 10, 12], goal=457
Initial number: 8
Step 1: operation * with number 12 -> result 96
Step 2: operation - with number 4 -> result 92
Step 3: operation * with number 10 -> result 920
Step 4: operation - with number 6 -> result 914
Step 5: operation / with number 2 -> result 457
Final number: 457
Distance from goal: 0
Time: 231.459s
---
Resilient case: numbers=[1, 3, 5, 8, 10, 50], goal=462
Initial number: 10
Step 1: operation + with number 50 -> result 60
Step 2: operation - with number 3 -> result 57
Step 3: operation * with number 8 -> result 456
Step 4: operation * with number 1 -> result 456
Step 5: operation + with number 5 -> result 461
Final number: 461
Distance from goal after attack: 5
Time: 233.317s
---
Resilient case: numbers=[3, 5, 6, 8, 9, 10], goal=317
Initial number: 5
Step 1: operation * with number 9 -> result 45
Step 2: operation + with number 10 -> result 55
Step 3: operation - with number 3 -> result 52
Step 4: operation * with number 6 -> result 312
Step 5: operation + with number 8 -> result 320
Final number: 320
Distance from goal after attack: 5
Time: 3194.222s
---
Resilient case: numbers=[2, 4, 7, 9, 25, 50], goal=463
Initial number: 4
Step 1: operation + with number 7 -> result 11
Step 2: operation / with number 25 -> result 0
Step 3: operation - with number 2 -> result 2
Step 4: operation * with number 50 -> result 100
Step 5: operation - with number 9 -> result 91
Final number: 91
Distance from goal after attack: 390
Time: 545.510s
---
Resilient case: numbers=[1, 6, 8, 12, 25, 75], goal=952
Initial number: 12
Step 1: operation + with number 1 -> result 13
Step 2: operation * with number 75 -> result 975
Step 3: operation - with number 25 -> result 950
Step 4: operation + with number 8 -> result 958
Step 5: operation - with number 6 -> result 952
Final number: 952
Distance from goal after attack: 5
Time: 379.947s
---
Resilient case: numbers=[1, 2, 3, 4, 6, 8], goal=999
Initial number: 3
Step 1: operation * with number 4 -> result 12
Step 2: operation + with number 1 -> result 13
Step 3: operation / with number 2 -> result 6
Step 4: operation * with number 8 -> result 48
Step 5: operation - with number 6 -> result 42
Final number: 42
Distance from goal after attack: 961
Time: 100.995s
---
Resilient case: numbers=[2, 3, 5, 7, 11, 13], goal=997
Initial number: 3
Step 1: operation - with number 7 -> result 4
Step 2: operation + with number 13 -> result 17
Step 3: operation - with number 5 -> result 12
Step 4: operation + with number 2 -> result 14
Step 5: operation - with number 11 -> result 3
Final number: 3
Distance from goal after attack: 995
Time: 111.202s
---
Resilient case: numbers=[1, 4, 6, 7, 8, 9], goal=503
Initial number: 1
Step 1: operation - with number 6 -> result 5
Step 2: operation * with number 8 -> result 40
Step 3: operation - with number 4 -> result 36
Step 4: operation - with number 7 -> result 29
Step 5: operation * with number 9 -> result 261
Final number: 261
Distance from goal after attack: 477
Time: 85.042s
---
Resilient case: numbers=[2, 4, 6, 8, 10, 12], goal=457
Initial number: 6
Step 1: operation + with number 2 -> result 8
Step 2: operation / with number 8 -> result 1
Step 3: operation - with number 12 -> result 11
Step 4: operation * with number 10 -> result 110
Step 5: operation + with number 4 -> result 114
Final number: 114
Distance from goal after attack: 436
Time: 130.286s
---
```
