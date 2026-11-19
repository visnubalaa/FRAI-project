import unittest
from classifier import validate_response, route_check, red_flag_check, process_complaint, FALLBACK_RESPONSE


class ValidatorTests(unittest.TestCase):
    def test_valid_json(self):
        ok, data, _ = validate_response('{"category":"pain","priority":"today","summary":"Headache since morning"}')
        self.assertTrue(ok)
        self.assertEqual(data["category"], "pain")
    def test_invalid_category(self):
        self.assertFalse(validate_response('{"category":"medical","priority":"today","summary":"Headache"}')[0])
    def test_extra_field(self):
        self.assertFalse(validate_response('{"category":"pain","priority":"today","summary":"Headache","extra":1}')[0])
    def test_long_summary(self):
        self.assertFalse(validate_response('{"category":"pain","priority":"today","summary":"one two three four five six seven eight nine ten eleven twelve thirteen"}')[0])
    def test_route_invalid_category(self):
        self.assertEqual(route_check({"category":"bad","priority":"routine","summary":"ok"})["category"], "other")
    def test_red_flag(self):
        self.assertEqual(red_flag_check("I have chest pain", {"priority":"routine"})["priority"], "see_now")

if __name__ == "__main__":
    unittest.main()
