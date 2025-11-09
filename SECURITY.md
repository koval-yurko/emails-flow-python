# Security Guidelines

## Environment Variables and Secrets Management

This repository follows secure practices for handling sensitive information:

### ✅ What We Do Right

1. **Environment Variables**: All sensitive data (API keys, passwords, database URLs) are loaded from environment variables using `os.getenv()`
2. **Gitignore Protection**: `.env` files are properly excluded from version control
3. **Example Configuration**: `.env.example` provides a template without exposing real credentials

### 🔒 Secrets Handling

**Never commit these to version control:**
- API keys (XAI_API_KEY, LANGSMITH_API_KEY, etc.)
- Database credentials (SUPABASE_KEY, DATABASE_URL)
- Email passwords (IMAP_PASSWORD)
- AWS credentials (except for LocalStack test values)
- Any production URLs or endpoints

### 📝 Configuration Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp cdk/.env.example cdk/.env
   ```

2. Replace placeholder values with your actual credentials:
   - `your-project-id.supabase.co` → your actual Supabase URL
   - `your-imap-server.com` → your actual IMAP server
   - Fill in all empty values with your real credentials

### 🛡️ Security Checklist

Before committing code, ensure:
- [ ] No hardcoded credentials in source code
- [ ] All sensitive values use `os.getenv()`
- [ ] `.env` files are not tracked by git
- [ ] Example files contain only placeholders
- [ ] Production URLs are not exposed in examples

### 🚨 If You Find a Secret Leak

1. **Immediately** remove the secret from the code
2. Rotate/regenerate the exposed credential
3. Check git history for the secret and consider repository cleanup
4. Update this documentation if needed

### 📚 Resources

- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_credentials)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Environment Variables Best Practices](https://12factor.net/config)