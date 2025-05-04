from __future__ import print_function

import logging

from steem import Steem as steemSteem
from steem.account import Account as steemAccount
from steem.post import Post as steemPost

from nectar import Steem
from nectar.account import Account

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    stm = Steem("https://api.steemit.com")
    nectar_acc = Account("thecrazygm", steem_instance=stm)
    stm2 = steemSteem(nodes=["https://api.steemit.com"])
    steem_acc = steemAccount("thecrazygm", steemd_instance=stm2)

    # profile
    print("nectar_acc.profile  {}".format(nectar_acc.profile))
    print("steem_acc.profile {}".format(steem_acc.profile))
    # sp
    print("nectar_acc.sp  {}".format(nectar_acc.sp))
    print("steem_acc.sp {}".format(steem_acc.sp))
    # rep
    print("nectar_acc.rep  {}".format(nectar_acc.rep))
    print("steem_acc.rep {}".format(steem_acc.rep))
    # balances
    print("nectar_acc.balances  {}".format(nectar_acc.balances))
    print("steem_acc.balances {}".format(steem_acc.balances))
    # get_balances()
    print("nectar_acc.get_balances()  {}".format(nectar_acc.get_balances()))
    print("steem_acc.get_balances() {}".format(steem_acc.get_balances()))
    # reputation()
    print("nectar_acc.get_reputation()  {}".format(nectar_acc.get_reputation()))
    print("steem_acc.reputation() {}".format(steem_acc.reputation()))
    # voting_power()
    print("nectar_acc.get_voting_power()  {}".format(nectar_acc.get_voting_power()))
    print("steem_acc.voting_power() {}".format(steem_acc.voting_power()))
    # get_followers()
    print("nectar_acc.get_followers()  {}".format(nectar_acc.get_followers()))
    print("steem_acc.get_followers() {}".format(steem_acc.get_followers()))
    # get_following()
    print("nectar_acc.get_following()  {}".format(nectar_acc.get_following()))
    print("steem_acc.get_following() {}".format(steem_acc.get_following()))
    # has_voted()
    print(
        "nectar_acc.has_voted()  {}".format(
            nectar_acc.has_voted("@thecrazygm/api-methods-list-for-appbase")
        )
    )
    print(
        "steem_acc.has_voted() {}".format(
            steem_acc.has_voted(steemPost("@thecrazygm/api-methods-list-for-appbase"))
        )
    )
    # curation_stats()
    print("nectar_acc.curation_stats()  {}".format(nectar_acc.curation_stats()))
    print("steem_acc.curation_stats() {}".format(steem_acc.curation_stats()))
    # virtual_op_count
    print("nectar_acc.virtual_op_count()  {}".format(nectar_acc.virtual_op_count()))
    print("steem_acc.virtual_op_count() {}".format(steem_acc.virtual_op_count()))
    # get_account_votes
    print("nectar_acc.get_account_votes()  {}".format(nectar_acc.get_account_votes()))
    print("steem_acc.get_account_votes() {}".format(steem_acc.get_account_votes()))
    # get_withdraw_routes
    print("nectar_acc.get_withdraw_routes()  {}".format(nectar_acc.get_withdraw_routes()))
    print("steem_acc.get_withdraw_routes() {}".format(steem_acc.get_withdraw_routes()))
    # get_conversion_requests
    print("nectar_acc.get_conversion_requests()  {}".format(nectar_acc.get_conversion_requests()))
    print("steem_acc.get_conversion_requests() {}".format(steem_acc.get_conversion_requests()))
    # export
    # history
    nectar_hist = []
    for h in nectar_acc.history(only_ops=["transfer"]):
        nectar_hist.append(h)
        if len(nectar_hist) >= 10:
            break
    steem_hist = []
    for h in steem_acc.history(filter_by="transfer", start=0):
        steem_hist.append(h)
        if len(steem_hist) >= 10:
            break
    print("nectar_acc.history()  {}".format(nectar_hist))
    print("steem_acc.history() {}".format(steem_hist))
    # history_reverse
    nectar_hist = []
    for h in nectar_acc.history_reverse(only_ops=["transfer"]):
        nectar_hist.append(h)
        if len(nectar_hist) >= 10:
            break
    steem_hist = []
    for h in steem_acc.history_reverse(filter_by="transfer"):
        steem_hist.append(h)
        if len(steem_hist) >= 10:
            break
    print("nectar_acc.history_reverse()  {}".format(nectar_hist))
    print("steem_acc.history_reverse() {}".format(steem_hist))
