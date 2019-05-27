import math

import attr
import numpy as np
import pytest

import pyle.constraintula as constraintula
from pyle.constraintula import Symbol

PI = np.pi


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def circumference(self):
        return self.radius * 2 * PI

    @property
    def area(self):
        return PI * self.radius**2


@attr.attrs(auto_attribs=True)
class Foo:
    x: float
    y: float
    z: float


def test_constraintula():
    C = Symbol('C')  # circumference
    D = Symbol('D')  # diameter
    R = Symbol('R')  # radius
    A = Symbol('A')  # area

    system = constraintula.System({
        D - 2 * R,
        C - PI * D,
        A - 2 * PI * R**2,
    }).with_independent(C)

    circle = Circle(system.evaluate({C: 10})[R])
    assert np.abs(circle.radius - 10 / (2 * PI)) < 0.001


def test_make_factory_for():
    x, y, z = constraintula.symbols('x y z')
    foo_factory = constraintula.make_factory_for(
        Foo,
        [x - y * z],)
    foo = foo_factory(y=2, z=3)
    assert math.isclose(foo.x, 6)


def test_constrain_with_attr():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    @attr.attrs(auto_attribs=True, frozen=True)
    class Bar:
        x: float
        y: float
        z: float

    bar = Bar(x=3, z=9)  # y should be 3
    assert math.isclose(bar.y, 3)
    with pytest.raises(Exception):
        bar.x = 4


def test_constrain_with_vanilla_class():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    class Baz:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    baz = Baz(x=3, z=9)  # pylint: disable=no-value-for-parameter
    assert math.isclose(baz.y, 3)


def test_constrain_with_properties():
    x, y, z = constraintula.symbols('x y z')

    @constraintula.constrain([x * y - z])
    class Milton:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        @property
        def z(self):
            return self.x * self.y

    milton = Milton(x=3, z=9)  # pylint: disable=no-value-for-parameter, unexpected-keyword-arg
    assert math.isclose(milton.y, 3)
    with pytest.raises(Exception):
        milton.z = 4