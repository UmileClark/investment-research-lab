"""Accounting identities, forecast chronology and decision-evidence controls."""
import copy, math, unittest
from datetime import date,timedelta
import numpy as np
from investment_lab.analytics import nw_ols, target_at, policy_simulation
from investment_lab.stress import combined_return, run as stress_run
from investment_lab.currency import minimum_variance_ratio
from investment_lab.drawdowns import episodes, bootstrap_drawdowns
from investment_lab.varchecks import forecasts, kupiec
from investment_lab.optionhedges import price, payoff
from investment_lab.decisionlog import append, validate


class ResearchControls(unittest.TestCase):
    def test_joint_fx_shock_compounds(self):
        self.assertAlmostEqual(combined_return(-.2,.1),-.12)

    def test_stress_position_impacts_reconcile(self):
        r=stress_run()['tables']
        for scenario in r['scenarios']:
            self.assertAlmostEqual(sum(p['pnl_eur'] for p in r['position_impacts'] if p['scenario']==scenario['scenario']),scenario['pnl_eur'])

    def test_minimum_variance_ratio_recovers_known_hedge(self):
        x=np.linspace(-1,1,100)
        self.assertAlmostEqual(minimum_variance_ratio(.7*x+.03,x),.7)

    def test_hac_fit_recovers_exact_linear_relation(self):
        rng=np.random.default_rng(1);x=rng.normal(size=(200,2));y=.01+x@np.array([.4,-.3])
        b,se,r2,resid=nw_ols(y,x)
        np.testing.assert_allclose(b,[.01,.4,-.3],atol=1e-12)
        self.assertAlmostEqual(r2,1);self.assertLess(max(se),1e-10)

    def test_signals_cannot_see_later_prices(self):
        p=np.column_stack([np.linspace(100,150,350),np.linspace(100,90,350)])
        q=p.copy();q[300:]*=10;base=np.array([.5,.4])
        for mode in ['trend','volcontrol']:
            np.testing.assert_array_equal(target_at(p,299,base,mode),target_at(q,299,base,mode))

    def test_trend_exit_and_vol_leverage_cap(self):
        p=np.column_stack([np.linspace(100,110,300),np.linspace(100,90,300)])
        base=np.array([.5,.4])
        np.testing.assert_array_equal(target_at(p,299,base,'trend'),[.5,0])
        self.assertTrue(np.all(target_at(p,299,base,'volcontrol')<=base))

    def test_strategy_cash_fee_identity_and_delayed_fills(self):
        dates=[(date(2023,1,1)+timedelta(days=i)).isoformat() for i in range(700) if (date(2023,1,1)+timedelta(days=i)).weekday()<5]
        p=np.full((len(dates),2),100.)
        r=policy_simulation(dates,p,np.array([.5,.4]),np.array([.0025,.0025]),'baseline')
        self.assertAlmostEqual(r['history'][-1]['nav'],100000-r['fees_eur'],places=7)
        for t in r['trades']:self.assertLess(t['signal_date'],t['fill_date'])

    def test_strategy_future_mutation_preserves_history(self):
        dates=[(date(2023,1,1)+timedelta(days=i)).isoformat() for i in range(700) if (date(2023,1,1)+timedelta(days=i)).weekday()<5]
        p=np.column_stack([np.linspace(100,130,len(dates)),np.linspace(100,80,len(dates))]);q=p.copy();q[-1]*=2
        for mode in ['trend','volcontrol']:
            args=(np.array([.5,.4]),np.array([.0025,.0025]),mode)
            a=policy_simulation(dates,p,*args);b=policy_simulation(dates,q,*args)
            self.assertEqual(a['history'][:-1],b['history'][:-1])

    def test_drawdown_recovery_and_open_episode(self):
        e=episodes(['a','b','c','d','e'],[100,80,100,110,99])
        self.assertAlmostEqual(e[0]['depth'],-.2);self.assertEqual(e[0]['recovery_date'],'c')
        self.assertFalse(e[1]['recovered']);self.assertIsNone(e[1]['recovery_date'])

    def test_bootstrap_flat_path_has_no_drawdown(self):
        np.testing.assert_array_equal(bootstrap_drawdowns(np.zeros(30),5,runs=20),np.zeros(20))

    def test_var_forecasts_only_use_prior_returns(self):
        r=np.random.default_rng(2).normal(0,.01,500);q=r.copy();q[400:]=-.4
        a=forecasts(r);b=forecasts(q)
        for x,y in zip(a,b):
            if x['index']<=400:
                for key in ['historical_var1','historical_var5','ewma_var1','ewma_var5']:self.assertEqual(x[key],y[key])

    def test_coverage_boundaries_are_finite(self):
        for count in [0,5,500]:
            lr,p=kupiec(count,500,.01);self.assertTrue(math.isfinite(lr));self.assertTrue(0<=p<=1)
        self.assertAlmostEqual(kupiec(5,500,.01)[0],0)

    def test_correlation_stress_remains_psd(self):
        r=np.random.default_rng(3).normal(size=(40,5));corr=np.corrcoef(r,rowvar=False)
        self.assertGreaterEqual(np.linalg.eigvalsh(.5*corr+.5*np.ones_like(corr)).min(),-1e-12)

    def test_put_call_parity(self):
        for vol in [.15,.25,.4]:
            self.assertAlmostEqual(price(100,90,.25,.03,vol,'call')-price(100,90,.25,.03,vol,'put'),100-90*math.exp(-.03*.25))

    def test_collar_floor_and_cap(self):
        put=price(100,90,.25,.03,.25);call=price(100,110,.25,.03,.25,'call')
        self.assertAlmostEqual(payoff(0,put,call,'collar'),payoff(89,put,call,'collar'))
        self.assertAlmostEqual(payoff(111,put,call,'collar'),payoff(300,put,call,'collar'))


class DecisionEvidence(unittest.TestCase):
    def setUp(self):
        self.forecast=dict(id='example',kind='forecast',created_at='2026-10-03T12:00:00Z',information_cutoff='2026-10-03T11:00:00Z',deadline='2026-11-01T00:00:00Z',probability=.6,event='Synthetic event',resolution_rule='Explicit criterion',source_url='https://example.com',alternative='Do nothing',invalidation='Contrary evidence')

    def test_hash_tampering_detected(self):
        rows=append([],self.forecast);validate(rows);rows[0]['probability']=.8
        with self.assertRaises(ValueError):validate(rows)

    def test_invalid_probability_future_source_and_past_deadline_rejected(self):
        for update in [dict(probability=1.1),dict(probability=float('nan')),dict(information_cutoff='2027-01-01T00:00:00Z'),dict(deadline='2020-01-01T00:00:00Z')]:
            with self.assertRaises(ValueError):append([],{**self.forecast,**update})

    def test_resolution_must_follow_deadline_and_cannot_repeat(self):
        rows=append([],self.forecast)
        resolution=dict(id='resolution',kind='resolution',forecast_id='example',created_at='2026-11-02T00:00:00Z',outcome=1,evidence_url='https://example.com/result')
        with self.assertRaises(ValueError):append(rows,{**resolution,'created_at':'2026-10-04T00:00:00Z'})
        rows=append(rows,resolution)
        with self.assertRaises(ValueError):append(rows,{**resolution,'id':'duplicate'})


if __name__=='__main__':unittest.main()
