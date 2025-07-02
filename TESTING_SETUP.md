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
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest weblate/api/tests.py::CategoryAPITest::test_bulk_add_label -v"
```

#### API Tests Only
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest weblate/api/ -v"
```

#### Full Test Suite (takes 10-30 minutes)
```bash
docker-compose -f dev-docker/docker-compose.yml exec weblate bash -c "cd /app/src && export CI_DATABASE=postgresql && export CI_DB_USER=weblate && export CI_DB_PASSWORD=weblate && export CI_DB_HOST=database && export CI_DB_PORT=5432 && export DJANGO_SETTINGS_MODULE=weblate.settings_test && pytest -v"
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
**Solution**: Use `echo "yes" |` to auto-confirm, or run with `--reuse-db` flag

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

## Notes

- The first run after starting containers may take longer as dependencies are installed
- Always use the full environment variable setup for consistent test results
- The test database is automatically created and managed by Django
- Some tests may require specific permissions or user roles to be set up correctly

## API Testing Best Practices

1. **Use `do_request()` helper**: The test base class provides a `do_request()` method that handles authentication and common setup
2. **Test permissions explicitly**: Create users with and without permissions to test access control
3. **Clean up test data**: Always clean up any test data created during tests
4. **Use proper error assertions**: Check for specific error attributes in the response structure

Example:
```python
# Check for specific error attributes
error_attrs = [e.get("attr") for e in response.data.get("errors", [])]
self.assertIn("error", error_attrs)
```
