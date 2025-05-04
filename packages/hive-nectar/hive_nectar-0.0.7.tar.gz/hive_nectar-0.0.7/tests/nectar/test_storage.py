# -*- coding: utf-8 -*-
import unittest

from nectar import Steem
from nectar.instance import set_shared_steem_instance, shared_steem_instance
from nectar.wallet import Wallet

from .nodes import get_steem_nodes

# Py3 compatibility
core_unit = "STM"
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stm = shared_steem_instance()
        stm.config.refreshBackup()

        cls.stm = Steem(
            node=get_steem_nodes(),
            nobroadcast=True,
            # We want to bundle many operations into a single transaction
            bundle=True,
            num_retries=10,
            # Overwrite wallet to use this list of wifs only
        )

        cls.stm.set_default_account("test")
        set_shared_steem_instance(cls.stm)
        # self.stm.newWallet("TestingOneTwoThree")

        cls.wallet = Wallet(steem_instance=cls.stm)
        cls.wallet.wipe(True)
        cls.wallet.newWallet("TestingOneTwoThree")
        cls.wallet.unlock(pwd="TestingOneTwoThree")
        cls.wallet.addPrivateKey(wif)

    @classmethod
    def tearDownClass(cls):
        stm = shared_steem_instance()
        stm.config.recover_with_latest_backup()

    def test_set_default_account(self):
        stm = self.stm
        stm.set_default_account("thecrazygm")

        self.assertEqual(stm.config["default_account"], "thecrazygm")
