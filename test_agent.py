
import unittest

from agent import (
    verify_sql_evidence,
    get_requested_quote_count,
    verify_answer_format,
    verify_quote,
    verify_review,
    enforce_verification,
)


class TestGameInsightsAgent(unittest.TestCase):

    def test_correct_sql_value(self):
        rows = [
            {
                "name": "Cyberpunk 2077",
                "positive_pct": 93.58
            }
        ]

        evidence = [
            {
                "game": "Cyberpunk 2077",
                "metric": "positive_pct",
                "value": 93.58
            }
        ]

        result = verify_sql_evidence(evidence, rows)

        self.assertTrue(result[0]["verified"])

    def test_incorrect_sql_value(self):
        rows = [
            {
                "name": "Cyberpunk 2077",
                "positive_pct": 93.58
            }
        ]

        evidence = [
            {
                "game": "Cyberpunk 2077",
                "metric": "positive_pct",
                "value": 98.58
            }
        ]

        result = verify_sql_evidence(evidence, rows)

        self.assertFalse(result[0]["verified"])

    def test_requested_quote_count(self):
        question = "Find exactly 2 positive reviews"

        result = get_requested_quote_count(question)

        self.assertEqual(result, 2)

    def test_valid_answer_format(self):
        answer = {
            "answer": "Cyberpunk 2077 has 93.58% positive reviews."
        }

        self.assertTrue(verify_answer_format(answer))

    def test_invalid_answer_format(self):
        answer = {
            "answer": "Cyberpunk wins.</answer>"
        }

        self.assertFalse(verify_answer_format(answer))


    def test_existing_review(self):
        result = verify_review("237767431")

        self.assertTrue(result["verified"])
        self.assertFalse(result["positive"])

    def test_fabricated_review(self):
        result = verify_review("nonexistent-review-id")

        self.assertFalse(result["verified"])

    def test_incorrect_quote_rejected(self):
        result = verify_quote(
            "237767431",
            "This is a completely fabricated review quotation."
        )

        self.assertFalse(result)

    def test_missing_sql_evidence_rejected(self):
        answer = {
            "answer": "Cyberpunk has the highest positive review rate.",
            "evidence": [],
            "review_quotes": [],
            "sql_evidence": [],
            "confidence": "high"
        }

        result = enforce_verification(
            answer,
            [],
            require_sql=True
        )

        self.assertEqual(
            result["verification_status"],
            "failed"
        )
        self.assertEqual(result["confidence"], "low")

    def test_wrong_quote_count_rejected(self):
        answer = {
            "answer": "Here is one review.",
            "evidence": [],
            "review_quotes": [],
            "sql_evidence": [],
            "confidence": "high"
        }

        verification = [
            {
                "review_id": "123",
                "fully_verified": True
            }
        ]

        result = enforce_verification(
            answer,
            verification,
            require_quotes=True,
            expected_quote_count=2
        )

        self.assertEqual(
            result["verification_status"],
            "failed"
        )

    def test_duplicate_review_ids_rejected(self):
        answer = {
            "answer": "Here are two reviews.",
            "evidence": [],
            "review_quotes": [],
            "sql_evidence": [],
            "confidence": "high"
        }

        verification = [
            {"review_id": "123", "fully_verified": True},
            {"review_id": "123", "fully_verified": True}
        ]

        result = enforce_verification(
            answer,
            verification,
            require_quotes=True,
            expected_quote_count=2
        )

        self.assertEqual(
            result["verification_status"], "failed"
        )

    def test_fabricated_sql_evidence_rejected(self):
        answer = {
            "answer": "Cyberpunk has 98.58% positive reviews.",
            "evidence": [],
            "review_quotes": [],
            "sql_evidence": [],
            "confidence": "high"
        }

        sql_verification = [
            {
                "game": "Cyberpunk 2077",
                "metric": "positive_pct",
                "value": 98.58,
                "verified": False
            }
        ]

        result = enforce_verification(
            answer,
            [],
            sql_verification=sql_verification,
            require_sql=True
        )

        self.assertEqual(
            result["verification_status"], "failed"
        )
        self.assertEqual(result["confidence"], "low")

    def test_malformed_answer_rejected(self):
        answer = {
            "answer": "Cyberpunk wins.</answer>",
            "evidence": [],
            "review_quotes": [],
            "sql_evidence": [],
            "confidence": "high"
        }

        result = enforce_verification(answer, [])

        self.assertEqual(
            result["verification_status"], "failed"
        )

if __name__ == "__main__":
    unittest.main()
