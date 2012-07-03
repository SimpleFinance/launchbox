import unittest

from launchbox.versions import matches_version_constraint as mvc
from launchbox.versions import high_to_low, pad_to_3
from launchbox.versions import version_to_components, components_to_version
from launchbox.versions import highest_version_match as hvm

def v(ver):
    return [int(c) for c in ver.split('.')]

class TestVersionContraints(unittest.TestCase):
    def test_matches_version_contraint_equals(self):
        self.assertTrue(mvc('=', v('1.0'), v('1.0.0')))
        self.assertTrue(mvc('=', v('1.0.0'), v('1.0.0')))
        self.assertFalse(mvc('=', v('1.1'), v('1.0.0')))

    def test_matches_version_contraint_greater_than(self):
        self.assertTrue(mvc('>', v('1.0'), v('1.1')))
        self.assertTrue(mvc('>', v('1.0.0'), v('2')))
        self.assertFalse(mvc('>', v('1.0'), v('1.0.0')))

    def test_matches_version_contraint_greater_or_equal(self):
        self.assertTrue(mvc('>=', v('1.0'), v('1.1')))
        self.assertTrue(mvc('>=', v('1.0.0'), v('1.0.0')))
        self.assertFalse(mvc('>=', v('2.0'), v('1.9.9')))

    def test_matches_version_contraint_less_than(self):
        self.assertTrue(mvc('<', v('2.0'), v('1.1')))
        self.assertTrue(mvc('<', v('2.0.0'), v('1.9.9')))
        self.assertFalse(mvc('<', v('2.0'), v('2.0.0')))

    def test_matches_version_contraint_less_or_equal(self):
        self.assertTrue(mvc('<=', v('2.0'), v('1.1')))
        self.assertTrue(mvc('<=', v('2.0.0'), v('1.9.9')))
        self.assertFalse(mvc('<=', v('2.0'), v('2.0.1')))

    def test_matches_version_contraint_approximately_equal(self):
        self.assertTrue(mvc('~>', v('2.0.0'), v('2.0.1')))
        self.assertTrue(mvc('~>', v('2.0.0'), v('2.0.0')))
        self.assertFalse(mvc('~>', v('2.0.0'), v('2.1.0')))

        self.assertTrue(mvc('~>', v('2.0'), v('2.0.1')))
        self.assertTrue(mvc('~>', v('2.0'), v('2.9')))
        self.assertFalse(mvc('~>', v('2.0'), v('3.0')))

    def test_highest_version_match(self):
        self.assertEqual('2.0', hvm('> 1.0', ['0.1', '0.9', '1.0', '1.1', '2.0']))
        self.assertEqual('1.0', hvm('= 1.0', ['0.1', '0.9', '1.0', '1.1', '2.0']))
        self.assertEqual('1.1', hvm('~> 1.0', ['0.1', '0.9', '1.0', '1.1', '2.0']))

class TestAuxiliaryFunctions(unittest.TestCase):
    def test_high_to_low(self):
        self.assertEqual([([3, 0, 0], '3.0'),
                          ([2, 1, 0], '2.1.0'),
                          ([2, 0, 0], '2')],
                         high_to_low(['2', '3.0', '2.1.0']))

    def test_pad_to_3(self):
        self.assertEqual([3, 0, 0], pad_to_3([3]))
        self.assertEqual([2, 1, 0], pad_to_3([2, 1]))
        self.assertEqual([1, 2, 3], pad_to_3([1, 2, 3]))

    def test_version_to_components(self):
        self.assertEqual([1, 2, 3], version_to_components('1.2.3'))

    def test_components_to_version(self):
        self.assertEqual('1.2.3', components_to_version([1, 2, 3]))
