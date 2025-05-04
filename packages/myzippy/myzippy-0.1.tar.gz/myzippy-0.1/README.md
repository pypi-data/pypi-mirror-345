# myzippy

A highly scientific and definitely serious package to measure your zipp size.

## Installation

```bash
pip install myzippy
```

## Usage

```python
import myzippy

myzippy.length.num(6)
print("your zipp is", myzippy.length.text())
```

### Output
```
your zipp is short
```

## Zipp Levels

| Length | Description        |
|--------|--------------------|
| ≤ 0    | you don't have a zipp |
| ≤ 3    | too short          |
| < 7    | short              |
| ≤ 10   | medium             |
| ≤ 15   | good               |
| ≤ 20   | perfect            |
| > 20   | tall               |
