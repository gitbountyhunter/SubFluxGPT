"""
Create sample bug bounty data for llm.c testing.
Generates synthetic data in llm.c .bin format without requiring a database.
"""

import os
import logging
import numpy as np
import tiktoken
from pathlib import Path

logger = logging.getLogger(__name__)


# llm.c header format for GPT-2
HEADERS_INFO = {
    "gpt-2": {
        "magic": 20240520,
        "version": 1,
        "token_dtype": np.uint16,
    },
}


def write_datafile(filename, toks, model_desc="gpt-2"):
    """
    Saves token data as a .bin file, for reading in C.
    """
    assert len(toks) < 2**31, "token count too large"
    assert model_desc in ["gpt-2"], f"unknown model descriptor {model_desc}"
    info = HEADERS_INFO[model_desc]
    
    header = np.zeros(256, dtype=np.int32)
    header[0] = info["magic"]
    header[1] = info["version"]
    header[2] = len(toks)
    
    toks_np = np.array(toks, dtype=info["token_dtype"])
    num_bytes = (256 * 4) + (len(toks) * toks_np.itemsize)
    print(f"writing {len(toks):,} tokens to {filename} ({num_bytes:,} bytes) in the {model_desc} format")
    with open(filename, "wb") as f:
        f.write(header.tobytes())
        f.write(toks_np.tobytes())


def generate_sample_reports():
    """Generate sample bug bounty reports."""
    reports = [
        """Program: example.com
Report title: Reflected XSS in search parameter
Vulnerability type: Cross-Site Scripting (XSS)
Severity: Medium
Description: The search parameter is vulnerable to reflected XSS. When a user inputs malicious JavaScript, it is executed in the browser context.
Impact: Attackers can steal session cookies, redirect users, or perform actions on behalf of victims.
Remediation: Implement proper output encoding and use Content Security Policy.""",

        """Program: testapp.io
Report title: SQL Injection in user profile
Vulnerability type: SQL Injection
Severity: High
Description: The user_id parameter in the profile endpoint is vulnerable to SQL injection. Attackers can extract database contents.
Impact: Full database compromise, data exfiltration, potential authentication bypass.
Remediation: Use parameterized queries and input validation.""",

        """Program: myshop.com
Report title: IDOR in order history
Vulnerability type: Insecure Direct Object Reference (IDOR)
Severity: Medium
Description: Users can access other users' order history by incrementing the order_id parameter.
Impact: Privacy violation, unauthorized access to sensitive order information.
Remediation: Implement proper access controls and verify ownership before allowing access.""",

        """Program: api.service.com
Report title: Broken access control on admin endpoint
Vulnerability type: Broken Access Control
Severity: Critical
Description: The /admin endpoint is accessible to regular users through API calls without proper authentication.
Impact: Full administrative access, data modification, service disruption.
Remediation: Implement strong authentication and authorization checks on all admin endpoints.""",

        """Program: social.net
Report title: Stored XSS in profile bio
Vulnerability type: Cross-Site Scripting (XSS)
Severity: High
Description: The bio field in user profiles does not sanitize input, allowing stored XSS attacks.
Impact: Attackers can compromise any user who views the infected profile, leading to account takeover.
Remediation: Sanitize all user input, implement Content Security Policy, and use HTML encoding.""",

        """Program: payments.io
Report title: Server-Side Request Forgery in webhook URL
Vulnerability type: Server-Side Request Forgery (SSRF)
Severity: High
Description: The webhook URL parameter does not validate the target, allowing attackers to make requests to internal services.
Impact: Access to internal services, data exfiltration, potential RCE.
Remediation: Validate and whitelist allowed webhook URLs, use network segmentation.""",

        """Program: cloudstore.app
Report title: Sensitive data exposure in error messages
Vulnerability type: Information Disclosure
Severity: Low
Description: Error messages contain stack traces and internal paths, revealing sensitive system information.
Impact: Information leakage aids attackers in planning more sophisticated attacks.
Remediation: Implement generic error messages for production, log detailed errors server-side.""",

        """Program: auth.service.com
Report title: Weak password policy
Vulnerability type: Weak Authentication
Severity: Medium
Description: Password policy allows weak passwords and does not enforce complexity requirements.
Impact: Brute force attacks, credential stuffing, account compromise.
Remediation: Implement strong password policy, enforce complexity, rate limit login attempts.""",

        """Program: ecommerce.site
Report title: CSRF in password change
Vulnerability type: Cross-Site Request Forgery (CSRF)
Severity: Medium
Description: Password change endpoint lacks CSRF protection, allowing attackers to change passwords via malicious links.
Impact: Account takeover, unauthorized password changes.
Remediation: Implement CSRF tokens, validate Referer header, use SameSite cookies.""",

        """Program: api.devtools.com
Report title: Rate limiting bypass
Vulnerability type: Rate Limiting Bypass
Severity: Medium
Description: API rate limiting can be bypassed by rotating IP addresses or using different user agents.
Impact: API abuse, denial of service, credential stuffing.
Remediation: Implement robust rate limiting based on user identity, not just IP.""",

        """Program: chat.app
Report title: Path traversal in file upload
Vulnerability type: Path Traversal
Severity: High
Description: File upload functionality does not validate filenames, allowing path traversal attacks.
Impact: Arbitrary file read/write, potential RCE, data exfiltration.
Remediation: Validate and sanitize filenames, use secure file storage, implement access controls.""",

        """Program: dashboard.io
Report title: Subdomain takeover on forgotten subdomain
Vulnerability type: Subdomain Takeover
Severity: Medium
Description: The subdomain dev.dashboard.io points to a decommissioned Heroku app that can be claimed.
Impact: Phishing attacks, cookie theft, reputation damage.
Remediation: Monitor DNS records, remove unused subdomains, implement takeover detection.""",

        """Program: tracker.app
Report title: DOM-based XSS in search
Vulnerability type: DOM-based XSS
Severity: Medium
Description: The search functionality uses user input to dynamically update the DOM without sanitization.
Impact: Session hijacking, credential theft, malicious script execution.
Remediation: Sanitize input before using in DOM operations, use safe DOM APIs.""",

        """Program: api.gateway.com
Report title: Authentication bypass via JWT manipulation
Vulnerability type: Authentication Bypass
Severity: Critical
Description: JWT tokens are not properly validated, allowing attackers to manipulate claims and bypass authentication.
Impact: Full system compromise, unauthorized access to all resources.
Remediation: Implement proper JWT validation, verify signatures, use strong secret keys.""",

        """Program: storage.cloud
Report title: Unrestricted file upload
Vulnerability type: Unrestricted File Upload
Severity: High
Description: File upload functionality does not restrict file types, allowing upload of executable files.
Impact: RCE, malware distribution, system compromise.
Remediation: Restrict file types, validate content, store files outside web root.""",

        """Program: social.graph
Report title: IDOR in message viewing
Vulnerability type: Insecure Direct Object Reference (IDOR)
Severity: Medium
Description: Users can view other users' private messages by incrementing the message_id parameter.
Impact: Privacy violation, unauthorized access to private communications.
Remediation: Implement proper access controls, verify message ownership.""",

        """Program: payment.gateway
Report title: Payment manipulation via parameter tampering
Vulnerability type: Business Logic Flaw
Severity: High
Description: Payment amount can be manipulated in the request, allowing purchase for $0.01.
Impact: Financial loss, fraud, business impact.
Remediation: Validate all payment parameters server-side, implement server-side price calculation.""",

        """Program: mobile.api
Report Title: Hardcoded API keys in mobile app
Vulnerability type: Hardcoded Credentials
Severity: High
Description: API keys are hardcoded in the mobile application binary and can be extracted.
Impact: Unauthorized API access, data exfiltration, service abuse.
Remediation: Use dynamic key generation, implement certificate pinning, rotate keys regularly.""",

        """Program: web.service
Report title: Open redirect via URL parameter
Vulnerability type: Open Redirect
Severity: Low
Description: The redirect_url parameter does not validate the target, allowing open redirect attacks.
Impact: Phishing attacks, credential theft, reputation damage.
Remediation: Validate redirect URLs, whitelist allowed domains, use relative redirects.""",

        """Program: analytics.dashboard
Report title: Improper access control on export feature
Vulnerability type: Broken Access Control
Severity: Medium
Description: Data export feature allows exporting all data without proper authorization checks.
Impact: Data exfiltration, privacy violation, compliance issues.
Remediation: Implement proper authorization checks, limit export scope, audit export activity."""
    ]
    
    return reports


