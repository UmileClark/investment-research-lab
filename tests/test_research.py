"""Financial identities, input integrity and temporal invariance checks."""
import unittest
import numpy as np
from investment_lab.math import (bond_price,bond_greeks,equity_dcf,reverse_dcf,carry_pnl,
                                 carry_break_even,price_fx_attribution,covariance,risk_contributions)
from investment_lab.data import Market,verify_inputs
from investment_lab.rebalancing import simulate
from investment_lab.accounting import audit
from investment_lab.commodities import convergence_return
from investment_lab.rates import curve_price


class FinancialIdentities(unittest.TestCase):
    def test_bond_par_and_discount_direction(self):
        self.assertAlmostEqual(bond_price(.04,.04,8),100,places=10)
        self.assertLess(bond_price(.04,.05,8),100)
        self.assertGreater(bond_price(.04,.03,8),100)

    def test_zero_coupon_duration(self):
        self.assertAlmostEqual(bond_greeks(0,.04,8)["duration"],8/1.02,places=5)

    def test_spot_curve_flat_matches_ytm(self):
        self.assertAlmostEqual(curve_price(8,.04,[1,2,5,10,30],[.05]*5),bond_price(.04,.05,8),places=10)

    def test_carry_forward_parity(self):
        t=.25;target=.0435;fund=.0025
        forward=(1+fund*t)/(1+target*t)
        self.assertAlmostEqual(carry_pnl(target,fund,t,forward-1),0,places=12)

    def test_carry_break_even_after_costs(self):
        spot=carry_break_even(.105,.0025,.25,.001)
        self.assertAlmostEqual(carry_pnl(.105,.0025,.25,spot,.001),0,places=12)
        self.assertLess(carry_pnl(.105,.0025,.25,-.10,.001),0)

    def test_price_fx_identity_with_interaction(self):
        local,fx=price_fx_attribution(10,100,110,.9,.8)
        self.assertAlmostEqual(local,90)
        self.assertAlmostEqual(fx,-110)
        self.assertAlmostEqual(local+fx,-20)

    def test_reverse_valuation_recovers_growth(self):
        value,_=equity_dcf(9,.11,.09,.03)
        self.assertAlmostEqual(reverse_dcf(9,value,.09,.03),.11,places=9)

    def test_invalid_terminal_value_rejected(self):
        with self.assertRaises(ValueError):equity_dcf(9,.08,.03,.03)

    def test_covariance_psd_and_euler_identity(self):
        rng=np.random.default_rng(42);r=rng.normal(0,.01,(250,5));w=np.array([.3,.2,.2,.1,.1])
        for target in ["constant_correlation","diagonal"]:
            for lam in [0,.25,1]:
                cov=covariance(r,lam,target);vol,share=risk_contributions(w,cov)
                self.assertGreater(np.linalg.eigvalsh(cov).min(),0)
                self.assertAlmostEqual(sum(share),1)
                vol2,share2=risk_contributions(w*2,cov)
                self.assertAlmostEqual(vol2,vol*2)
                np.testing.assert_allclose(share,share2)

    def test_flat_futures_curve_convergence(self):
        self.assertAlmostEqual(convergence_return(100,100,collateral=0,fee=0),0)
        self.assertLess(convergence_return(100,102,collateral=0,fee=0),0)
        self.assertGreater(convergence_return(100,98,collateral=0,fee=0),0)


class TemporalAndAccountingChecks(unittest.TestCase):
    def test_hashes_and_frozen_ledger(self):
        verify_inputs();r=audit()
        self.assertLess(r["max_daily_nav_error_eur"],1e-6)
        self.assertTrue(r["pending_excluded"])

    def test_no_future_or_stale_quotes(self):
        archive={"A":{"rows":[{"date":"2024-01-01","close":100,"adjusted":100},
                               {"date":"2024-01-10","close":900,"adjusted":900}]}}
        self.assertEqual(Market.row(archive,"A","2024-01-04")["close"],100)
        with self.assertRaises(ValueError):Market.row(archive,"A","2024-01-09")
        with self.assertRaises(ValueError):Market.row(archive,"A","2023-12-31")

    def test_new_future_prices_do_not_rewrite_earlier_actions(self):
        dates=["2024-09-30","2024-10-01","2024-10-30","2024-10-31","2024-11-01","2024-11-04"]
        p=np.array([[100,100],[101,99],[115,90],[120,85],[110,91],[112,89]],dtype=float)
        w=np.array([.5,.4]);cost=np.array([.0025,.0025])
        for mode in ["buy_hold","monthly","drift"]:
            original=simulate(dates,p,w,cost,mode)
            revised=p.copy();revised[-1]=[900,10]
            future=simulate(dates,revised,w,cost,mode)
            self.assertEqual(original["history"][:-1],future["history"][:-1])
            self.assertEqual(original["trades"],future["trades"])
            shorter=simulate(dates[:-1],p[:-1],w,cost,mode)
            self.assertEqual(original["history"][:-1],shorter["history"])
            for t in original["trades"]:self.assertLess(t["decision_date"],t["fill_date"])

    def test_fee_accounting_at_constant_prices(self):
        dates=["2024-09-30","2024-10-01","2024-10-31","2024-11-01"]
        p=np.full((4,2),100.);r=simulate(dates,p,np.array([.5,.4]),np.array([.0025,.0025]),"monthly")
        self.assertAlmostEqual(r["nav"],100000-r["fees"],places=8)

    def test_training_cutoff_and_archive_bridge(self):
        m=Market();dates,p=m.training()
        self.assertLessEqual(max(dates),"2024-09-27")
        for s in m.symbols:
            a=m.row(m.combined,s,"2024-09-27",exact=True)["adjusted"]
            b=m.row(m.post,s,"2024-09-27",exact=True)["adjusted"]
            self.assertEqual(a,b)


if __name__=="__main__":unittest.main()
