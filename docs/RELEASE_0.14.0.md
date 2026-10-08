# KITT Ecosystem 0.14.0 — Structured Agent results

The supplied logs showed successful planning and a second provider request for high-risk review. Gemini returned an unescaped JSON verdict inside the outer content string and repeated the defect in both repair attempts. The architecture now removes that extra model serialization layer: Agent contract v3 carries a result object directly in content, and the host serializes it for standard OpenAI message transport.

| Component | Version | Change |
| --- | --- | --- |
| Protocol | 0.10.0 | Authoritative Agent response schema/identifiers and strict object decoder |
| Agent | 0.85.0 | Structured plans and all review/validation/completion report consumers |
| Proxy | 5.0.0 | Object-valued results, explicit version mismatch and shared schema validation |
| Assistant | 0.1.33 / runtime 0.3.0 | Compatible Agent dependency range and all Python/Rust/TypeScript locks |
| Workers / Evals / Evolution | 0.1.57 | Compatible immutable Agent/Protocol locks |
| Memory / Toolbox | 0.9.3 / 0.4.3 | Existing compatible consumers |

Planning, pre-mutation review, independent validation, adversarial review and autonomous completion share one strict result decoder. Old textual report markers and permissive JSON-fragment extraction are removed. One complete bare or JSON-fenced object is accepted. Duplicate keys, multiple decisions, trailing prose, non-finite values and non-object results are rejected. Unsupported Agent header versions are rejected before provider execution, and Agent blocks discovered incompatible Proxy versions before dispatch.

Resilient recovery remains bounded and accepts only a unique schema-valid interpretation; optional tool arguments with competing interpretations remain invalid. Tool arguments, read-only reviewers, approvals, path checks, cancellation, request attempts/deadlines and domain acceptance criteria retain their governance. WebChat still owns token limits. ContextEnvelope v1, envelope protocol v1 and standard OpenAI API interoperability remain unchanged.

The composition must be upgraded together. No legacy Agent v2 negotiation or prefixed-report fallback is provided. No YAML/XML/custom notation or new parser dependency is added. Removing redundant escaping and markers reduces serialization overhead, but no tokenizer-specific savings percentage is claimed.

## Validation

270 Agent tests passed with one skipped and 18 subtests; 209 Proxy tests passed with TypeScript checks and production build. Protocol SDK Python/TypeScript checks, SDK identifier parity and schema provenance passed. Workers/Evals/Evolution passed 33 tests; focused Assistant dependency/runtime checks passed. Critical Ruff, Agent clean-room verification and compilation passed. All Python consumer locks passed uv lock --check.

HTTP regressions preserve structured objects and quoted/whitespace content in one attempt, reject v2 before provider submission, and retain raw-quote recovery without admitting ambiguous tools. Cross-language composition checks execute the Proxy's actual TypeScript transformation and the installed Agent/Protocol Python decoders. Root clean-install CI requires that check and both generated schemas to match. A fresh authenticated Gemini session was not executed locally.

The release manifest pins every compatible component revision. Main installation resolves main once per run; the release channel uses the immutable composition.
