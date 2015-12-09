from django.test import TestCase

import unittest
import fixtures

class TestBasic(unittest.TestCase):

    def setUp(self):
        self.cos = fixtures.company_fixtures()
        self.users = fixtures.appuser_fixtures()
        self.roles = fixtures.approle_fixtures()

    def tearDown(self):
        del self.cos
        del self.users
        del self.roles

    def test_companies(self):
        """Companies"""
        # print "Companies %s" % self.cos
        assert self.cos == ['Affiliated Physicians(channel)', 
                            'City of Cedar Rapids(employer)', 
                            'HSI-Rx(channel)', 
                            'Vertex Pharmaceuticals(employer)', 
                            'ZPH Admin(admin_co)'
        ]

    def test_users(self):
        """Users"""
        # print "Users %s" % self.users
        assert 'heather' in self.users and 'j.singh*' in self.users

    def test_positive_permissions(self):
        """Permissions +"""
        assert fixtures.validate_permission('j.singh', 'Affiliated Physicians', ['phii'])

    def test_negative_permissions(self):
        """Permissions -"""
        assert not fixtures.validate_permission('heather', 'Vertex Pharmaceuticals', ['hmtx'])
