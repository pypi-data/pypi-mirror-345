import unittest
from ipulse_shared_base_ftredge import ProgressStatus

class TestProgressStatusEnum(unittest.TestCase):  

    def test_progress_status_sets_complement(self):
            """Test that closed_or_skipped and pending statuses are complementary and complete"""
            # Get all enum values
            all_statuses = set(ProgressStatus)
            
            # Get the sets to compare
            closed_or_skipped = set(ProgressStatus.closed_or_skipped_statuses())
            pending = set(ProgressStatus.pending_or_blocked_statuses())
            
            # Test no intersection
            intersection = closed_or_skipped.intersection(pending)
            assert len(intersection) == 0, f"Found overlapping statuses: {intersection}"
            
            # Test union covers all statuses
            union = closed_or_skipped.union(pending)
            assert union == all_statuses, f"Missing statuses: {all_statuses - union}, Extra statuses: {union - all_statuses}"
            
            # Additional verification of individual elements
            assert all(isinstance(status, ProgressStatus) for status in closed_or_skipped)
            assert all(isinstance(status, ProgressStatus) for status in pending)