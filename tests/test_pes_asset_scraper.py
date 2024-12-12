import os
import unittest
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pes_asset_scraper import PESAssetScraper

class TestPESAssetScraper(unittest.TestCase):
    def setUp(self):
        """
        Setup test environment for PESAssetScraper
        """
        # Create temporary directory for downloads
        self.test_dir = tempfile.mkdtemp()
        
        # Initialize scraper with test directory
        self.scraper = PESAssetScraper(base_dir=self.test_dir)
    
    def tearDown(self):
        """
        Clean up temporary test files
        """
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('pes_asset_scraper.requests.get')
    def test_download_image_success(self, mock_get):
        """
        Test successful image download
        """
        # Mock image download
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'test_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Prepare download path
        download_path = os.path.join(self.test_dir, 'test_logo.png')
        
        # Download image
        result = self.scraper._download_image('https://example.com/logo.png', download_path)
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(os.path.exists(download_path))
    
    @patch('pes_asset_scraper.requests.get')
    def test_download_image_failure(self, mock_get):
        """
        Test image download failure
        """
        # Simulate download failure
        mock_get.side_effect = Exception("Download failed")
        
        # Prepare download path
        download_path = os.path.join(self.test_dir, 'failed_logo.png')
        
        # Download image
        result = self.scraper._download_image('https://example.com/logo.png', download_path)
        
        # Assertions
        self.assertFalse(result)
        self.assertFalse(os.path.exists(download_path))
    
    @patch('pes_asset_scraper.requests.get')
    def test_search_team(self, mock_get):
        """
        Test team search functionality
        """
        # Mock search response
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <a href="/team/manchester-united">Manchester United</a>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Search for team
        result = self.scraper.search_team('Manchester United')
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertTrue('manchester-united' in result)
    
    @patch.object(PESAssetScraper, 'download_team_assets')
    def test_download_multiple_teams(self, mock_download):
        """
        Test downloading assets for multiple teams
        """
        # Mock download results
        mock_download.side_effect = [
            {'logo': True, 'kit': True},
            {'logo': False, 'kit': True},
            None
        ]
        
        # Teams to download
        teams = ['Manchester United', 'Liverpool', 'Barcelona']
        
        # Download assets
        results = self.scraper.download_multiple_teams(teams)
        
        # Assertions
        self.assertEqual(len(results), 3)
        self.assertTrue(results['Manchester United']['logo'])
        self.assertTrue(results['Manchester United']['kit'])
        self.assertFalse(results['Liverpool']['logo'])
        self.assertTrue(results['Liverpool']['kit'])
        self.assertIsNone(results['Barcelona'])
    
    def test_sanitize_filename(self):
        """
        Test filename sanitization
        """
        # Test cases
        test_cases = [
            ('Manchester United', 'Manchester_United'),
            ('Team/with/slashes', 'Team_with_slashes'),
            ('Invalid:Chars', 'Invalid_Chars')
        ]
        
        for input_name, expected_output in test_cases:
            result = self.scraper._sanitize_filename(input_name)
            self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
