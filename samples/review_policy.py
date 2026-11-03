# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpsPilot AI
# Source: private implementation, canonical review policy; runnable evaluation excerpt.
"""Conservative review gate, independent of model instructions and self-reported confidence.

Keyword rules are a baseline, not a guarantee that every risky intent is detected.
No client response, payment or refund is executed by this application.
"""
import re

RISK = re.compile(r"обмен|возврат|верну(?:ть|те)|верните|вернуть|деньг|оплат|плат[её]ж|списа|компенсац|refund|payment|chargeback|взлом|утечк|мошенн|суд|угроз|fraud", re.I)


def review_reasons(text: str, category: str, priority: str, confidence: float) -> list[str]:
    reasons = []
    if RISK.search(text):
        reasons.append("independent_risk_rule")
    if category in {"return", "payment"}:
        reasons.append("financial_category")
    if priority == "critical":
        reasons.append("critical_priority")
    if category == "other" or confidence < 0.6:
        reasons.append("ambiguous_classification")
    return reasons


if __name__ == '__main__':
    # Executable portfolio example; no app database, credentials or model required.
    import unittest
    class ReviewPolicyExample(unittest.TestCase):
        def test_financial_text_despite_wrong_category(self):
            self.assertIn('independent_risk_rule', review_reasons('Верните деньги', 'order', 'low', .99))
        def test_exchange_despite_wrong_category(self):
            self.assertIn('independent_risk_rule', review_reasons('Хочу обменять брюки', 'order', 'low', .99))
        def test_unknown_requires_review(self):
            self.assertTrue(review_reasons('Уточните детали', 'other', 'low', .99))
        def test_ordinary_delivery(self):
            self.assertEqual(review_reasons('Когда приедет посылка?', 'delivery', 'low', .9), [])
    unittest.main()
