import unittest

from roughcut.model.clip_names import name_problems


def problem(name):
    return name_problems([name])[0]


class NameProblemsTest(unittest.TestCase):
    def test_good_names_have_no_problem(self):
        self.assertEqual(name_problems(["Breach", "Ambush and push", "raid 03", "v1.2 final"]),
                         [None, None, None, None])

    def test_empty_or_blank_name(self):
        self.assertIsNotNone(problem(""))
        self.assertIsNotNone(problem("   "))

    def test_each_forbidden_character(self):
        for character in '\\/:*?"<>|':
            with self.subTest(character=character):
                message = problem(f"Ambush{character}")
                self.assertIsNotNone(message)
                self.assertIn(character, message)

    def test_control_character(self):
        self.assertIsNotNone(problem("Amb\tush"))

    def test_trailing_space_or_dot(self):
        self.assertIsNotNone(problem("Ambush "))
        self.assertIsNotNone(problem("Ambush."))

    def test_reserved_names_any_case_and_with_extension(self):
        for name in ["con", "NUL.txt", "COM1", "lpt1", "Aux .mp4"]:
            with self.subTest(name=name):
                self.assertIsNotNone(problem(name))

    def test_names_merely_starting_with_a_reserved_word_are_fine(self):
        self.assertIsNone(problem("Console clutch"))
        self.assertIsNone(problem("COM10"))

    def test_duplicates_ignoring_case_flag_both_rows(self):
        problems = name_problems(["Breach", "Ambush", "breach"])
        self.assertIn("3", problems[0])
        self.assertIsNone(problems[1])
        self.assertIn("1", problems[2])

    def test_count_of_problems(self):
        problems = name_problems(["Ambush?", "Breach", "breach", "Extract"])
        self.assertEqual(sum(p is not None for p in problems), 3)


if __name__ == "__main__":
    unittest.main()
