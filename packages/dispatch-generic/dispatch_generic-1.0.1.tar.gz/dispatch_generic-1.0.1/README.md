# dispatch-generic

A simple dispatch decorator for generic functions.

`pip install dispatch-generic`

```python
from dispatch import dispatch


@dispatch
def test(i: int):
    print('for int')


@dispatch
def test(s: str):
    print('for str')


test(5)  # for int
test('s')  # for str
test()  # TypeError
```
