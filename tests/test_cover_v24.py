"""Cover harus berasal dari volume Google Books yang sama, bukan gambar hasil pencarian bebas."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import api

class CoverV24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(api.app)

    def test_exact_title_uses_official_thumbnail(self):
        payload = {'volumeInfo': {'title':'Business Growth Strategy', 'imageLinks': {
            'thumbnail':'http://books.google.com/books/content?id=realimage'}}}
        with patch.object(api, 'google_books_volume', return_value=payload):
            response = self.client.get('/api/v1/catalog/BK00001/cover')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'verified_google_books')
        self.assertTrue(response.json()['cover_url'].startswith('https://books.google.com/'))

    def test_wrong_title_cannot_display_unrelated_cover(self):
        payload = {'volumeInfo': {'title':'The Art of Bonsai', 'imageLinks': {
            'thumbnail':'https://books.google.com/books/content?id=wrong'}}}
        with patch.object(api, 'google_books_volume', return_value=payload):
            data = self.client.get('/api/v1/catalog/BK00001/cover').json()
        self.assertEqual(data['status'], 'identity_mismatch')
        self.assertIsNone(data['cover_url'])

    def test_network_failure_returns_placeholder_state(self):
        with patch.object(api, 'google_books_volume', side_effect=TimeoutError()):
            data = self.client.get('/api/v1/catalog/BK00001/cover').json()
        self.assertEqual(data['status'], 'metadata_unavailable')
        self.assertIsNone(data['cover_url'])

    def test_image_host_filter(self):
        url, status = api.verified_cover_url({'volumeInfo': {'title':'Business Growth Strategy',
            'imageLinks': {'thumbnail':'https://books.google.com.evil.example/cover.jpg'}}},
            {'title':'Business Growth Strategy', 'isbn':''})
        self.assertIsNone(url)
        self.assertEqual(status, 'unsafe_thumbnail_url')

    def test_nonexistent_book_404(self):
        self.assertEqual(self.client.get('/api/v1/catalog/BK_NOT_REAL/cover').status_code, 404)

if __name__ == '__main__': unittest.main()
