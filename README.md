Part 1: ./part1.md

## Development notes:

### Found issues and solutions:
- **Users should not have access to any data except shows**

  - Usually this would be handled by an API middleman as this would all be server hosted. However instead, the user program will call an 'API' program that will perform checks and authentication such as comparing hashes.
  - Encrypted database to ensure proper security and protection against unauthorised access attempts.
