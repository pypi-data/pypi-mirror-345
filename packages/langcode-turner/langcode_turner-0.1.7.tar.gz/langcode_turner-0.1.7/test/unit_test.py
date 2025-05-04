from langcode_turner import langcode_turner
import unittest

class Test(unittest.TestCase):

    def test_iso639_turner(self):
        turn = langcode_turner("fr")
        assert turn.iso_639_3 == "fra"

    def test_iso639_turn_to_ids_code(self):
        turn = langcode_turner("est")
        assert turn.ids_code == "127"

    def test_iso639_turn_to_ids_code_error(self):
        turn = langcode_turner("jpn")
        assert turn.ids_code == ""
    
    def test_language_name_to_turn(self):
        turn = langcode_turner("French")
        assert turn.iso_639_3 == "fra"

    def test_lanauge_name_to_wordnet(self):
        turn = langcode_turner("Chinese")
        assert turn.wordnet() == "cmn-Hans"
        turn = langcode_turner("French")
        assert turn.wordnet() == "fr"
    def test_langcode_aliyun(self):
        turn = langcode_turner("zh")
        assert turn.aliyun_lang_code == "zh"
    def test_langcode_huawei(self):
        turn = langcode_turner("zh")
        assert turn.huawei_lang_code == "zh"
    def test_langcode_arc(self):
        turn = langcode_turner("zh")
        assert turn.arc_lang_code == "zh"
if __name__ == '__main__':
    unittest.main()