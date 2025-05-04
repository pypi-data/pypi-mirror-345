# -*- coding: utf-8 -*-
import unittest

from parameterized import parameterized

from nectar import Hive, Steem
from nectar.account import Account
from nectar.amount import Amount
from nectar.block import Block
from nectar.blockchain import Blockchain
from nectar.comment import Comment
from nectar.instance import set_shared_config, set_shared_steem_instance, shared_steem_instance
from nectar.market import Market
from nectar.price import Price
from nectar.transactionbuilder import TransactionBuilder
from nectar.vote import Vote
from nectar.wallet import Wallet
from nectar.witness import Witness
from nectarapi.exceptions import RPCConnection

from .nodes import get_hive_nodes

# Py3 compatibility

core_unit = "STM"


class Testcases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stm = Hive(node=get_hive_nodes())
        stm.config.refreshBackup()
        stm.set_default_nodes(["xyz"])
        del stm

        cls.urls = get_hive_nodes()
        cls.bts = Hive(node=cls.urls, nobroadcast=True, num_retries=10)
        set_shared_steem_instance(cls.bts)
        acc = Account("fullnodeupdate", steem_instance=cls.bts)
        comment = Comment(acc.get_blog_entries(limit=5)[1], steem_instance=cls.bts)
        cls.authorperm = comment.authorperm
        votes = comment.get_votes(raw_data=True)
        last_vote = votes[-1]
        cls.authorpermvoter = comment["authorperm"] + "|" + last_vote["voter"]

    @classmethod
    def tearDownClass(cls):
        stm = Hive(node=get_hive_nodes())
        stm.config.recover_with_latest_backup()

    @parameterized.expand([("instance"), ("steem")])
    def test_account(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            acc = Account("test")
            self.assertIn(acc.blockchain.rpc.url, self.urls)
            self.assertIn(acc["balance"].blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Account(
                    "test",
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1),
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            acc = Account("test", steem_instance=stm)
            self.assertIn(acc.blockchain.rpc.url, self.urls)
            self.assertIn(acc["balance"].blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Account("test")

    @parameterized.expand([("instance"), ("steem")])
    def test_amount(self, node_param):
        if node_param == "instance":
            stm = Steem(node="https://abc.d", autoconnect=False, num_retries=1)
            set_shared_steem_instance(self.bts)
            o = Amount("1 %s" % self.bts.backed_token_symbol)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Amount("1 %s" % self.bts.backed_token_symbol, steem_instance=stm)
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Amount("1 %s" % self.bts.backed_token_symbol, steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Amount("1 %s" % self.bts.backed_token_symbol)

    @parameterized.expand([("instance"), ("steem")])
    def test_block(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Block(1)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Block(
                    1, steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1)
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Block(1, steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Block(1)

    @parameterized.expand([("instance"), ("steem")])
    def test_blockchain(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Blockchain()
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Blockchain(
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1)
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Blockchain(steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Blockchain()

    @parameterized.expand([("instance"), ("steem")])
    def test_comment(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Comment(self.authorperm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Comment(
                    self.authorperm,
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1),
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Comment(self.authorperm, steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Comment(self.authorperm)

    @parameterized.expand([("instance"), ("steem")])
    def test_market(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Market()
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Market(steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1))
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Market(steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Market()

    @parameterized.expand([("instance"), ("steem")])
    def test_price(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Price(10.0, "%s/%s" % (self.bts.token_symbol, self.bts.backed_token_symbol))
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Price(
                    10.0,
                    "%s/%s" % (self.bts.token_symbol, self.bts.backed_token_symbol),
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1),
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Price(
                10.0,
                "%s/%s" % (self.bts.token_symbol, self.bts.backed_token_symbol),
                steem_instance=stm,
            )
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Price(10.0, "%s/%s" % (self.bts.token_symbol, self.bts.backed_token_symbol))

    @parameterized.expand([("instance"), ("steem")])
    def test_vote(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Vote(self.authorpermvoter)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Vote(
                    self.authorpermvoter,
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1),
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Vote(self.authorpermvoter, steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Vote(self.authorpermvoter)

    @parameterized.expand([("instance"), ("steem")])
    def test_wallet(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Wallet()
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                o = Wallet(
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1)
                )
                o.blockchain.get_config()
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Wallet(steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                o = Wallet()
                o.blockchain.get_config()

    @parameterized.expand([("instance"), ("steem")])
    def test_witness(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Witness("gtg")
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Witness(
                    "gtg",
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1),
                )
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = Witness("gtg", steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                Witness("gtg")

    @parameterized.expand([("instance"), ("steem")])
    def test_transactionbuilder(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = TransactionBuilder()
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                o = TransactionBuilder(
                    steem_instance=Steem(node="https://abc.d", autoconnect=False, num_retries=1)
                )
                o.blockchain.get_config()
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = TransactionBuilder(steem_instance=stm)
            self.assertIn(o.blockchain.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                o = TransactionBuilder()
                o.blockchain.get_config()

    @parameterized.expand([("instance"), ("steem")])
    def test_steem(self, node_param):
        if node_param == "instance":
            set_shared_steem_instance(self.bts)
            o = Steem(node=self.urls)
            o.get_config()
            self.assertIn(o.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                stm = Steem(node="https://abc.d", autoconnect=False, num_retries=1)
                stm.get_config()
        else:
            set_shared_steem_instance(Steem(node="https://abc.d", autoconnect=False, num_retries=1))
            stm = self.bts
            o = stm
            o.get_config()
            self.assertIn(o.rpc.url, self.urls)
            with self.assertRaises(RPCConnection):
                stm = shared_steem_instance()
                stm.get_config()

    def test_config(self):
        set_shared_config({"node": self.urls})
        set_shared_steem_instance(None)
        o = shared_steem_instance()
        self.assertIn(o.rpc.url, self.urls)
