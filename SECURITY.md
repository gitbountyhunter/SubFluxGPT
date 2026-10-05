# Security Policy

## Supported Versions

| Version | Supported Until |
|---------|----------------|
| 1.0.x   | Current        |

## Reporting a Vulnerability

If you discover a security vulnerability in SubFluxGPT, please report it responsibly.

### How to Report

1. **Do not** create a public issue
2. Send an email to: your.email@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- Initial response within 48 hours
- Detailed analysis within 7 days
- Patch release based on severity

### Disclosure Policy

We follow responsible disclosure:
- Coordinate with reporter on timeline
- Release patch before public disclosure
- Credit reporter in release notes (if desired)

## Security Best Practices

### API Key Management

- Never commit API keys to the repository
- Use environment variables or `.env` files
- Add `.env` to `.gitignore`
- Rotate keys regularly
- Use separate keys for development/production

### Usage Guidelines

- Only use on targets you have permission to test
- Respect rate limits of all APIs
- Be aware of legal implications of subdomain enumeration
- Follow bug bounty program rules

### Dependencies

We regularly update dependencies for security patches. To stay secure:

```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

## Known Security Considerations

### DNS Resolution

- SubFluxGPT performs DNS resolution which may be logged by DNS servers
- Use with privacy considerations in mind
- Consider using VPN or Tor for sensitive operations

### API Usage

- All API calls are made over HTTPS
- API keys are stored in environment variables
- No sensitive data is logged by default

### BBRF Integration

- BBRF credentials are stored in environment variables
- Ensure your BBRF instance is properly secured
- Use HTTPS for BBRF connections

## Secure Configuration Example

```bash
# .env file (never commit this)
GEMINI_API_KEY=your_key_here
NETLAS_API_KEY=your_key_here

# Use restricted API keys when possible
# Rotate keys regularly
# Use different keys for different environments
```

## Dependency Vulnerability Scanning

We recommend scanning dependencies regularly:

```bash
pip install safety
safety check -r requirements.txt
```

## License

This tool is provided for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before testing any systems.

## Contact

For security-related questions:
- Email: your.email@example.com
- GitHub Issues: Use the "Security" flag (for non-sensitive issues only)
