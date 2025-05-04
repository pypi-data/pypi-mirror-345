# -*- coding: utf-8 -*-
import logging
import unittest

from nectar import Hive, Steem
from nectar.account import Account
from nectar.instance import set_shared_steem_instance
from nectar.nodelist import NodeList

log = logging.getLogger()


class Testcases(unittest.TestCase):
    def test_stm1stm2(self):
        nodelist = NodeList()
        nodelist.update_nodes(steem_instance=Hive(node=nodelist.get_hive_nodes(), num_retries=10))
        b1 = Steem(node="https://api.steemit.com", nobroadcast=True, num_retries=10)
        node_list = nodelist.get_hive_nodes()

        b2 = Hive(node=node_list, nobroadcast=True, num_retries=10)

        self.assertNotEqual(b1.rpc.url, b2.rpc.url)

    def test_default_connection(self):
        nodelist = NodeList()
        nodelist.update_nodes(steem_instance=Hive(node=nodelist.get_hive_nodes(), num_retries=10))

        b2 = Hive(
            node=nodelist.get_hive_nodes(),
            nobroadcast=True,
        )
        set_shared_steem_instance(b2)
        bts = Account("nectar")
        self.assertEqual(bts.blockchain.prefix, "STM")
