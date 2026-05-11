# envault

> A CLI tool for securely storing and syncing `.env` files across machines using encrypted backends.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize envault with a backend (e.g., S3, local):**

```bash
envault init --backend s3 --bucket my-secure-bucket
```

**Push your `.env` file to an encrypted backend:**

```bash
envault push --env .env --project my-app
```

**Pull and restore your `.env` file on another machine:**

```bash
envault pull --project my-app --output .env
```

**List stored projects:**

```bash
envault list
```

**Delete a stored project:**

```bash
envault delete --project my-app
```

**Rotate the encryption key for a stored project:**

```bash
envault rotate --project my-app
```

Secrets are encrypted client-side before being sent to any backend. Your plaintext values never leave your machine unencrypted.

---

## Supported Backends

- Local filesystem
- AWS S3
- HashiCorp Vault *(coming soon)*

---

## Requirements

- Python 3.8+
- AWS credentials configured (if using S3 backend)

---

## License

This project is licensed under the [MIT License](LICENSE).
