from fputils.option import Some, Empty
import pytest


def test_some():
    some_value = Some(42)
    assert some_value.is_defined(), "Expected Some to be defined."
    assert some_value.get() == 42, "Expected Some value to be 42."
    assert not some_value.is_empty(), "Expected Some to not be empty."


def test_empty():
    value = Empty()

    assert not value.is_defined(), "Expected Empty to not be defined."
    assert value.is_empty(), "Expected Empty to be empty."

    with pytest.raises(ValueError):
        value.get()


def test_contains():
    assert Some(42).contains(42), "Expected Some to contain 42."
    assert not Some(42).contains(43), "Expected Some to not contain 43."
    assert not Empty().contains(42), "Expected Empty to not contain 42."
    assert not Empty().contains(None), (
        "Even though Empty represents None, this should be False."
    )


def test_exists():
    assert Some(42).exists(lambda x: x > 0), (
        "Expected Some to exist with a positive value."
    )
    assert not Some(42).exists(lambda x: x < 0), (
        "Expected Some to not exist with a negative value."
    )
    assert not Empty().exists(lambda x: x > 0), (
        "Expected Empty to not exist with any predicate."
    )
    assert not Empty().exists(lambda x: x < 0), (
        "Expected Empty to not exist with any predicate."
    )


def test_filter():
    assert Some(42).filter(lambda x: x > 0).is_defined(), (
        "Expected Some to be defined after filtering with a positive predicate."
    )
    assert Some(42).filter(lambda x: x < 0).is_empty(), (
        "Expected Some to be empty after filtering with a negative predicate."
    )
    assert Empty().filter(lambda x: x > 0).is_empty(), (
        "Expected Empty to remain empty after filtering."
    )
    assert Empty().filter(lambda x: x < 0).is_empty(), (
        "Expected Empty to remain empty after filtering."
    )

    assert Some(42).filter_not(lambda x: x > 0).is_empty(), (
        "Expected Some to be empty after filtering with a negative predicate."
    )
    assert Some(42).filter_not(lambda x: x < 0).is_defined(), (
        "Expected Some to be defined after filtering with a positive predicate."
    )
    assert Empty().filter_not(lambda x: x > 0).is_empty(), (
        "Expected Empty to remain empty after filtering."
    )
    assert Empty().filter_not(lambda x: x < 0).is_empty(), (
        "Expected Empty to remain empty after filtering."
    )


def test_flatmap():
    assert Some(42).flatmap(lambda x: Some(x + 1)).get() == 43, (
        "Expected flatmap to return Some with incremented value."
    )
    assert Some(42).flatmap(lambda x: Empty()).is_empty(), (
        "Expected flatmap to return Empty."
    )
    assert Empty().flatmap(lambda x: Some(x + 1)).is_empty(), (
        "Expected flatmap on Empty to remain Empty."
    )
    assert Empty().flatmap(lambda x: Empty()).is_empty(), (
        "Expected flatmap on Empty to remain Empty."
    )

    assert (
        Some(42).flatmap(lambda x: Empty()).flatmap(lambda x: Some(123)).is_empty()
    ), "Expected flatmap to return Empty."


def test_map():
    assert Some(42).map(lambda x: x + 1).get() == 43, (
        "Expected map to return Some with incremented value."
    )
    assert Empty().map(lambda x: x + 1).is_empty(), (
        "Expected map on Empty to remain Empty."
    )
    assert Some(42).map(lambda x: x + 1).map(lambda x: x + 1).get() == 44, (
        "Expected map to return Some with incremented value."
    )


def test_flatten():
    assert Some(Some(42)).flatten().get() == 42, (
        "Expected flatten to return the inner Some value."
    )
    assert Some(Empty()).flatten().is_empty(), (
        "Expected flatten on Some(Empty) to return Empty."
    )
    assert Empty().flatten().is_empty(), "Expected flatten on Empty to remain Empty."
    assert Some(Some(Empty())).flatten().is_defined(), (
        "Expected flatten to flatten only a single level"
    )

    with pytest.raises(AssertionError):
        Some(42).flatten().get()


def test_fold():
    assert Some(42).fold(lambda x: x + 1, 0) == 43, (
        "Expected fold to return incremented value."
    )
    assert Empty().fold(lambda x: x + 1, 0) == 0, (
        "Expected fold on Empty to return default value."
    )
    assert Some(42).fold(lambda x: x + 1, 100) == 43, (
        "Expected fold to return incremented value."
    )
    assert Empty().fold(lambda x: x + 1, 100) == 100, (
        "Expected fold on Empty to return default value."
    )


