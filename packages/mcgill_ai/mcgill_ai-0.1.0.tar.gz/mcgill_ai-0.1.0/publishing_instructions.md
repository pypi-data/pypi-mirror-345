# Publishing Instructions

## Publishing to TestPyPI (for testing)

1. Register an account on TestPyPI: https://test.pypi.org/account/register/
2. Create an API token: https://test.pypi.org/manage/account/#api-tokens
3. Run the following command:

```bash
uv publish --publish-url https://test.pypi.org/legacy/ --token YOUR_TEST_PYPI_TOKEN
```

## Publishing to PyPI (for production)

1. Register an account on PyPI: https://pypi.org/account/register/
2. Create an API token: https://pypi.org/manage/account/#api-tokens
3. Run the following command:

```bash
uv publish --token YOUR_PYPI_TOKEN
```

You can also set the token as an environment variable to avoid exposing it:

```bash
# Set the token as an environment variable
$env:UV_PUBLISH_TOKEN="your-token-here"

# Then publish without exposing the token in the command
uv publish
``` 