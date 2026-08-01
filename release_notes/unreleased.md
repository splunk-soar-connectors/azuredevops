**Unreleased**

* Encoded string path identifiers and enforced integer work-item IDs before building Azure DevOps request paths.
* Bound OAuth callbacks to a high-entropy, one-time state value.
* Required a separate single-use launch secret before disclosing a pending OAuth authorization URL.
* Prevented OAuth token responses and headers from being written to debug data.
* Added page and result limits and loop detection to user-entitlement pagination.
* Bounded individual HTTP responses and cumulative user-entitlement pagination data before retaining results.
* Documented least-privilege Personal Access Token scopes for Basic Authentication.
