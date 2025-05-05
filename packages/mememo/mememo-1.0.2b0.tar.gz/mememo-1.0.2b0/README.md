# mememo

![PyPI version](https://img.shields.io/badge/v1.0.2b0-5FC33B)
![Python version](https://img.shields.io/badge/python-2.5+-blue)

 A lighweight package to find the mean, median, and mode.

---

## Benefits

- Most efficient and more lightweight than the `numpy` or `statistics` module.
- No need other 3rd-party modules to install.
- Only 3 functions.
---

## Installation
To import, run

```python
import mememo
```

## `mean()`

You can use the `mean()` function to find the mean of 2+ numbers.

```python
a = mememo.mean([1, 2])
print(a) # Output: 1.5
```

#### Same way applies to the `median()` and `mode()` functions.

```python
a = mememo.median([1, 2])
print(a) # Output: 1.5
```
```python
a = mememo.mode([1, 2])
print(a) # Output: 2
```

## Cruical note: The function must only take in one argument which is the list of numbers.

For example,
```python
mememo.mean(10, 15, 87)
```
will raise this error
```python
TypeError: mean() takes 1 positional argument but 2 were given
```