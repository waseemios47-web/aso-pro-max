"""Unit tests for core detectors in aso_audit.py.

Run: cd ~/.claude/skills/aso-pro-max && python3 -m pytest tests/
Or:  python3 tests/test_aso_audit.py  (uses unittest)
"""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from aso_audit import (
    LocaleMeta, stem, tokenize, char_count,
    check_budget, check_cross_field_dup,
    check_same_language_dup, check_translit_traps, check_keywords_format,
)


class TestStem(unittest.TestCase):
    def test_english_same_root(self):
        # Snowball: bride/brides/bridal → 同 stem
        self.assertEqual(stem("bride", "en-US"), stem("brides", "en-US"))
        self.assertEqual(stem("wed", "en-US"), stem("wedding", "en-US"))
        self.assertEqual(stem("photo", "en-US"), stem("photograph", "en-US")[:5])

    def test_french_same_root(self):
        # marié / mariée 同 stem
        self.assertEqual(stem("marié", "fr-FR"), stem("mariée", "fr-FR"))

    def test_cjk_no_stemming(self):
        # CJK 整词
        self.assertEqual(stem("結婚", "ja"), "結婚")
        self.assertNotEqual(stem("結婚", "ja"), stem("結婚式", "ja"))


class TestTokenize(unittest.TestCase):
    def test_english_word_split(self):
        self.assertEqual(
            sorted(tokenize("WePics - AI Couple Portraits", "en-US")),
            sorted(["wepics", "ai", "couple", "portraits"])
        )

    def test_cjk_punctuation_split(self):
        # CJK 按标点 / 空格 / 连字符切
        tokens = tokenize("WePics - AIフォトウェディング前撮り", "ja")
        self.assertIn("wepics", tokens)
        self.assertIn("aiフォトウェディング前撮り", tokens)
        # 不应被切成一个超长 token
        self.assertNotIn("wepics - aiフォトウェディング前撮り", tokens)


class TestCharCount(unittest.TestCase):
    def test_cjk_one_codepoint_per_char(self):
        self.assertEqual(char_count("結婚"), 2)
        self.assertEqual(char_count("微出片"), 3)

    def test_ascii_one_codepoint_per_char(self):
        self.assertEqual(char_count("WePics"), 6)


class TestCheckBudget(unittest.TestCase):
    def test_keywords_over_limit_errors(self):
        m = LocaleMeta(locale="en-US", keywords="a" * 101)
        out = check_budget(m)
        self.assertTrue(any(f.severity == "error" for f in out))

    def test_keywords_underuse_warns(self):
        m = LocaleMeta(locale="en-US", keywords="a,b")
        out = check_budget(m)
        self.assertTrue(any("未充分利用" in f.msg for f in out))

    def test_cjk_short_name_not_warned(self):
        m = LocaleMeta(locale="zh-Hans", name="微出片", subtitle="一键合成", keywords="x")
        out = check_budget(m)
        self.assertFalse(any(f.field == "name" and "过短" in f.msg for f in out))

    def test_en_short_name_warned(self):
        m = LocaleMeta(locale="en-US", name="App", subtitle="Hello", keywords="x")
        out = check_budget(m)
        self.assertTrue(any(f.field == "name" and "过短" in f.msg for f in out))


class TestCrossFieldDup(unittest.TestCase):
    def test_en_stem_dup_detected(self):
        # name 含 "Couple"，keyword 含 "couples" → stem 同 → ERROR
        m = LocaleMeta(
            locale="en-US",
            name="MyApp - AI Couple Portraits",
            subtitle="Wedding Photos in Sec",
            keywords="couples,swap"
        )
        out = check_cross_field_dup(m)
        self.assertTrue(any(f.severity == "error" for f in out))

    def test_en_phrase_keyword_dup_detected(self):
        # keyword "wedding ring" 含 "wedding"，与 subtitle "Wedding" 重 → ERROR
        m = LocaleMeta(
            locale="en-US",
            name="MyApp",
            subtitle="Wedding Photos",
            keywords="wedding ring,engagement"
        )
        out = check_cross_field_dup(m)
        self.assertTrue(any(f.severity == "error" for f in out))

    def test_cjk_substring_warn(self):
        # ja keyword "フォトウェディング" ⊂ name "AIフォトウェディング前撮り" → WARN
        m = LocaleMeta(
            locale="ja",
            name="MyApp - AIフォトウェディング前撮り",
            subtitle="二人の写真",
            keywords="フォトウェディング,プレ花嫁"
        )
        out = check_cross_field_dup(m)
        self.assertTrue(any(f.severity == "warn" and "CJK 子串" in f.msg for f in out))

    def test_no_dup_passes(self):
        m = LocaleMeta(
            locale="en-US",
            name="MyApp",
            subtitle="Photos",
            keywords="engagement,vows,knot"
        )
        out = check_cross_field_dup(m)
        self.assertEqual(out, [])


class TestSameLanguageDup(unittest.TestCase):
    def test_en_us_gb_stem_dup_detected(self):
        # phrase "bride groom" 含 bride (stem=bride)，与单字 brides (stem=bride) 跨 locale 同根
        metas = {
            "en-US": LocaleMeta(locale="en-US", keywords="bride groom,vows"),
            "en-GB": LocaleMeta(locale="en-GB", keywords="brides,pose"),
        }
        out = check_same_language_dup(metas)
        self.assertTrue(any("bride" in str(f.msg) for f in out))

    def test_different_words_no_dup(self):
        metas = {
            "en-US": LocaleMeta(locale="en-US", keywords="engagement,vows"),
            "en-GB": LocaleMeta(locale="en-GB", keywords="pose,bouquet"),
        }
        out = check_same_language_dup(metas)
        self.assertEqual(out, [])


class TestTranslitTraps(unittest.TestCase):
    def test_japanese_retro_warned(self):
        m = LocaleMeta(locale="ja", keywords="婚礼,神社,レトロ")
        out = check_translit_traps(m)
        self.assertTrue(any("レトロ" in str(f.msg) for f in out))

    def test_korean_vintage_warned(self):
        m = LocaleMeta(locale="ko", keywords="커플사진,빈티지")
        out = check_translit_traps(m)
        self.assertTrue(any("빈티지" in str(f.msg) for f in out))

    def test_korean_old_traps_extended(self):
        # ko 清单含 6 个词
        m = LocaleMeta(locale="ko", keywords="리터칭,부케,셀카")
        out = check_translit_traps(m)
        msg = str(out[0].msg) if out else ""
        self.assertIn("리터칭", msg)
        self.assertIn("부케", msg)


class TestKeywordsFormat(unittest.TestCase):
    def test_comma_with_space_warned(self):
        m = LocaleMeta(locale="en-US", keywords="bride, groom, wedding")
        out = check_keywords_format(m)
        self.assertTrue(any("逗号后含空格" in f.msg for f in out))

    def test_no_space_passes(self):
        m = LocaleMeta(locale="en-US", keywords="bride,groom,wedding")
        out = check_keywords_format(m)
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
