# PyPI Deployment Setup Guide for airbyte-prefect

This guide will walk you through setting up your PyPI accounts and credentials to deploy `airbyte-prefect`.

## Prerequisites

✅ You've already completed:
- [x] Built the package (`dist/` folder contains v1.0.0 distributions)
- [x] Installed `build` and `twine` tools
- [x] Created git tag `v1.0.0`

## Step 1: Create PyPI Accounts

### 1.1 TestPyPI Account (for testing)

1. Go to: https://test.pypi.org/account/register/
2. Fill in the registration form:
   - **Username**: Choose a unique username
   - **Email**: `oladele2abeeb@gmail.com` (or your preferred email)
   - **Password**: Create a strong password
3. Verify your email address (check inbox for verification link)
4. Complete two-factor authentication (2FA) setup - **REQUIRED**

### 1.2 Production PyPI Account

1. Go to: https://pypi.org/account/register/
2. Fill in the registration form (same as above)
3. Verify your email address
4. Complete two-factor authentication (2FA) setup - **REQUIRED**

**Important**: Use the SAME username on both TestPyPI and PyPI for consistency.

---

## Step 2: Generate API Tokens

API tokens are safer than using passwords and are required for uploads.

### 2.1 Generate TestPyPI Token

1. Log in to TestPyPI: https://test.pypi.org
2. Go to Account Settings: https://test.pypi.org/manage/account/
3. Scroll to "API tokens" section
4. Click **"Add API token"**
5. Fill in the form:
   - **Token name**: `airbyte-prefect-test`
   - **Scope**: Select "Entire account" (for first upload)
     - After first upload, you can create a project-specific token
6. Click **"Add token"**
7. **COPY THE TOKEN IMMEDIATELY** - it starts with `pypi-AgEI...`
8. Store it securely (you won't be able to see it again!)

### 2.2 Generate Production PyPI Token

1. Log in to PyPI: https://pypi.org
2. Go to Account Settings: https://pypi.org/manage/account/
3. Scroll to "API tokens" section
4. Click **"Add API token"**
5. Fill in the form:
   - **Token name**: `airbyte-prefect-prod`
   - **Scope**: Select "Entire account"
6. Click **"Add token"**
7. **COPY THE TOKEN IMMEDIATELY**
8. Store it securely

---

## Step 3: Configure Credentials

You have two options: use `.pypirc` file (recommended) or environment variables.

### Option A: Using `.pypirc` File (Recommended)

Create or edit `~/.pypirc` in your home directory:

```bash
nano ~/.pypirc
```

Add the following content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

**Important Steps:**
1. Replace `pypi-YOUR-PRODUCTION-TOKEN-HERE` with your actual PyPI token
2. Replace `pypi-YOUR-TEST-TOKEN-HERE` with your actual TestPyPI token
3. Secure the file:
   ```bash
   chmod 600 ~/.pypirc
   ```

### Option B: Using Environment Variables

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-PRODUCTION-TOKEN-HERE
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

---

## Step 4: Test Your Setup (TestPyPI)

Before uploading to production PyPI, test with TestPyPI:

```bash
# Use the deployment script
./deploy.sh test

# Or manually:
python -m twine upload --repository testpypi dist/*
```

**What happens:**
1. You'll be prompted for credentials (or it uses `.pypirc`)
2. If using 2FA, you might need to authenticate
3. Upload progress will be shown
4. Success message will include the package URL

**Test Installation:**
```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            airbyte-prefect

# Test import
python -c "from airbyte_prefect import AirbyteConnection, AirbyteServer; print('Success!')"

# Clean up
deactivate
rm -rf test_env
```

---

## Step 5: Deploy to Production PyPI

Once TestPyPI works, deploy to production:

```bash
# Use the deployment script
./deploy.sh prod

# Or manually:
python -m twine upload dist/*
```

**After successful upload:**
- View at: https://pypi.org/project/airbyte-prefect/
- Install with: `pip install airbyte-prefect`
- Share the package with the world! 🎉

---

## Step 6: Push to GitHub

Don't forget to push your commits and tags:

```bash
git push origin main
git push origin v1.0.0
```

---

## Troubleshooting

### Issue: "Invalid or non-existent authentication information"

**Solution**:
- Check that your token starts with `pypi-`
- Ensure username is `__token__` (two underscores)
- Regenerate token if needed

### Issue: "The name 'airbyte-prefect' is already taken"

**Solution**:
- Someone else registered the name
- Choose a different name (e.g., `airbyte-prefect-community`)
- Update `setup.py` with the new name

### Issue: "403 Forbidden"

**Solution**:
- Your token might not have the right scope
- Regenerate a token with "Entire account" scope
- After first upload, you can use project-specific tokens

### Issue: "Package version already exists"

**Solution**:
- You can't re-upload the same version
- Increment version: create a new tag like `v1.0.1`
- Update code and rebuild

### Issue: "File already exists"

**Solution**:
- Delete the existing file on PyPI (if you have permissions)
- Or increment the version number

---

## Security Best Practices

1. ✅ **Never commit `.pypirc` to git** - add to `.gitignore`
2. ✅ **Use API tokens** instead of passwords
3. ✅ **Enable 2FA** on both PyPI accounts
4. ✅ **Use project-specific tokens** after first upload
5. ✅ **Rotate tokens regularly** (every 6-12 months)
6. ✅ **Never share tokens** - generate separate tokens for CI/CD

---

## Quick Reference

### Useful Commands

```bash
# Check package before upload
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*

# Check PyPI package info
pip show airbyte-prefect

# View package on PyPI
open https://pypi.org/project/airbyte-prefect/
```

### Deploy Script Usage

```bash
# Test deployment (TestPyPI)
./deploy.sh test

# Production deployment (PyPI)
./deploy.sh prod
```

---

## Next Steps After Deployment

1. **Update README badges** with PyPI version badge
2. **Create GitHub release** with release notes
3. **Announce on social media** (Twitter, LinkedIn, etc.)
4. **Update documentation** with installation instructions
5. **Monitor PyPI downloads** at https://pypistats.org/packages/airbyte-prefect

---

## Need Help?

- PyPI Help: https://pypi.org/help/
- TestPyPI: https://test.pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/

---

**Ready to deploy? Start with Step 4 (TestPyPI) above!** 🚀
