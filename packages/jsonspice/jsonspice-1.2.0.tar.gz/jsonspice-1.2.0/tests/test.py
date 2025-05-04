import jsonspice  # import this one first to monkeypatch spiceypy
import spiceypy

def test_jsonspice():
    """
    Test the jsonspice module.
    """

    # not there:
    # v = spiceypy.gdpool('hello', 0, 10)

    # spiceypy.furnsh('de-403-masses.tpc.txt')
    spiceypy.furnsh('de-403-masses.tpc')
    v = spiceypy.gdpool('BODY1_GM', 0, 1)
    assert v[0] == 22032.080, f"Expected 22032.080, got {v[0]}"

    inp = [1,2,3]
    spiceypy.furnsh({"abc": inp})
    v = spiceypy.gdpool('abc', 0, 10)
    print(v)
    assert all(x==y for x,y in zip(v,inp)), f"Expected {inp}, got {v}"

    inp2 = [4,5,6]
    inp.extend(inp2)
    spiceypy.furnsh({"+abc": inp2})
    v = spiceypy.gdpool('abc', 0, 10)
    print(v)
    assert all(x==y for x,y in zip(v,inp)), f"Expected {inp}, got {v}"

    res = -8.83656e+08
    spiceypy.furnsh({"time": '@1972-JAN-1'})
    v = spiceypy.gdpool('time', 0, 10)
    print(v)
    assert v[0] == res, f"Expected {res}, got {v[0]}"

    res = [-8.836560e+08, -8.835696e+08]
    spiceypy.furnsh({"+time": '@1972-JAN-2'})
    v = spiceypy.gdpool('time', 0, 10)
    print(v)
    assert all(x==y for x,y in zip(v,res)), f"Expected {res}, got {v}"

    spiceypy.furnsh('test.json')
    v = spiceypy.gdpool('VARIABLE2', 0, 10)
    print(v)
    assert v[0] == 42.0, f"Expected 42.0, got {v[0]}"

    # an example of an invalid @ string, that just returns a string:
    spiceypy.furnsh({"time2": '@SYNTAX-ERROR'})
    v = spiceypy.gcpool('time2', 0, 10)
    print(v)
    assert v[0] == '@SYNTAX-ERROR', f"Expected '@SYNTAX-ERROR', got {v[0]}"

    # a meta kernel:
    spiceypy.furnsh('meta.json')
    v = spiceypy.gdpool('VAR1', 0, 1)
    print(v)
    assert v[0] == 1.0, f"Expected '1', got {v[0]}"
    v = spiceypy.gdpool('VAR2', 0, 1)
    print(v)
    assert v[0] == 2.0, f"Expected '2', got {v[0]}"
    v = spiceypy.gdpool('HELLO', 0, 1)
    print(v)
    assert v[0] == 1.0, f"Expected '1', got {v[0]}"

