# Weblate Testing Setup Guide

## Quick Start

### 1. Docker Environment Setup
```bash
# Start the development environment
docker-compose -f dev-docker/docker-compose.yml up -d

# Wait for containers to be healthy (check with: docker-compose -f dev-docker/docker-compose.yml ps)
```

### 2. Volume Mount Fix
**IMPORTANT**: The docker-compose.yml file needs to be corrected for proper volume mounting:

```yaml
# In dev-docker/docker-compose.yml, change:
volumes:
  - $PWD/..:/app/src   # WRONG - mounts parent directory

# To:
volumes:
  - $PWD:/app/src      # CORRECT - mounts current weblate directory
```

### 3. Environment Variables for Testing
```bash
export CI_DATABASE=postgresql
export CI_DB_USER=weblate
export CI_DB_PASSWORD=weblate
export CI_DB_HOST=database
export CI_DB_PORT=5432
export DJANGO_SETTINGS_MODULE=weblate.settings_test
```

### 4. Running Tests

#### Single Test
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest weblate/api/tests.py::OptimizedEndpointAPITest::test_optimized_endpoint_basic -v --reuse-db"
```

#### API Tests Only
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest weblate/api/ -v --reuse-db"
```

#### Export Tests
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest weblate/formats/tests/test_exporters.py::MultiCSVExporterTest -v --reuse-db"
```

#### Full Test Suite (takes 10-30 minutes)
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest -v --reuse-db"
```

## Critical Lessons Learned

### 1. Test Database Issues
**Problem**: `database "test_weblate" already exists`
**Solution**: Always use `--reuse-db` flag to avoid database conflicts

### 2. Component Creation Requirements
**Problem**: `KeyError: ''` when creating Component
**Solution**: Component requires specific fields:
```python
Component.objects.create(
    name="Test Component",
    slug="test-component",
    project=project,
    file_format="po",  # REQUIRED - cannot be empty
    vcs="local"        # Use "local" instead of "none" or "git"
)
```

### 3. Translation Creation Requirements
**Problem**: `null value in column "plural_id" violates not-null constraint`
**Solution**: Translation requires a Plural object:
```python
# Create language first
language, _ = Language.objects.get_or_create(
    code="test-en",
    defaults={"name": "Test English"}
)

# Create plural for the language
from weblate.lang.models import Plural
plural, _ = Plural.objects.get_or_create(
    language=language,
    defaults={"formula": "n != 1"}
)

# Create translation with plural
translation, _ = Translation.objects.get_or_create(
    component=component,
    language=language,
    defaults={"plural": plural}
)
```

### 4. Unit Creation Requirements
**Problem**: `null value in column "position" violates not-null constraint`
**Solution**: Unit requires position field:
```python
Unit.objects.create(
    translation=translation,
    source="Test source",
    target="Test target",
    state=StringState.STATE_TRANSLATED,  # Use STATE_TRANSLATED, not TRANSLATED
    id_hash=12345,
    position=1  # REQUIRED - cannot be null
)
```

### 5. StringState Constants
**CRITICAL**: Always use the correct StringState constants:
```python
# CORRECT:
StringState.STATE_TRANSLATED
StringState.STATE_FUZZY
StringState.STATE_APPROVED

# WRONG (causes AttributeError):
StringState.TRANSLATED
StringState.FUZZY
StringState.APPROVED
```

### 6. URL Pattern Requirements
**Problem**: `NoReverseMatch` for API endpoints
**Solution**: Use correct URL parameter names:
```python
# CORRECT:
kwargs={
    "component__project__slug": project.slug,
    "component__slug": component.slug,
    "language__code": language.code,
}

# WRONG:
kwargs={
    "project__slug": project.slug,  # Should be component__project__slug
    "component__slug": component.slug,
    "language__code": language.code,
}
```

### 7. Test Class Inheritance
**For API Tests**: Use `APIBaseTest` instead of `TestCase`
```python
class OptimizedEndpointAPITest(APIBaseTest):  # Inherit from APIBaseTest
    def setUp(self) -> None:
        super().setUp()  # Call parent setUp
        # Add custom setup here
```

**For Export Tests**: Use `TestCase` or existing test base classes
```python
class MultiCSVExporterTest(TestCase):  # Inherit from TestCase
    def setUp(self):
        # Setup here
```

