# Uber Eats Account Generator
Generate Uber Eats Accounts using IMAP or Hotmail Emails using Mobile Packets

## ⚠️ DISCLAIMER

This project was initially built for my personal education, as I was studying mobile requests using mitmproxy, and python requests and automation vs a bigger corporation with higher end security and a multi-step authentication process. That being said, this project is not intended to be used whatsoever as it is against Ubers TOS, and it is purely and only for educational purposes.

---

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

<h2 id="features">🚀 Features</h2>

 - Generate an email, name, and password automatically(email using gmails IMAP or given hotmail accounts user:pass format)
 - Simulate an account creation process as an Iphone user, using mitmproxy to intercept requests and responses, and python asyncio and curl_cffi to automate the process.
 - Extract the OTP from the email automatically using IMAP and BeautifulSoup.
 - Save the account details to a file.

 ### Additional Features
  - Use imap domains to generate emails
  - Automatically get OTP verification code from email
  - Proxy support to avoid ip blocks
  - Asynchronous and Session based requests
  - Spoofing Device fingerprints and data(act like a real human)
  - Logging

<h2 id="requirements">📦 Requirements</h2>

### System Requirements
- Python 3.8 or higher

### Python Dependencies
```txt
curl-cffi>=0.5.9
beautifulsoup4>=4.12.0
colorama>=0.4.6
aiofiles>=23.0.0
python-dotenv>=1.0.0
```

### Email Requirements
- IMAP-enabled email account (for OTP extraction)

<h2 id="installation">🛠️ Installation</h2>

### 1. Clone the Repository
```bash
git clone https://github.com/yubunus/Uber-Eats-Account-Generator.git
cd Uber-Eats-Account-Generator
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Configure Settings
```bash
nano config.json
```

<h2 id="configuration">⚙️ Configuration</h2>

### Basic Configuration (config.json)

```json
{
  "proxy": "http://user:pass@proxy:port",
  "proxy_enabled": false,
  "imap": {
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "server": "imap.gmail.com",
    "domain": "yourdomain.com"
  },
  "security": {
    "use_proxy": true,
    "rotate_user_agents": true,
    "randomize_timing": true
  }
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `proxy` | Proxy server URL | None |
| `proxy_enabled` | Enable proxy usage | false |
| `imap.username` | Email for OTP retrieval | Required |
| `imap.password` | Email app password | Required |
| `rate_limiting.requests_per_minute` | Max requests per minute | 10 |
| `security.randomize_timing` | Add random delays | true |

<h2 id="usage">💻 Usage</h2>

### Basic Usage

```bash
# Run the main program
python main.py

# Run with specific configuration
python main.py --config custom_config.json

# Run in debug mode
python main.py --debug
```

### Menu Options

1. **Generate using IMAP**: Generates account using your personal domain and imap email
2. **Generate using Hotmail**: Generates account using hotmail accounts from `hotmailaccs.txt` in `user:pass` format
3. **Exit**: Safely exits the program

### Data Flow

1. **Initialization**: Load config, create device fingerprint
2. **Email Signup**: Submit email to initiate process
3. **OTP Retrieval**: Monitor email for verification code
4. **OTP Submission**: Submit code to verify email
5. **Registration**: Complete remaining steps
6. **Finalization**: Save account details

<h2 id="contributing">🤝 Contributing</h2>

We welcome contributions that enhance the educational value of this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit your changes (`git commit -m 'Add educational feature'`)
4. Push to the branch (`git push origin feature/enhancement`)
5. Open a Pull Request

### Contribution Guidelines

- Focus on educational value
- Add comprehensive documentation
- Include security implications

<h2 id="license">📄 License</h2>

This project is licensed under the **MIT License with Educational Use Clause** - see the [LICENSE](LICENSE) file for details.

---

**Remember**: The purpose of understanding these vulnerabilities is to build better, more secure systems. Always use this knowledge responsibly and ethically.