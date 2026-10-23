import sqlite3
import unittest
from gamedatalab.analytics import database, retention, ltv, churn_rows, experiment, experiment_from_db, auc
from gamedatalab.synthetic import generate


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.users = [('a','2026-09-01','search','control'),
                      ('b','2026-09-30','organic','treatment')]
        self.events = [('1','a','2026-09-01','session',0),
                       ('2','a','2026-09-02','session',0),
                       ('3','a','2026-09-02','session',0),
                       ('4','a','2026-09-07','session',0),
                       ('5','a','2026-09-08','session',0),
                       ('6','a','2026-09-01','purchase',1000),
                       ('7','a','2026-09-02','refund',-200)]
        self.costs = [('a',200),('b',0)]

    def db(self, events=None):
        c = database(self.users, self.events if events is None else events, self.costs)
        self.addCleanup(c.close)
        return c

    def test_retention_deduplicates_active_users_and_censors(self):
        rows = retention(self.db(),'2026-09-30')
        d = {(r['install_date'],r['day_n']): r for r in rows}
        self.assertEqual(d[('2026-09-01',1)]['retained'],1)
        self.assertEqual(d[('2026-09-01',7)]['retention'],1.0)
        self.assertIsNone(d[('2026-09-01',30)]['retention'])
        self.assertIsNone(d[('2026-09-30',1)]['retained'])

    def test_ltv_refunds_zero_cost_and_mature_denominator(self):
        rows = ltv(self.db(),'2026-10-01')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['receipts_usd'],8.0)
        self.assertAlmostEqual(rows[0]['contribution_roas'],2.8)
        self.assertEqual(rows[0]['installs'],1)
        self.assertIsNone(ltv(self.db(),'2026-11-01')[0]['contribution_roas'])

    def test_retry_is_idempotent_conflict_is_rejected(self):
        con = self.db(self.events+[self.events[0]])
        self.assertEqual(con.execute('SELECT COUNT(*) FROM events').fetchone()[0],len(self.events))
        with self.assertRaises(ValueError):
            self.db(self.events+[('1','a','2026-09-01','purchase',50)])

    def test_schema_rejects_invalid_ledger(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db([('bad','a','2026-09-01','purchase',-100)])
        with self.assertRaises(ValueError):
            self.db([('bad','a','2026-08-01','session',0)])

    def test_churn_boundary_and_feature_leakage(self):
        rows = churn_rows(self.db(),'2026-09-30')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['active_days_7'],3)
        self.assertEqual(rows[0]['churned'],0)
        # A future D14 event cannot alter features or the D7..13 label.
        extra = self.events+[('future','a','2026-09-15','session',0)]
        self.assertEqual(rows,churn_rows(self.db(extra),'2026-09-30'))
        self.assertEqual(churn_rows(self.db(),'2026-09-13'),[])

    def test_experiment_srm_and_lift(self):
        self.assertAlmostEqual(experiment(1000,500,1000,600)['absolute_lift'],0.1)
        self.assertEqual(experiment(1000,500,1000,500)['p_value'],1.0)
        self.assertFalse(experiment(1000,500,100,50)['valid_allocation'])
        for args in [(0,0,10,5),(10,11,10,5),(10,0,10,5),(1.2,1,10,5)]:
            with self.assertRaises(ValueError):
                experiment(*args)

    def test_auc_ties_and_single_class(self):
        self.assertEqual(auc([0,1],[0.1,0.9]),1.0)
        self.assertEqual(auc([0,1],[0.9,0.1]),0.0)
        self.assertEqual(auc([0,1],[0.5,0.5]),0.5)
        self.assertIsNone(auc([1,1],[0.1,0.9]))

    def test_generation_reproducible(self):
        self.assertEqual(generate(100,7),generate(100,7))
        self.assertNotEqual(generate(100,7),generate(100,8))

    def test_future_events_do_not_change_retention_cutoff(self):
        extra = self.events+[('future','a','2026-10-01','session',0)]
        self.assertEqual(retention(self.db(),'2026-09-30'),retention(self.db(extra),'2026-09-30'))

    def test_cost_coverage_and_bad_dates_rejected(self):
        with self.assertRaises(ValueError):
            database(self.users,self.events,[('a',200)])
        with self.assertRaises(ValueError):
            self.db([('bad','a','not-a-date','session',0)])

    def test_itt_includes_non_completers_and_deduplicates_success(self):
        users = [(str(i),'2026-09-01','organic','control' if i<20 else 'treatment') for i in range(40)]
        events = [(f'{i}-done',str(i),'2026-09-01','tutorial_complete',0) for i in list(range(10))+list(range(20,30))]
        events += [('another','0','2026-09-01','tutorial_complete',0)]
        con = database(users,events,[(str(i),0) for i in range(40)])
        self.addCleanup(con.close)
        result = experiment_from_db(con,'2026-09-02')
        self.assertEqual(result['control_n'],20)
        self.assertEqual(result['control_rate'],0.5)
        self.assertEqual(result['treatment_rate'],0.5)


if __name__ == '__main__':
    unittest.main()
