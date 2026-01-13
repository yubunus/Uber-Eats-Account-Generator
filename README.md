# Uber Eats Account Generator

Automated Uber Eats account creation using mobile API simulation with IMAP or Hotmail email verification.

by @yubunus on discord and telegram

## ⚠️ DISCLAIMER

This project was initially built for my personal education, as I was studying mobile requests using mitmproxy, and python requests and automation vs a bigger corporation with higher end security and a multi-step authentication process. That being said, this project is not intended to be used whatsoever as it is against Ubers TOS, and it is purely and only for educational purposes.

## 📋 Features

- Automated account creation via mobile API endpoints
- Two email verification methods: Gmail IMAP or Hotmail API
- Android device spoofing with realistic fingerprints
- Automatic OTP extraction from emails
- Batch account generation
- Proxy support with automatic rotation
- Auto promo code application
- Saves account credentials and tokens to JSON

## 📦 Requirements

**Python 3.8+**

Dependencies:

```
curl-cffi>=0.5.9
beautifulsoup4>=4.12.0
requests>=2.31.0
cryptography>=41.0.0
colorama>=0.4.6
aiofiles>=23.0.0
python-dotenv>=1.0.0
```

## 🛠️ Installation

```bash
git clone https://github.com/yubunus/Uber-Eats-Account-Generator.git
cd Uber-Eats-Account-Generator
pip install -r requirements.txt
```

## ⚙️ Configuration

Edit `config.json`:

```json
{
  "app_variant": "ubereats",
  "proxies_enabled": true,
  "auto_get_otp": true,
  "sleep": 3,
  "hotmail_client_key": "your_hotmail007_key_here",
  "promos": {
    "apply_promo": false,
    "promo_code": "PROMO123"
  },
  "imap": {
    "username": "youremail@gmail.com",
    "password": "your_app_password",
    "server": "imap.gmail.com",
    "domains": ["domain1.com", "domain2.com"]
  }
}
```

### Configuration Options

| Option               | Description                           | Default  |
| -------------------- | ------------------------------------- | -------- |
| `app_variant`        | "ubereats" or "postmates"             | ubereats |
| `proxies_enabled`    | Use proxies from proxies.txt          | false    |
| `auto_get_otp`       | Auto-extract OTP vs manual entry      | true     |
| `sleep`              | Delay between requests (seconds)      | 3        |
| `hotmail_client_key` | API key for Hotmail verification      | -        |
| `promos.apply_promo` | Apply promo code to new accounts      | false    |
| `promos.promo_code`  | Promo code to apply                   | -        |
| `imap.username`      | Gmail for receiving OTPs              | required |
| `imap.password`      | Gmail app password                    | required |
| `imap.domains`       | Catchall domains for email generation | required |

### Proxy Setup

Create `proxies.txt` (one per line):

```
192.168.1.1:8080
user:pass:192.168.1.2:8080
user:pass@192.168.1.3:8080
```

### Hotmail Setup

For Hotmail verification, create `hotmail_accounts.txt` (format: `email:password:token:uuid`):

```
user@hotmail.com:password:token123:uuid-here
```

Get accounts from providers like [hotmail007.com](https://hotmail007.com/) and add your client key to `config.json`.

## 💻 Usage

Run the main script:

```bash
python main.py
```

You'll be prompted to:

1. Choose account type (IMAP catchall or Hotmail)
2. Enter number of accounts to generate

Accounts are processed in batches of 20 and saved to `genned/` directory.

### Output Files

- `genned/genned_accounts.json` - Account info (email, device, location)
- `genned/genned_accounts_production.json` - Full credentials (tokens, cookies)
- `genned/postmates_genned.json` - Postmates accounts (if using postmates variant)

## 🔍 How It Works

1. **Device Initialization**: Generates realistic Android device profile with 100+ unique IDs
2. **Session Setup**: Three-step device upsert process to register with Uber's backend
3. **Email Signup**: Submits email address to initiate account creation
4. **OTP Verification**: Automatically extracts 4-digit code from email
5. **Account Completion**: Submits name, accepts terms, exchanges auth codes
6. **Token Exchange**: OAuth PKCE flow with ES256 signing
7. **Finalization**: Sets cookies and optionally applies promo codes

## 📄 License

MIT License - Educational use only.

---

**Note**: This tool demonstrates security research into mobile API authentication. Understanding these mechanisms helps build better security systems. Use responsibly and ethically.
