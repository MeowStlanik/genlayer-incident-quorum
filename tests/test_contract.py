import json
import unittest
from contract_harness import Harness, UserError, Address, Return

class IncidentTests(unittest.TestCase):
    def setUp(self):
        self.h=Harness('incident-quorum','IncidentQuorum');self.c=self.h.contract
        self.urls=['https://status.vendor.example/report','https://monitor.example/report','https://archive.example/report']
        self.c.register('api','Merchant API',json.dumps(self.urls),30)
        for url in self.urls:self.h.pages[url]='On 2025-01-01 the Merchant API outage started 01:00 UTC and ended 02:00 UTC.'

    def finding(self,status='OUTAGE',start=60,end=120):
        return {'status':status,'start':start if status=='OUTAGE' else 0,'end':end if status=='OUTAGE' else 0,
                'quote':'outage started 01:00 UTC and ended 02:00 UTC' if status=='OUTAGE' else ''}

    def test_correlated_minutes_not_sum_of_durations(self):
        rows=[self.finding(start=10,end=60),self.finding(start=40,end=90),self.finding('UNKNOWN')]
        self.assertEqual(self.h.ns['derive'](rows,30),{'outcome':'UNKNOWN','corroborated_minutes':20})
        self.assertEqual(self.h.ns['derive'](rows,20)['outcome'],'OUTAGE')

    def test_unknown_never_becomes_healthy(self):
        self.assertEqual(self.h.ns['derive']([self.finding('UNKNOWN')]*3,30)['outcome'],'UNKNOWN')

    def test_contradictory_sources_disputed(self):
        rows=[self.finding(),self.finding(),self.finding('HEALTHY')]
        self.assertEqual(self.h.ns['derive'](rows,30)['outcome'],'DISPUTED')

    def test_real_control_flow_refetches_all_three_sources(self):
        self.h.outputs=[self.finding()]*6
        self.c.observe('api','2025-01-01')
        receipt=json.loads(self.c.get_receipt('api','2025-01-01',1))
        self.assertEqual(receipt['outcome'],'OUTAGE')
        self.assertEqual(receipt['corroborated_minutes'],60)
        self.assertEqual(self.h.web_calls,self.urls*2)
        with self.assertRaises(UserError):self.c.observe('api','2025-01-01')

    def test_independent_interval_disagreement_rejected(self):
        self.h.outputs=[self.finding()]*3+[self.finding(start=61)]*3
        with self.assertRaisesRegex(UserError,'consensus rejected'):self.c.observe('api','2025-01-01')
        self.assertEqual(self.c.latest_attempt('api','2025-01-01'),0)

    def test_different_hosts_and_closed_day_required(self):
        with self.assertRaises(UserError):self.c.register('bad','x',json.dumps([self.urls[0]]*3),30)
        with self.assertRaises(UserError):self.c.observe('api','2999-01-01')

    def test_unknown_retries_are_capped(self):
        for _ in range(3):
            self.h.outputs=[self.finding('UNKNOWN')]*6
            self.c.observe('api','2025-01-01')
        with self.assertRaises(UserError):self.c.observe('api','2025-01-01')

if __name__ == '__main__': unittest.main()
