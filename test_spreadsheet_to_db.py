import unittest

from spreadsheet_to_db import (
    get_contributor_name,
    get_article_name,
    convert_date,
    get_source_from_url,
    get_url_from_citation,
    format_classification,
)


class TestGetContributorName(unittest.TestCase):
    def test_strips_trailing_comma_and_date(self):
        self.assertEqual(get_contributor_name("Jane Doe, 3/1"), "Jane Doe")

    def test_strips_trailing_date_without_comma(self):
        self.assertEqual(get_contributor_name("Jane Doe 3/1"), "Jane Doe")


    def test_strips_trailing_period(self):
        self.assertEqual(get_contributor_name("Smith."), "Smith")

    def test_name_only_no_trailing_content(self):
        self.assertEqual(get_contributor_name("Jane Doe"), "Jane Doe")


class TestGetArticleName(unittest.TestCase):
    def test_docstring_example(self):
        source = (
            "Trump's federal workforce cuts: A timeline of firings and "
            "court reversals - USATODAY"
        )
        expected = (
            "Trump's federal workforce cuts: A timeline of firings and "
            "court reversals"
        )
        self.assertEqual(get_article_name(source), expected)

    def test_no_dash_returns_whole_string(self):
        self.assertEqual(get_article_name("No dash here"), "No dash here")



class TestConvertDate(unittest.TestCase):
    def test_full_date_two_digit_year(self):
        self.assertEqual(convert_date("3/15/25"), "2025-03-15")

    def test_full_date_four_digit_year_dash_separated(self):
        self.assertEqual(convert_date("03-15-2025"), "2025-03-15")

    def test_month_day_only_defaults_to_2026(self):
        self.assertEqual(convert_date("3/15"), "2026-03-15")

    def test_pads_single_digit_month_and_day(self):
        self.assertEqual(convert_date("1/5/25"), "2025-01-05")

    def test_invalid_date_returns_none(self):
        self.assertIsNone(convert_date("not a date"))


class TestGetSourceFromUrl(unittest.TestCase):
    def test_nytimes_with_www(self):
        citation = (
            'Bender, Michael C., et al. "Trump Administration Highlights." '
            "The New York Times, 20 Mar. 2025, "
            "www.nytimes.com/live/2025/03/20/us/trump-education-news."
        )
        self.assertEqual(get_source_from_url(citation), "nytimes")

    def test_apnews_without_www_or_scheme(self):
        citation = (
            "Offenhartz, Jake, et al. AP News, 11 Feb. 2025, "
            "apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666"
            "?utm_source=copy&utm_medium=share."
        )
        self.assertEqual(get_source_from_url(citation), "apnews")

    def test_apnews_with_https_scheme(self):
        citation = (
            "Casey, Michael. AP News, 15 April 2025, "
            "https://apnews.com/article/harvard-trump-administration-federal-cuts-"
            "antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d."
        )
        self.assertEqual(get_source_from_url(citation), "apnews")

    def test_no_url_returns_none(self):
        self.assertIsNone(get_source_from_url("no url in this citation"))

    def test_uses_last_url_when_multiple_present(self):
        citation = "See www.example.com then read apnews.com/article/1"
        self.assertEqual(get_source_from_url(citation), "apnews")


class TestGetUrlFromCitation(unittest.TestCase):
    """
    NOTE: get_url_from_citation is documented to return the matched URL
    substring (e.g. "apnews.com/article/..."), but the current implementation
    just returns the compiled regex pattern object instead of applying it.
    These tests assert the documented/intended behavior, so they currently
    fail and flag the bug rather than encode it as correct.
    """

    def test_returns_full_url_with_www(self):
        citation = (
            'Bender, Michael C., et al. "Trump Administration Highlights." '
            "The New York Times, 20 Mar. 2025, "
            "www.nytimes.com/live/2025/03/20/us/trump-education-news."
        )
        self.assertEqual(
            get_url_from_citation(citation),
            "www.nytimes.com/live/2025/03/20/us/trump-education-news",
        )

    def test_returns_full_url_without_scheme(self):
        citation = (
            "Offenhartz, Jake, et al. AP News, 11 Feb. 2025, "
            "apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666"
            "?utm_source=copy&utm_medium=share."
        )
        self.assertEqual(
            get_url_from_citation(citation),
            "apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666"
            "?utm_source=copy&utm_medium=share",
        )

    def test_returns_full_url_with_https(self):
        citation = (
            "Casey, Michael. AP News, 15 April 2025, "
            "https://apnews.com/article/harvard-trump-administration-federal-cuts-"
            "antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d."
        )
        self.assertEqual(
            get_url_from_citation(citation),
            "https://apnews.com/article/harvard-trump-administration-federal-cuts-"
            "antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d",
        )


class TestFormatClassification(unittest.TestCase):
    def test_lowercases_and_replaces_space(self):
        self.assertEqual(format_classification("Norm Violation"), "norm_violation")

    def test_single_word_lowercased(self):
        self.assertEqual(format_classification("Unlawful"), "unlawful")

    def test_multi_word_classification(self):
        self.assertEqual(format_classification("Social Contradiction"), "social_contradiction")

    def test_already_lowercase(self):
        self.assertEqual(format_classification("unconstitutional"), "unconstitutional")

    def test_nan_returns_null_string(self):
        self.assertEqual(format_classification(float("nan")), "NULL")

    def test_none_returns_null_string(self):
        self.assertEqual(format_classification(None), "NULL")

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(format_classification("  Norm Violation  "), "norm_violation")


if __name__ == "__main__":
    unittest.main()
