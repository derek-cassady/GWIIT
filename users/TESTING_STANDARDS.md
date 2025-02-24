# Testing Standards

## Overview
This document outlines the standardized approach for writing and maintaining tests in this project. These standards ensure consistency, readability, and reliability across all test cases.

---
## Emoji Usage in Test Output
- **⏳ (Hourglass)** → Before executing an important query or operation.
- **✅ (Green Check)** → When a test case successfully meets expectations.
- **❌ (Red X)** → When an assertion fails (unexpected result).
- **🔴 (Red Dot)** → When testing an expected failure case (intentional error check).

### **Emoji Rules:**
- Emojis should appear **inside `print()` statements** for easy visual confirmation on testing.
- Assertions should include **❌** only when a test fails.
- Emojis are not used inside python comments or docstrings.
    ```python
    # ❌ Not cool bro
    ```
---
## Testing Both Success & Failure Cases
- Every test must include **both**:
  - A **passing case** (expected successful behavior).
  - A **failure case** (ensuring proper error handling).

---
## Print Statements for Test Start/End Announcements
- Each test must **clearly announce its start and end** using `print()`.
- Example format:
  ```python
  print("\n⏳ Starting test_user_manager_create_user_success...")
  print("✅ Finished test_user_manager_create_user_success...")
  ```

---
## Consistent Test Naming Convention
- Test method names follow this format:
  ```
  test_<class_name>_<method_name>_<expected_behavior>()
  ```
- Example:
  ```python
  def test_user_manager_create_user_success(self):
  ```
- Ensures clarity in test discovery and debugging.

---
## Standardized Assertions
- **Count Assertions:**
  ```python
  self.assertEqual(queryset.count(), expected_count, "❌ <message>")
  ```
- **Inclusion Assertions:**
  ```python
  self.assertIn(expected_user, queryset, "❌ <message>")
  ```
- **Failure Assertions:**
  ```python
  with self.assertRaises(ExpectedException):
      function_that_should_fail()
  ```

---
## Grouping Related Assertions Together
- Keep assertions structured and logical:
  ```python
  # Check count first
  self.assertEqual(active_users.count(), 3, "❌ Expected exactly 3 active users.")

  # Then check user inclusion
  self.assertIn(self.user1, active_users, "❌ User1 should be in active users.")
  ```

---
## Keep Test Data Creation Inside `setUp()`
- Avoid modifying test data inside individual test methods unless absolutely necessary.
- If a test needs modifications, use **`.refresh_from_db()`** instead of creating new objects.
- Ensures all tests start from a **clean, reproducible state**.

## Preparation Method Comments

### **Standard Format for Preparation Method Comments**
Preparation methods are responsible for setting up the test environment before test execution. Since these methods do not directly test functionality but instead establish **consistent preconditions**, their comments follow a slightly different structure than standard test cases.

The **preparation method comment format** ensures clarity by defining:
- **Why the setup is needed** rather than focusing on assertions.
- **What environment is being created** to ensure proper test execution.
- **What guarantees are provided** to the test cases that rely on them.

The comment structure consists of the following sections:
---
### **Comment Structure**

Prepares ```<test environment details>``` before each test method runs.

**Purpose:**
- Explains why the preparation method is necessary.
- Describes what relationships and data structures are being set up.
- Provides context for how this setup benefits test reliability.

**Expected Behavior:**
- Defines what a successful setup looks like.
- Lists key properties of the test data (e.g., correct relationships, valid attributes).
- Outlines constraints such as expected variations in data.

**Data Setup:**
1. **[Data Category]** (Stored in `[database]`)
    - Describes what entities are created and how they are linked.
    - Highlights any attributes or variations important to testing.
2. **[Data Category]** (Stored in `[database]`)
    - Continues outlining setup details for different entities.
3. **[Data Category]** (Stored in `[database]`)
    - Lists key setup components relevant to the test cases.

Guarantees that ```<expected outcomes>``` are in place before test execution.

---

## Testing Method Comments

### **Standard Format for Testing Method Comments**
Testing methods verify specific functionality within the system. To ensure clarity and maintainability, **each test method should be well-documented with a structured comment** explaining its purpose, expected behavior, and test cases.

The **testing method comment format** ensures:
- **A clear purpose statement** that describes what functionality is being tested.
- **A breakdown of expected behavior** to define success and failure conditions.
- **A structured list of test cases** that outline what specific conditions are being verified.

The comment structure consists of the following sections:

---

### **Comment Structure**

Tests ```<method_name>``` to ensure ```<primary function>```.

**Purpose:**
- Describes what functionality the test verifies.
- Explains why this test is necessary.
- Highlights any constraints or assumptions.

**Expected Behavior:**
- Defines what success looks like for the test.
- Outlines failure conditions that should be handled.
- Lists key attributes or outputs that should be verified.

**Test Cases:**
1. **[Test Case Name]** - Briefly describe what it verifies.
2. **[Test Case Name]** - Describe an edge case scenario.
3. **[Test Case Name]** - Explain failure handling conditions.

Guarantees that ```<method_name>``` functions correctly in ```<specific scenario, like multi-database>```.

---

### **Why This Standard Matters**
- **Ensures test cases are easy to understand and maintain.**  

- **Clearly separates test purpose from assertions, reducing redundancy.**  

- **Prevents ambiguity in what the test is verifying.**  

- **Creates a structured approach that future contributors can easily follow.**  

By following this structured **testing method comment format**, we ensure **consistent, maintainable, and well-documented test cases** across the project.

## Conclusion
Following these standards ensures that our test suite remains **consistent, maintainable, and easy to debug**. All new tests must adhere to these guidelines.

---
## Assertions in Django Testing

### What Are Assertions?

Assertions are conditions used in test cases to validate expected behavior. If an assertion fails, Django marks the test as a failure. Assertions ensure that our code is functioning correctly and prevent regressions in future updates.

### Why Are Assertions Needed?

- **Validate Expected Behavior –** Ensures that a function, query, or API returns the expected result.

- **Prevent Bugs –** Identifies unexpected behavior early in development.

- **Improve Debugging –** Failed assertions provide clear feedback about what went wrong.

### How Django Uses Assertions

Django’s test framework extends Python’s unittest module, which provides several built-in assertions, including:

- **self.assertEqual(a, b) –** Checks if a and b are equal.

- **self.assertNotEqual(a, b) –** Checks if a and b are not equal.

- **self.assertTrue(condition) –** Ensures the condition is True.

- **self.assertFalse(condition) –** Ensures the condition is False.

- **self.assertRaises(ExpectedException) –** Ensures that the specified exception is raised.

By following standardized assertion practices, we ensure that test cases are reliable, easy to understand, and maintainable.

### Running Tests

To run the test suite, use the following command:

```python
python manage.py test
```
### This command will:

- Discover all test cases in the project.

- Execute them in an isolated environment.

- Display the results, including passed, failed, and errored tests.

### To run a specific test file:
```python
python manage.py test <app_name>.tests
```
### To run a specific test case:
```python
python manage.py test <app_name>.tests.<TestClassName>
```
### To increase verbosity for better debugging:
```python
python manage.py test --verbosity 2
```