# Uber Eats Account Generator

Generate Uber Eats Accounts using IMAP or Hotmail Emails using Mobile Packets
by @yubunus on discord and telegram - nuunuu1923@gmail.com

## ⚠️ DISCLAIMER

This project was initially built for my personal education, as I was studying mobile requests using mitmproxy, and python requests and automation vs a bigger corporation with higher end security and a multi-step authentication process. That being said, this project is not intended to be used whatsoever as it is against Ubers TOS, and it is purely and only for educational purposes.

## IMPORTANT

Due to security and abuse prevention concerns, the modern updated version of this code which produces fully undetectable accounts is not available to be open sourced for free, as well as other custom variations with more features. If you are interested in purchasing a custom variation, please contact me on discord or telegram.

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Hotmail Setup](#hotmail)
- [License](#license)

<h2 id="features">🚀 Features</h2>

- Generate accounts automatically using Gmail IMAP or Hotmail accounts
- Batch account generation with progress tracking
- Multi-domain support with random domain selection
- Proxy support with multiple formats (ip:port, user:pass:ip:port, user:pass@ip:port)
- Proxy cycling or random selection
- Simulate Android or iOS device requests using mitmproxy intercepted packets
- Extract OTP from emails automatically using IMAP and BeautifulSoup
- Spoofed device fingerprints and data
- Optional data persistence (cookies, device data, device info)
- Automatic promo code application to new accounts

<h2 id="requirements">📦 Requirements</h2>

### System Requirements

- Python 3.8 or higher

### Python Dependencies

```txt
curl-cffi>=0.5.9
beautifulsoup4>=4.12.0
colorama>=0.4.6
```

### Email Requirements

- IMAP-enabled email account (Gmail with app password or Hotmail)

<h2 id="installation">🛠️ Installation</h2>

### 1. Clone the Repository

```bash
git clone https://github.com/yubunus/Uber-Eats-Account-Generator.git
cd Uber-Eats-Account-Generator
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Settings

```bash
nano config.json
```

<h2 id="configuration">⚙️ Configuration</h2>

### config.json

```json
{
  "device": "android",
  "proxy_enabled": false,
  "cycle_proxies": false,
  "auto_get_otp": true,
  "save_info": {
    "cookies": false,
    "device_data": false,
    "device_info": true
  },
  "promos": {
    "auto_apply": false,
    "promo_code": "promo_code_here"
  },
  "imap": {
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "server": "imap.gmail.com",
    "domains": ["yourdomain.com", "anotherdomain.com"]
  }
}
```

### Configuration Options

| Option                  | Description                                | Default        |
| ----------------------- | ------------------------------------------ | -------------- |
| `device`                | Device type to simulate (android/ios)      | android        |
| `proxy_enabled`         | Enable proxy usage                         | false          |
| `cycle_proxies`         | Cycle through proxies vs random selection  | false          |
| `auto_get_otp`          | Auto get OTP from emails, otherwise manual | true           |
| `save_info.cookies`     | Save account cookies to file               | false          |
| `save_info.device_data` | Save device data to file                   | false          |
| `save_info.device_info` | Save device info to file                   | true           |
| `promos.auto_apply`     | Automatically apply promo code             | false          |
| `promos.promo_code`     | Promo code to apply to new accounts        | Required\*     |
| `imap.username`         | Email for OTP retrieval                    | Required       |
| `imap.password`         | Email app password                         | Required       |
| `imap.server`           | IMAP server                                | imap.gmail.com |
| `imap.domains`          | List of domains for account generation     | Required       |

\*Required only if `promos.auto_apply` is enabled

### Proxy Setup

Create `proxies.txt` in the project directory with one proxy per line:

```
192.168.1.1:8080
user:pass:192.168.1.2:8080
user:pass@192.168.1.3:8080
```

Supported formats: `ip:port`, `user:pass:ip:port`, `user:pass@ip:port`

<h2 id="usage">💻 Usage</h2>

### Basic Usage

```bash
python cli.py
```

### Menu Options

1. **Generate using IMAP**: Generates accounts using your Gmail IMAP

   - Asks how many accounts to generate
   - Randomly selects domain from your configured domains list
   - Shows success/failure summary

2. **Generate using Hotmail**: Generates accounts using Hotmail from `hotmailaccs.txt`

   - Shows available Hotmail accounts
   - Asks how many to use (0 for all)
   - Shows success/failure summary

3. **Exit**: Safely exits the program

<h2 id="hotmail">Using Hotmail</h2>

1. **Purchase Hotmail Accounts**
   Buy Hotmail accounts from a provider such as [hotmail007.com](https://hotmail007.com/).

2. **Prepare `hotmailaccs.txt`**
   Create a file named `hotmailaccs.txt` in the project directory:

   ```
   user1@hotmail.com:password1
   user2@hotmail.com:password2
   ```

3. **Run the Program**
   ```bash
   python cli.py
   ```
   Select **Generate using Hotmail** from the menu.

<h2 id="license">📄 License</h2>

This project is licensed under the **MIT License with Educational Use Clause** - see the [LICENSE](LICENSE) file for details.

---

**Remember**: The purpose of understanding these vulnerabilities is to build better, more secure systems. Always use this knowledge responsibly and ethically.
