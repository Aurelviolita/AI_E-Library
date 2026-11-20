"""Regresi akses buku dan provenance skor; Google Books API di-mock."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import api

class BookAccessV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.client = TestClient(api.app)

    def test_catalog_detail_has_source_link(self):
        response = self.client.get('/api/v1/catalog/BK00001')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['source_url'].startswith('https://books.google.co.id/'))

    def test_access_fallback_without_google_api(self):
        with patch.object(api, 'google_books_access', side_effect=TimeoutError('network')):
            data = self.client.get('/api/v1/catalog/BK00001/access').json()
        self.assertEqual(data['verification'], 'metadata_unavailable')
        self.assertIsNone(data['preview_url'])
        self.assertTrue(data['source_url'])

    def test_access_preview_only_if_confirmed(self):
        with patch.object(api, 'google_books_access', return_value={
            'viewability':'PARTIAL', 'is_full_readable':False,
            'preview_url':'https://books.google.com/books?id=abc', 'web_reader_url':None,
        }):
            data = self.client.get('/api/v1/catalog/BK00001/access').json()
        self.assertEqual(data['verification'], 'google_books_api')
        self.assertFalse(data['is_full_readable'])
        self.assertTrue(data['preview_url'])

    def test_invalid_host_is_not_shared(self):
        self.assertIsNone(api.safe_google_books_url('https://books.google.com.evil.example/'))
        self.assertIsNone(api.safe_google_books_url('javascript:alert(1)'))

    def test_personalized_source_explicit_and_links(self):
        data = self.client.post('/api/v1/personalized-learning', json={
            'assessment_source':'simulasi',
            'assessments':[{'competency_id':'C023','current_level':2,'required_level':4,'importance':3}],
            'top_k':2,
        }).json()
        self.assertEqual(data['assessment_source'], 'simulasi')
        self.assertIn('Simulasi', data['assessment_note'])
        self.assertTrue(data['books'][0]['source_url'])

if __name__ == '__main__': unittest.main()
