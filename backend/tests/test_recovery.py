"""
Unit Tests for GitPulse Recovery Engine and Handlers.
"""
import unittest
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.git_graph import GitRecoveryEngine
from handlers.ingest_telemetry import lambda_handler as ingest_handler


class TestGitRecoveryEngine(unittest.TestCase):
    def test_detached_head_recovery(self):
        reflog = [
            "abcdef1 HEAD@{0}: checkout: moving from feature-auth to abcdef1",
            "1234567 HEAD@{1}: commit: add login flow"
        ]
        plan = GitRecoveryEngine.analyze(
            state_type="DETACHED_HEAD",
            head_commit="abcdef1234567890",
            branch_name="HEAD",
            reflog_tail=reflog
        )
        self.assertEqual(plan["status"], "DETERMINISTIC_PLAN_READY")
        self.assertEqual(plan["target_branch"], "feature-auth")
        self.assertTrue(len(plan["steps"]) >= 3)
        self.assertIn("git branch rescue/detached-", plan["steps"][0]["command"])
        self.assertIn("git checkout feature-auth", plan["steps"][1]["command"])

    def test_rebase_conflict_recovery(self):
        plan = GitRecoveryEngine.analyze(
            state_type="IN_PROGRESS_REBASE",
            head_commit="fa12345",
            branch_name="feature-payments",
            reflog_tail=[]
        )
        self.assertEqual(plan["status"], "DETERMINISTIC_PLAN_READY")
        self.assertEqual(plan["safety_level"], "BACKUP_FIRST")
        self.assertIn("git diff >", plan["steps"][0]["command"])
        self.assertEqual(plan["steps"][1]["command"], "git rebase --abort")

    def test_accidental_reset_recovery(self):
        reflog = [
            "1111111 HEAD@{0}: reset: moving to HEAD~1",
            "2222222 HEAD@{1}: commit: unpushed work before disaster"
        ]
        plan = GitRecoveryEngine.analyze(
            state_type="ACCIDENTAL_RESET",
            head_commit="1111111",
            branch_name="main",
            reflog_tail=reflog
        )
        self.assertEqual(plan["status"], "DETERMINISTIC_PLAN_READY")
        self.assertEqual(plan["safety_level"], "REFLOG_EXTRACTION")
        self.assertIn("2222222", plan["steps"][0]["command"])

    def test_ingest_handler_missing_fields_fails_early(self):
        # Event missing repo_id and state_type
        event = {
            "body": json.dumps({"author": "dev-alice"})
        }
        res = ingest_handler(event, None)
        self.assertEqual(res["statusCode"], 400)
        body = json.loads(res["body"])
        self.assertEqual(body["error"], "ValidationFailed")


if __name__ == "__main__":
    unittest.main()