### 8. Required Imports for API Tests
When adding new API tests to `weblate/api/tests.py`, ensure these imports:
```python
from rest_framework import status
from weblate.utils.state import StringState
```

### 9. Error Response Format
**Problem**: Test assertions don't match actual error response format
**Solution**: Django REST Framework returns structured error responses:
```python
# Test for validation errors:
self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
data = response.json()
self.assertEqual(data["type"], "validation_error")
self.assertTrue(any(error["attr"] == "since" for error in data["errors"]))
```

### 10. Test Data Uniqueness
**Problem**: `IntegrityError: duplicate key value violates unique constraint`
**Solution**: Use `get_or_create` for test data and unique identifiers:
```python
# Use unique names/slugs
self.user, _ = User.objects.get_or_create(
    username="testuser_optimized",  # Unique username
    defaults={"password": "testpass"}
)

self.project, _ = Project.objects.get_or_create(
    slug="test-project-optimized",  # Unique slug
    defaults={"name": "Test Project Optimized"}
)
```

## Common Issues & Solutions

### 1. "No pyproject.toml found" Error
**Problem**: Container can't find the source code
**Solution**: Fix volume mount in docker-compose.yml (see step 2 above)

### 2. Database Connection Issues
**Problem**: Tests can't connect to PostgreSQL
**Solution**: Ensure all environment variables are set correctly (see step 3)

### 3. Permission Issues in Tests
**Problem**: Tests fail with 403 errors when expecting 400
**Solution**: Weblate has granular permissions. Use `project.add_user(user, "Administration")` to grant permissions in tests

### 4. Test Database Issues
**Problem**: Django asks to delete test database
**Solution**: Use `--reuse-db` flag to avoid database recreation

### 5. Stopping Long-Running Tests
```bash
# Kill pytest process
docker-compose -f dev-docker/docker-compose.yml exec weblate pkill -f pytest

# Check if process is still running
docker-compose -f dev-docker/docker-compose.yml exec weblate ps aux | grep pytest
```

## Useful Commands

### Check Container Status
```bash
docker-compose -f dev-docker/docker-compose.yml ps
```

### View Container Logs
```bash
docker-compose -f dev-docker/docker-compose.yml logs weblate
```

### Restart Environment
```bash
docker-compose -f dev-docker/docker-compose.yml down
docker-compose -f dev-docker/docker-compose.yml up -d
```

### Run Migrations
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate python /app/src/manage.py migrate
```

## Project Layout Notes

### Test File Organization
- **API Tests**: All in `weblate/api/tests.py` (single large file)
- **Export Tests**: In `weblate/formats/tests/test_exporters.py`
- **Model Tests**: In `weblate/trans/tests/`

### Test Class Patterns
- **API Tests**: Inherit from `APIBaseTest`
- **Export Tests**: Inherit from `TestCase`
- **Model Tests**: Inherit from `RepoTestMixin` or `TestCase`

### Import Patterns
- Use existing imports in test files when possible
- Add new imports at the top of the file
- Follow the existing import order and grouping

## Performance Notes

### Test Execution Time
- Single API test: ~1-2 seconds
- Full API test suite: ~6-10 seconds
- Full test suite: 10-30 minutes

### Database Performance
- Use `--reuse-db` to avoid database recreation
- Tests run faster after first execution due to cached database
- Consider using `--nomigrations` for faster startup if migrations aren't needed

## Deployment Notes

### Files That Need Deployment
When deploying new features, ensure these files are updated:
1. **`weblate/api/views.py`** - API endpoints
2. **`weblate/formats/exporters.py`** - Export functionality
3. **`weblate/formats/models.py`** - Export format registration
4. **`weblate/utils/views.py`** - Download functionality
5. **`weblate/api/tests.py`** - API tests (if modified)

### StringState Constants
**CRITICAL FOR DEPLOYMENT**: Ensure all `StringState` references use the correct constants:
- `StringState.STATE_TRANSLATED` (not `StringState.TRANSLATED`)
- `StringState.STATE_FUZZY` (not `StringState.FUZZY`)
- `StringState.STATE_APPROVED` (not `StringState.APPROVED`)

This was the main issue that caused the production server error in the optimized endpoint.
