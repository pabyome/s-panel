## 2026-01-31 - Trust Verification Over Comments
**Vulnerability:** Critical Path Traversal in Logs API allowing arbitrary file read/truncation.
**Learning:** The code contained comments explicitly mentioning security checks (`# Security: Validate path...`), but the implementation was entirely missing. This "comment-ware" security created a false sense of safety.
**Prevention:** Never trust code comments regarding security controls. Always verify implementation logic and enforce it with negative test cases that attempt to bypass controls.
