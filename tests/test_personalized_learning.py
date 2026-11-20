import unittest
from src.personalized_learning import calculate_gaps, merge_learning_recommendations

NAMES = {'C023': 'Risk Management', 'C010': 'Corporate Budgeting'}

class TestPersonalizedLearning(unittest.TestCase):
    def test_gap_priority(self):
        gaps = calculate_gaps([
            {'competency_id':'C023','current_level':2,'required_level':4,'importance':5},
            {'competency_id':'C010','current_level':4,'required_level':4,'importance':3}
        ], NAMES)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0].gap, 2)
        self.assertEqual(gaps[0].priority, 2)

    def test_reject_invalid_assessment(self):
        for entry in [
            {'competency_id':'C999','current_level':1,'required_level':4},
            {'competency_id':'C023','current_level':7,'required_level':4},
            {'competency_id':'C023','current_level':1,'required_level':4,'importance':8},
        ]:
            with self.assertRaises(ValueError):
                calculate_gaps([entry], NAMES)

    def test_merge_and_explanation(self):
        gaps = calculate_gaps([{'competency_id':'C023','current_level':1,'required_level':4}], NAMES)
        docs = [{'book_id':'A','score':0.8,'judul':'Risk'}, {'book_id':'B','score':0.2,'judul':'Other'}]
        results = merge_learning_recommendations(gaps, lambda cid, top_k: docs)
        self.assertEqual(results[0]['book_id'], 'A')
        self.assertIn('tingkat saat ini', results[0]['reason'])
        self.assertEqual(results[0]['target_competency_id'], 'C023')

    def test_zero_gap(self):
        gaps = calculate_gaps([{'competency_id':'C023','current_level':5,'required_level':4}], NAMES)
        self.assertEqual(merge_learning_recommendations(gaps, lambda cid, top_k: []), [])

if __name__ == '__main__': unittest.main()