def test_forall():
    assert Some(42).forall(lambda x: x > 0), (
        "Expected forall to return True for positive predicate."
    )
    assert not Some(42).forall(lambda x: x < 0), (
        "Expected forall to return False for negative predicate."
    )
    assert Empty().forall(lambda x: x > 0), "Expected forall on Empty to return True."
    assert Empty().forall(lambda x: x < 0), "Expected forall on Empty to return True."


def test_foreach():
    result = []

    def add_to_result(x):
        result.append(x)

    Some(42).foreach(add_to_result)
    assert result == [42], "Expected foreach to add value to result."

    Empty().foreach(add_to_result)
    assert result == [42], "Expected foreach on Empty to not modify result."


def test_get_or_else():
    assert Some(42).get_or_else(0) == 42, "Expected get_or_else to return Some value."
    assert Empty().get_or_else(0) == 0, (
        "Expected get_or_else on Empty to return default value."
    )
    assert Some(42).get_or_else(100) == 42, "Expected get_or_else to return Some value."
    assert Empty().get_or_else(100) == 100, (
        "Expected get_or_else on Empty to return default value."
    )


def test_or_else():
    assert Some(42).or_else(Some(100)).get() == 42, (
        "Expected or_else to return Some value."
    )
    assert Empty().or_else(Some(100)).get() == 100, (
        "Expected or_else on Empty to return alternative value."
    )
    assert Some(42).or_else(Empty()).get() == 42, (
        "Expected or_else to return Some value."
    )
    assert Empty().or_else(Empty()).is_empty(), (
        "Expected or_else on Empty to return Empty."
    )


def test_or_none():
    assert Some(42).or_none() == 42, "Expected or_none to return Some value."
    assert Empty().or_none() is None, "Expected or_none on Empty to return None."
    assert Some(42).or_none() == 42, "Expected or_none to return Some value."
    assert Empty().or_none() is None, "Expected or_none on Empty to return None."


def test_to_left():
    assert Some(42).to_left(100).fold(lambda x: x, lambda x: x) == 42, (
        "Expected to_left to return Left(42)."
    )
    assert Empty().to_left(100).contains(100), (
        "Expected to_left on Empty to return the provided Right(100)."
    )


def test_to_right():
    assert Some(42).to_right(100).contains(42), (
        "Expected to_right to return Right with Some value."
    )
    assert Empty().to_right(100).fold(lambda x: x, lambda x: x) == 100, (
        "Expected to_right on Empty to return Left(100)."
    )


def test_zip():
    assert Some(42).zip(Some(100)).get() == (42, 100), (
        "Expected zip to return a tuple of values."
    )
    assert Empty().zip(Some(100)).is_empty(), "Expected zip on Empty to return Empty."
    assert Some(42).zip(Empty()).is_empty(), "Expected zip on Empty to return Empty."
    assert Empty().zip(Empty()).is_empty(), "Expected zip on Empty to return Empty."


def test_unzip():
    assert Some((42, 100)).unzip() == (Some(42), Some(100)), (
        "Expected unzip to return a tuple of Options."
    )
    assert Empty().unzip() == (Empty(), Empty()), (
        "Expected unzip on Empty to return a tuple of two Empty options."
    )
    assert Some(42).unzip() == (Empty(), Empty()), (
        "Expected unzip on non-tuple to return a tuple of two Empty options."
    )


def test_comparison():
    assert Some(42) == Some(42), "Expected Some(42) to be equal to Some(42)."
    assert Some(42) != Some(100), "Expected Some(42) to not be equal to Some(100)."
    assert Some(42) != Empty(), "Expected Some(42) to not be equal to Empty."
    assert Empty() == Empty(), "Expected Empty to be equal to Empty."
    assert Empty() != Some(100), "Expected Empty to not be equal to Some(100)."
    assert Some(42) != "ABC", "Expected Some(42) to not be equal to a string."
    assert Empty() != "ABCExpected Empty to not be equal to a string."


def test_iterable():
    assert list(Some(42)) == [42], "Expected iterable to return a list with the value."
    assert list(Empty()) == [], "Expected iterable on Empty to return an empty list."
