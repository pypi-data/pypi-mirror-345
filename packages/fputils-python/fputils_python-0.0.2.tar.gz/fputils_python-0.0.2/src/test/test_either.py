from fputils.either import Left, Right


def test_is_left():
    left = Left("error")
    assert left.is_left() is True
    assert left.is_right() is False


def test_is_right():
    right = Right(10)
    assert right.is_left() is False
    assert right.is_right() is True


def test_contains():
    assert Right(5).contains(5) is True
    assert Right(5).contains(6) is False
    assert Left("error").contains("error") is False


def test_exists():
    assert Right(10).exists(lambda x: x > 5) is True
    assert Right(3).exists(lambda x: x > 5) is False
    assert Left("err").exists(lambda x: True) is False


def test_filter_or_else():
    left = Left("e")
    assert left.filter_or_else(lambda x: True, "other") is left
    r_fail = Right(2).filter_or_else(lambda x: x > 3, "other")
    assert isinstance(r_fail, Left) and r_fail._value == "other"
    r_ok = Right(5).filter_or_else(lambda x: x > 3, "other")
    assert isinstance(r_ok, Right) and r_ok._value == 5


def test_flatmap():
    left = Left("err").flatmap(lambda x: Right(x))
    assert isinstance(left, Left) and left._value == "err"
    r = Right(4).flatmap(lambda x: Right(x * 2))
    assert isinstance(r, Right) and r._value == 8


def test_flatten():
    nested = Right(Right(7))
    result = nested.flatten()
    assert isinstance(result, Right) and result._value == 7
    assert Right(Right(Right(7))).flatten().flatten()._value == 7
    assert Right(Left(Right(7))).flatten().flatten().is_left() is True


def test_fold():
    left = Left("e")
    right = Right(3)
    assert left.fold(lambda x: f"left:{x}", lambda x: f"right:{x}") == "left:e"
    assert right.fold(lambda x: f"left:{x}", lambda x: f"right:{x}") == "right:3"


def test_forall():
    assert Left("e").forall(lambda x: False) is True
    assert Left("e").forall(lambda x: True) is True
    assert Right(5).forall(lambda x: x > 3) is True
    assert Right(2).forall(lambda x: x > 3) is False


def test_foreach():
    result = []
    Left("e").foreach(lambda x: result.append(x))
    assert result == []
    Right(9).foreach(lambda x: result.append(x))
    assert result == [9]


def test_get_or_else():
    assert Right(5).get_or_else(0) == 5
    assert Left("err").get_or_else(0) == 0


def test_map():
    left = Left("e").map(lambda x: "f")
    assert isinstance(left, Left) and left._value == "e"
    r = Right(3).map(lambda x: x + 1)
    assert isinstance(r, Right) and r._value == 4


def test_or_else():
    other = Right(100)
    right = Right(1).or_else(other)
    assert isinstance(right, Right) and right._value == 1
    left = Left("e").or_else(other)
    assert left is other


def test_swap():
    s_left = Right(5).swap()
    assert isinstance(s_left, Left) and s_left._value == 5
    s_right = Left("e").swap()
    assert isinstance(s_right, Right) and s_right._value == "e"


def test_to_list():
    assert Left("e").to_list() == []
    assert Right(8).to_list() == [8]
