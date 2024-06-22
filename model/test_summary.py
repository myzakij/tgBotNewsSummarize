import unittest

from summary import summarize_text

class TestSummarization(unittest.TestCase):
    
    def setUp(self):
        self.text_short = "Это короткая версия текста для теста суммаризации"
        self.text_long = """Это удлиненная версия текста в котором больше слов для теста суммаризации.
                            Это важно проверить, чтобы знать как себя поведет языковая модель."""
        self.text_empty = ""

    def test_short_text(self):
        summary = summarize_text(self.text_short)
        self.assertTrue(len(summary) > 0, "Суммаризация не должна быть пустой")
        print("Test 'test_short_text' passed.")
        
    def test_long_text(self):
        summary = summarize_text(self.text_long)
        self.assertTrue(len(summary) > 0, "Суммаризация не должна быть пустой")
        print("Test 'test_long_text' passed.")

    def test_empty_text(self):
        summary = summarize_text(self.text_empty)
        self.assertNotEqual(summary, "", "Суммаризация не должна быть пустой")
        print("Test 'test_empty_text' passed.")
        
    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            summarize_text(45678987654345678909876545678905567876545678987654) 
        print("Test 'test_invalid_input' passed.")
        
if __name__ == '__main__':
    unittest.main()
