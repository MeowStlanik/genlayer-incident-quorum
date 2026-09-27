# Validation — incident-quorum

The unchanged contract source passed live Bradbury schema generation on 2026-09-27. The returned ABI is in `schema.json`.

The local logic tests load this exact contract through a minimal fake GenVM, model and web adapter. They cover relevant authorization, immutable state, evidence validation and independent validator disagreement.

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

No Python packages are required. These are control-flow tests, not a full GenVM emulator or real AI-consensus trials. Source loading and ABI extraction do not prove runtime behavior or economic safety.

A published `deployment.json` proves an observed transaction with matching source. It does not assert final successful deployment. Before a submission or integration, confirm final successful initialization, inspect the on-chain code and run the README examples plus unauthorized, ambiguous and adversarial evidence cases. Consumer actions must respect finality and appeals.

This repository intentionally contains no deployment scripts or signing secrets.