def main():
    """Create sample llm.c data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create sample bug bounty data for llm.c")
    parser.add_argument('--output_dir', type=str, default='data/llmc', help='Output directory')
    parser.add_argument('--repeat', type=int, default=10, help='Repeat reports N times for more data')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create output directory
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        args.output_dir
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize GPT-2 tokenizer
    enc = tiktoken.get_encoding("gpt2")
    eot = enc.eot_token  # End of text token
    
    # Generate sample reports
    reports = generate_sample_reports()
    
    # Repeat reports for more data
    reports = reports * args.repeat
    
    logger.info(f"Generated {len(reports)} sample reports")
    
    # Tokenize
    tokens = []
    for i, report in enumerate(reports):
        tokens.append(eot)
        encoded = enc.encode_ordinary(report + "\n\n")
        tokens.extend(encoded)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Tokenized {i + 1}/{len(reports)} reports")
    
    logger.info(f"Total tokens: {len(tokens):,}")
    
    # Split into train/val
    val_split = 0.1
    split_idx = int(len(tokens) * (1 - val_split))
    
    val_tokens = tokens[:split_idx]
    train_tokens = tokens[split_idx:]
    
    logger.info(f"Train tokens: {len(train_tokens):,}")
    logger.info(f"Val tokens: {len(val_tokens):,}")
    
    # Save to files
    val_filename = os.path.join(output_dir, "bugbounty_val.bin")
    train_filename = os.path.join(output_dir, "bugbounty_train.bin")
    
    write_datafile(val_filename, val_tokens, model_desc="gpt-2")
    write_datafile(train_filename, train_tokens, model_desc="gpt-2")
    
    logger.info(f"Sample data created in {output_dir}")
    print(f"\nSample data created:")
    print(f"  Train file: {train_filename}")
    print(f"  Val file: {val_filename}")
    print(f"  Train tokens: {len(train_tokens):,}")
    print(f"  Val tokens: {len(val_tokens):,}")


if __name__ == '__main__':
    main()
