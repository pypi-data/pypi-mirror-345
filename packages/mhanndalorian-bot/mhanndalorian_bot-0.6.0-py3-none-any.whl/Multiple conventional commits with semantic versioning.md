feat(auth): add JWT authentication strategy

This commit introduces JWT-based authentication for the API.
It includes token generation, validation, and middleware for
secured endpoints.

fix(auth): resolve bug with password hashing

Fixed an issue where passwords shorter than 8 characters
were causing the hashing function to fail unexpectedly.

refactor(api): improve database query performance

Optimized the queries for fetching user data, reducing
response times by approximately 30%.

BREAKING CHANGE: Updated API endpoints for user login

- The `/login` endpoint now requires an `api_key` header.
- All API consumers must update their request headers to avoid
  401 Unauthorized errors.

Closes #23, #45


### **Tips for Writing Multiple Messages**
1. **Separate Concerns**: Split related changes into individual sections (e.g., `feat`, `fix`, `refactor`) for readability.
2. **Use Imperative Mood**: Write summaries like commands (e.g., “Add X,” “Fix Y”) rather than past or future tense.
3. **Keep Summaries Short**: The first line should be ≤ 50 characters. Additional details can go in the body.
4. **Relate Fixes to Issues**: Use keywords like `Closes` or `Fixes` to tie changes to specific issues or tickets in your tracker.
5. **Mention Breaking Changes**: Use `BREAKING CHANGE:` in the footer for any major changes.

By following this structure, you'll produce a well-organized and professional commit history that is easy to understand and manage.
