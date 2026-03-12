from __future__ import annotations

import unittest

from evoting.domain.validators import (
    ValidationError,
    calculate_age,
    ensure_in_options,
    ensure_matches,
    ensure_non_empty,
    ensure_password_length,
    parse_birth_date_and_age,
    parse_int_list,
)


class ValidatorTests(unittest.TestCase):
    def test_ensure_non_empty_rejects_blank_values(self) -> None:
        with self.assertRaises(ValidationError):
            ensure_non_empty("   ", "Name")

    def test_password_length_enforced(self) -> None:
        with self.assertRaises(ValidationError):
            ensure_password_length("123")
        self.assertEqual(ensure_password_length("123456"), "123456")

    def test_matches_validation(self) -> None:
        with self.assertRaises(ValidationError):
            ensure_matches("a", "b", "Mismatch")

    def test_birth_date_and_age_parsing(self) -> None:
        age_data = parse_birth_date_and_age("2000-01-01")
        self.assertEqual(age_data.birth_date.strftime("%Y-%m-%d"), "2000-01-01")
        self.assertGreaterEqual(age_data.age, 20)

    def test_calculate_age_uses_calendar_boundaries(self) -> None:
        age_data = parse_birth_date_and_age("2004-12-31")
        manual_age = calculate_age(age_data.birth_date)
        self.assertEqual(age_data.age, manual_age)

    def test_parse_int_list_trims_whitespace(self) -> None:
        self.assertEqual(parse_int_list("1, 2,3", "IDs"), [1, 2, 3])

    def test_parse_int_list_rejects_invalid_input(self) -> None:
        with self.assertRaises(ValidationError):
            parse_int_list("1, nope", "IDs")

    def test_ensure_in_options(self) -> None:
        self.assertEqual(ensure_in_options("M", {"M", "F"}, "bad"), "M")
        with self.assertRaises(ValidationError):
            ensure_in_options("X", {"M", "F"}, "bad")


if __name__ == "__main__":
    unittest.main()
