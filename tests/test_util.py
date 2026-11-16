"""Stable filesystem-safe job names for movie titles."""
import unicodedata
import unittest

from easyedit import web
from easyedit.util import slugify


class SlugifyTests(unittest.TestCase):
    def test_ascii_titles_keep_existing_job_names(self):
        self.assertEqual(slugify("The Wolf of Wall Street!"), "the-wolf-of-wall-street")
        self.assertEqual(slugify("A" * 80), "a" * 60)

    def test_accents_are_normalized_before_stripping(self):
        self.assertEqual(slugify("Amélie"), "amelie")
        self.assertEqual(slugify("Amélie"), slugify(unicodedata.normalize("NFD", "Amélie")))

    def test_non_latin_titles_have_distinct_stable_job_names(self):
        titles = ["千と千尋の神隠し", "Спутник", "기생충", "Κυνόδοντας", "🎬", "🎥", ""]
        slugs = [slugify(title) for title in titles]
        self.assertEqual(len(set(slugs)), len(titles))
        for title, slug in zip(titles, slugs):
            with self.subTest(title=title):
                self.assertEqual(slug, slugify(title))
                self.assertRegex(slug, r"^[a-z0-9-]+$")
                self.assertNotEqual(slug, "edit")
                self.assertLessEqual(len(slug), 60)

    def test_equivalent_non_latin_unicode_has_the_same_fallback(self):
        title = "Κυνόδοντας"
        self.assertEqual(slugify(title), slugify(unicodedata.normalize("NFD", title)))

    def test_truncation_strips_trailing_hyphens_for_web_safe_job(self):
        titles = [
            "Everything Everywhere All at Once Special Edition Directors Cut",
            "The Lord of the Rings The Fellowship of the Ring Extended A Journey",
        ]
        for title in titles:
            with self.subTest(title=title):
                slug = slugify(title)
                self.assertFalse(slug.endswith("-"))
                self.assertLessEqual(len(slug), 60)
                self.assertIsNotNone(web.safe_job(slug))
                self.assertRegex(slug, web._SLUG)
