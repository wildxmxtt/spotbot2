import unittest
from unittest.mock import mock_open, patch
import json
import supporting_scripts.config_tools as ct

class TestConfigTools(unittest.TestCase):

    def test_config_data_valid(self):
        # Mock JSON content
        mock_data = '{"key": "value"}'
        expected_result = {"key": "value"}

        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = ct.config_data("dummy_path.json")

        self.assertEqual(result, expected_result)

        result = ct.config_data()

    def test_config_data_invalid(self):
        # Mock JSON content
        mock_data = '{"key": "value"'

        with patch("builtins.open", mock_open(read_data=mock_data)):
            with self.assertRaises(json.JSONDecodeError):
                ct.config_data("dummy_path.json")

    def test_getSpotifyID(self):
        # Track Links
        trackLinks = [
            ["spotifyTrackLink", "https://open.spotify.com/track/2QTDuJIGKUjR7E2Q6KupIh?si=32494c664b10490b"],
            ["spotifyTrackLinkNoSI", "https://open.spotify.com/track/2QTDuJIGKUjR7E2Q6KupIh"],
            ["spotifyTrackURI", "spotify:track:2QTDuJIGKUjR7E2Q6KupIh"]
        ]
        expectedLinkID = "2QTDuJIGKUjR7E2Q6KupIh"

        # Playlist Links
        playlistLinks = [
            ["spotifyPlaylistLink", "https://open.spotify.com/playlist/1qGNevTlHmCimM6AjmFv1u?si=34a16b6f03684936"],
            ["spotifyPlaylistLinkNoSI", "https://open.spotify.com/playlist/1qGNevTlHmCimM6AjmFv1u"],
            ["spotifyPlaylistURI", "spotify:playlist:1qGNevTlHmCimM6AjmFv1u"]
        ]
        expectedPlaylistID = "1qGNevTlHmCimM6AjmFv1u"

        for link in trackLinks:
            # Use the link located at index 1
            result = ct.getSpotifyID(link[1])

            # Test the id
            self.assertEqual(result['id'], expectedLinkID)

            # Test the type
            self.assertEqual(result['type'], "track")

        for link in playlistLinks:
            # Use the link located at index 1
            result = ct.getSpotifyID(link[1])

            # Test the id
            self.assertEqual(result['id'], expectedPlaylistID)

            # Test the type
            self.assertEqual(result['type'], "playlist")

        
if __name__ == "__main__":
    unittest.main()