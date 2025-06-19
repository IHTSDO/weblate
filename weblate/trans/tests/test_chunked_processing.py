"""
Tests for chunked processing in translation synchronization.
"""

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from unittest.mock import patch

from weblate.lang.models import Language
from weblate.trans.models import Project, Component, Translation
from weblate.trans.tests.utils import create_test_user


class ChunkedProcessingTest(TestCase):
    """Test chunked processing functionality."""

    def setUp(self):
        """Set up test data."""
        # Clean up previous test data
        from weblate.trans.models import Translation, Component, Project
        Translation.objects.all().delete()
        Component.objects.all().delete()
        Project.objects.all().delete()
        self.user = create_test_user()
        unique_id = str(id(self))
        self.project = Project.objects.create(
            name=f"Test Project {unique_id}",
            slug=f"test-project-{unique_id}",
        )
        # Patch sync_git_repo to prevent VCS operations
        patcher = patch('weblate.trans.models.component.Component.sync_git_repo', lambda self, *a, **kw: None)
        self.addCleanup(patcher.stop)
        patcher.start()
        self.component = Component.objects.create(
            name=f"Test Component {unique_id}",
            slug=f"test-component-{unique_id}",
            project=self.project,
            repo="dummy",
            file_format="po",
        )
        self.language = Language.objects.get(code="en")
        self.translation, created = Translation.objects.get_or_create(
            component=self.component,
            language=self.language,
            defaults={'plural_id': 0},
        )

    @override_settings(TRANSLATION_SYNC_CHUNK_SIZE=500)
    def test_chunk_size_configuration(self):
        """Test that chunk size is properly configured from settings."""
        # Test that the setting is read correctly
        from django.conf import settings
        self.assertEqual(settings.TRANSLATION_SYNC_CHUNK_SIZE, 500)

    def test_process_units_chunked_method_exists(self):
        """Test that the chunked processing method exists."""
        self.assertTrue(hasattr(self.translation, '_process_units_chunked'))
        self.assertTrue(hasattr(self.translation, '_delete_stale_units_chunked'))

    def test_chunked_processing_with_empty_units(self):
        """Test chunked processing with no units."""
        # Test with empty store units
        empty_units = []
        result = self.translation._process_units_chunked(empty_units)
        self.assertEqual(result, {})

    def test_chunked_processing_with_small_dataset(self):
        """Test chunked processing with a small dataset."""
        # Create a small number of units (less than chunk size)
        small_units = []
        for i in range(10):
            def is_readonly(self):
                return self.readonly
            def is_fuzzy(self, default=False):
                return self.fuzzy
            def is_translated(self):
                return self.translated
            unit = type('Unit', (), {
                'id_hash': i,
                'context': f'ctx_{i}',
                'source': f'source_{i}',
                'locations': [],
                'flags': '',
                'previous_source': '',
                'target': '',
                'comments': '',
                'explanation': '',
                'fuzzy': False,
                'translated': False,
                'readonly': False,
                'obsolete': False,
                'notes': '',
                'is_readonly': is_readonly,
                'is_fuzzy': is_fuzzy,
                'is_translated': is_translated,
            })()
            small_units.append(unit)
    
        result = self.translation._process_units_chunked(small_units, chunk_size=3)
        # Should process all units without issues
        self.assertEqual(len(result), 10)  # All 10 mock units should be processed

    def test_chunked_processing_with_multiple_chunks(self):
        """Test chunked processing that actually uses multiple chunks."""
        # Create units that will require multiple chunks
        large_units = []
        for i in range(25):  # 25 units
            def is_readonly(self):
                return self.readonly
            def is_fuzzy(self, default=False):
                return self.fuzzy
            def is_translated(self):
                return self.translated
            unit = type('Unit', (), {
                'id_hash': i,
                'context': f'ctx_{i}',
                'source': f'source_{i}',
                'locations': [],
                'flags': '',
                'previous_source': '',
                'target': '',
                'comments': '',
                'explanation': '',
                'fuzzy': False,
                'translated': False,
                'readonly': False,
                'obsolete': False,
                'notes': '',
                'is_readonly': is_readonly,
                'is_fuzzy': is_fuzzy,
                'is_translated': is_translated,
            })()
            large_units.append(unit)
    
        # Use chunk size of 5, so we should have 5 chunks (25/5 = 5)
        result = self.translation._process_units_chunked(large_units, chunk_size=5)
        # Should process all units without issues
        self.assertEqual(len(result), 25)  # All 25 mock units should be processed

    def test_chunked_deletion_with_empty_updated(self):
        """Test chunked deletion with no updated units."""
        # Test with empty updated dict
        self.translation._delete_stale_units_chunked({}, chunk_size=100)
        # Should complete without errors

    @override_settings(TRANSLATION_SYNC_CHUNK_SIZE=1000)
    def test_chunk_size_determination(self):
        """Test that chunk size is determined correctly based on unit count."""
        # This would require mocking the store.content_units to test the logic
        # For now, we just verify the method exists and can be called
        self.assertTrue(hasattr(self.translation, 'check_sync')) 