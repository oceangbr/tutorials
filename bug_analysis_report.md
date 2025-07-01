# Bug Analysis Report

## Summary
This report documents 3 critical bugs identified in the codebase, including SQL injection vulnerabilities, resource leaks, and unsafe exception handling. Each bug is analyzed with its potential impact and provided with a secure fix.

## Bug #1: SQL Injection Vulnerability
**Location:** `software-security/sql-injection-samples/src/main/java/com/baeldung/examples/security/sql/AccountDAO.java:54`  
**Severity:** Critical  
**Type:** Security Vulnerability

### Description
The `unsafeFindAccountsByCustomerId` method constructs SQL queries using string concatenation, making it vulnerable to SQL injection attacks.

```java
String sql = "select " + "customer_id,acc_number,branch_id,balance from Accounts where customer_id = '" + customerId + "'";
```

### Impact
- Attackers can inject malicious SQL code through the `customerId` parameter
- Potential data breach, data manipulation, or complete database compromise
- Example attack: `'; DROP TABLE Accounts; --`

### Fix Applied
Replace string concatenation with parameterized PreparedStatement to prevent SQL injection.

## Bug #2: Resource Leak - FileInputStream Not Closed
**Location:** `spring-mvc-java/src/main/java/com/baeldung/excel/ExcelPOIHelper.java:33`  
**Severity:** High  
**Type:** Resource Leak

### Description
The `readExcel` method creates a FileInputStream but doesn't ensure it's properly closed in all execution paths.

```java
FileInputStream fis = new FileInputStream(new File(fileLocation));
```

### Impact
- File handles remain open, leading to resource exhaustion
- Memory leaks in long-running applications
- Potential "too many open files" errors under load

### Fix Applied
Implement try-with-resources pattern to ensure automatic closure of FileInputStream.

## Bug #3: Empty Catch Block Swallowing Exceptions
**Location:** `core-java-modules/core-java-exceptions/src/main/java/com/baeldung/exceptions/exceptionhandling/Exceptions.java:178`  
**Severity:** Medium  
**Type:** Logic Error

### Description
The method contains an empty catch block that silently swallows exceptions without any handling.

```java
} catch (Exception e) {} // <== catch and swallow
```

### Impact
- Silent failures that are difficult to debug
- Unexpected behavior without error indication
- Production issues that are hard to diagnose

### Fix Applied
Add proper exception logging and error handling to maintain application observability.

## Recommendations
1. Implement static analysis tools (SonarQube, SpotBugs) to catch these issues early
2. Conduct regular security code reviews focusing on input validation
3. Use try-with-resources pattern consistently for all resource management
4. Never use empty catch blocks - always log or handle exceptions appropriately
5. Implement parameterized queries as the standard practice for database access

## Additional Findings
- Static memory leak potential in `StaticFieldsDemo.java` with unbounded list growth
- Multiple instances of `equals(null)` usage in test files (semantic issue)
- Inconsistent exception handling patterns across the codebase

These fixes significantly improve the security, reliability, and maintainability of the codebase.