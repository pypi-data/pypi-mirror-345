# -*- coding: utf-8 -*-

import unittest
import spaudio


class TestSpAudioException(unittest.TestCase):
    def setUp(self):
        self.audio = spaudio.SpAudio()

    def tearDown(self):
        self.audio.terminate()
        del self.audio

    def test_open_exception1(self):
        self.audio.open('ro')
        self.assertRaises(RuntimeError, self.audio.open, ('w',))

    def test_open_exception2(self):
        self.audio.open('wo')
        self.assertRaises(RuntimeError, self.audio.open, ('r',))

    def test_open_exception3(self):
        self.audio.open('r')
        self.assertRaises(RuntimeError, self.audio.open, ('r',))

    def test_open_exception4(self):
        self.audio.open('w')
        self.assertRaises(RuntimeError, self.audio.open, ('w',))


if __name__ == '__main__':
    unittest.main()
