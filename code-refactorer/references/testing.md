# Testing Patterns per SOLID Principle

Concise testing patterns referenced from `SKILL.md`.

| Principle | Testing Pattern |
|-----------|-----------------|
| **SRP** | Split tests by responsibility. One test class per extracted service (e.g., `UserCreationTest`, `EmailSendingTest`). Mock collaborators so each test exercises one reason to change. |
| **OCP** | Add new test classes for new extensions; never modify existing tests. A new discount type gets its own test file; existing discount tests remain untouched and still pass. |
| **LSP** | Substitute the subtype in base-type tests. Existing `Rectangle` tests should pass unchanged when fed a `Square`; if they fail, the inheritance violates LSP. |
| **ISP** | Test implementing classes only against the interfaces they actually use. `Robot` tests reference `Workable`, never `Eatable`/`Sleepable`. |
| **DIP** | Inject test doubles. `OrderService` tests use `MockEmailService`; verify `placeOrder` calls `send()` without touching SMTP or the real provider. |