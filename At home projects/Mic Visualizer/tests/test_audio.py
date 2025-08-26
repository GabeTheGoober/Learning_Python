import unittest
from unittest.mock import patch
from audio_processor import AudioWorker
from PyQt5.QtCore import QThread

class TestAudioWorker(unittest.TestCase):
    def setUp(self):
        self.audio_worker = AudioWorker(device_index=0)
    
    @patch('pyaudio.PyAudio')
    def test_audio_worker_initialization(self, mock_pyaudio):
        """Test AudioWorker initialization."""
        self.assertEqual(self.audio_worker.device_index, 0)
        self.assertFalse(self.audio_worker.running)
        self.assertEqual(self.audio_worker.threshold, 300)
    
    def test_set_frequency_analysis(self):
        """Test enabling/disabling frequency analysis."""
        self.audio_worker.set_frequency_analysis(True)
        self.assertTrue(self.audio_worker.frequency_analysis)
        self.audio_worker.set_frequency_analysis(False)
        self.assertFalse(self.audio_worker.frequency_analysis)
    
    def test_set_threshold(self):
        """Test setting the threshold."""
        self.audio_worker.set_threshold(500)
        self.assertEqual(self.audio_worker.threshold, 500)

if __name__ == '__main__':
    unittest.main()