import pytest
from fracted import tools

@pytest.mark.parametrize(("f1", "f2", "args", "kwargs"), [
    (lambda x: x * 2, lambda x: x + 5, (2,), {}),
    (lambda x, y: x * y, lambda x: "He" + x + "o!", ("l", 5), {}),
    (lambda x=1, y=2, z=3: x + y + z, lambda x=1, y=2: x * y, (4,), {"z": 5})
])
def test_func_composion(f1, f2, args, kwargs):
    """Tests if composed funcs gives same output as f2(f1(x))."""
    output = f2(f1(*args, **kwargs))

    assert tools.compose_funcs(f1, f2)(*args, **kwargs) == output
    
    @tools.append_func_after(f2)
    def f(*args, **kwargs):
        return f1(*args, **kwargs)
    assert f(*args, **kwargs) == output

    @tools.append_func_before(f1)
    def f(*args, **kwargs):
        return f2(*args, **kwargs)
    assert f(*args, **kwargs) == output
