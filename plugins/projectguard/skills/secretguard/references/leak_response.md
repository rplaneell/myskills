# If a secret reached GitHub

Do these in order. Speed matters more than tidiness.

1. **Revoke the secret at the provider** (the service that issued it): cloud console, payment dashboard, email provider. Revoking makes the leaked copy useless.
2. **Create a new secret** and put it only in the local `.env` file (and in the CI settings page of your host if CI needs it).
3. **Check the provider's logs** for use of the old secret between the time it was pushed and the time it was revoked. If you find strange use, treat it as a breach and tell whoever must know.
4. **Remove it from the code** and commit. This does not remove it from history.
5. **Optionally clean the history.** Rewriting history (`git filter-repo` or similar) and force pushing removes it from the branch, but copies in forks, clones, caches and pull request refs may remain. This is housekeeping, not protection: step 1 is the protection. Make a backup branch first and ask the owner.
6. **Find out how it happened** and add the missing layer: the hook not installed, the file not ignored, a screenshot or a document containing the key.

## What counts as a secret

API keys, access tokens, passwords, private keys (`.pem`, `.key`, `id_rsa`), database connection strings with passwords, signing secrets, cloud credentials files, session cookies copied from a browser, and `.env` files themselves. A public identifier (for example a publishable key that is meant to be in browser code) is not a secret, but check the provider's documentation before deciding.

## Never do these while testing

Do not paste a real key into a test file, a chat, a commit message or a screenshot. Generate a made up value with the same shape (for example `ghp_` followed by 36 random letters and digits) at run time.
