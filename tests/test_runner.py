import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from test_transfer_manager import TestTransferManager
from test_database_manager import TestPESDatabaseManager
from test_pes_asset_scraper import TestPESAssetScraper
from test_integration import TestPESUpdaterIntegration
from test_edge_cases import TestEdgeCases

def run_tests():
    """
    Run all test suites and generate a comprehensive report
    """
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestTransferManager,
        TestPESDatabaseManager,
        TestPESAssetScraper,
        TestPESUpdaterIntegration,
        TestEdgeCases
    ]
    
    for test_case in test_cases:
        test_suite.addTests(unittest.makeSuite(test_case))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
