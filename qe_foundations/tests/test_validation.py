"""Unit tests for the validation runner (Wednesday: unittest).

Run from the repository root:
    python -m unittest qe_foundations.tests.test_validation -v

Two tests are provided and already pass. The others are TODO stubs that FAIL on
purpose (self.fail) until you replace them. You need at least 5 passing tests in
total, including one that uses assertRaises with ValidationFailedError and one
that proves a rule really catches a known planted defect.

Remember (Wednesday): arrange / act / assert, one idea per test, a descriptive
test name, and each test builds its own fresh in-memory database in setUp.
"""
import unittest

from qe_foundations.validation import runner
from qe_foundations.validation.exceptions import ValidationFailedError


class ValidationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.conn = runner.connect(":memory:")
        runner.load_seed(self.conn)
        self.addCleanup(self.conn.close)

    # ---- provided -----------------------------------------------------------
    def test_seed_loads_expected_number_of_rows(self):
        (count,) = self.conn.execute("SELECT COUNT(*) FROM test_runs").fetchone()
        self.assertEqual(count, 60)

    def test_parse_rules_finds_the_required_rule_ids(self):
        ids = {rule.rule_id for rule in runner.parse_rules()}
        required = {f"R-{n:02d}" for n in range(1, 13)} | {"E-01", "E-02"}
        self.assertTrue(required <= ids, f"missing rules: {sorted(required - ids)}")

    # ---- TODO: replace each self.fail with a real test ----------------------
    def test_run_rule_returns_rows_when_rule_holds(self):                                                                  
        rule = runner.Rule(                                                                                                
            rule_id="T-01",                                                                                                
            dimension="Validity",                                                                                          
            description="Probe rule matching no rows",                                                                     
            sql="SELECT run_id FROM test_runs WHERE run_id = -1;",                                                         
            expect=0,                                                                                                      
        )                                                                                                                  
        # Act                                                                                                              
        rows = runner.run_rule(self.conn, rule)                                                                            
        # Assert                                                                       
        self.assertEqual(rows, [])                                                                                         
                                                                                                                        
    def test_run_rule_raises_validation_failed_error_with_the_evidence(self):                                              
        # Arrange - Rule returning run 5003 with expect=0                                                                 
        rule = runner.Rule(                                                                                                
            rule_id="T-02",                                                                                                
            dimension="Validity",                                                                                          
            description="Probe rule catching run 5003",                                                                    
            sql="SELECT run_id FROM test_runs WHERE run_id = 5003;",                                                       
            expect=0,                                                                                                      
        )                                                                                                                  
        # Act & Assert                                                                                                     
        with self.assertRaises(ValidationFailedError) as ctx:                                                              
            runner.run_rule(self.conn, rule)                                                                               
                                                                                                                            
        self.assertEqual(ctx.exception.rule_id, "T-02")                                                                    
        self.assertEqual(ctx.exception.rows, [(5003,)])                                                                    
                                                                                                                               
    def test_duration_rule_catches_the_known_bad_runs(self):                                                               
        # Arrange (load rule R-04)                                                                                          
        rules = {r.rule_id: r for r in runner.parse_rules()}                                                               
        rule_r04 = rules["R-04"]                                                                                           
        # Act (get rows returned by R-04)                                                                                 
        _, rows = runner.fetch_rows(self.conn, rule_r04.sql)                                                               
        returned_ids = {row[0] for row in rows}                                                                            
        # Assert predicted bad runs (used 5009: -250ms, 5016: NULL) are caught                                     
        self.assertEqual(returned_ids, {5009, 5016})                                                                       
                                                                                                                               
    def test_expectation_rule_fails_when_the_expected_row_is_missing(self):                                                
        # Arrange an expectation rule with expect=1 whose SQL matches nothing                                             
        rule = runner.Rule(                                                                                                
            rule_id="E-99",                                                                                                
            dimension="Expectation",                                                                                       
            description="Expectation probe missing target row",                                                            
            sql="SELECT run_id FROM test_runs WHERE run_id = -1;",                                                         
            expect=1,                                                                                                      
        )                                                                                                                  
        # Act/Assert: missing row raises ValidationFailedError                                                       
        with self.assertRaises(ValidationFailedError):                                                                     
            runner.run_rule(self.conn, rule)                                                                               
                                                                                                                               
    def test_duration_rule_does_not_flag_legal_skipped_zero_ms_run(self):                                                  
        # verify decoy run 5004 (SKIPPED with 0 ms) is NOT falsely flagged by R-04                                  
        rules = {r.rule_id: r for r in runner.parse_rules()}                                                               
        rule_r04 = rules["R-04"]                                                                                           
        _, rows = runner.fetch_rows(self.conn, rule_r04.sql)                                                               
        returned_ids = {row[0] for row in rows}                                                                            
        self.assertNotIn(5004, returned_ids)  


if __name__ == "__main__":
    unittest.main()
