# vuln-checker

[![PyPI version](https://img.shields.io/pypi/v/vuln-checker?color=brightgreen)](https://pypi.org/project/vuln-checker/)
[![Python version](https://img.shields.io/pypi/pyversions/vuln-checker)](https://pypi.org/project/vuln-checker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/skm248/vuln-checker?style=social)](https://github.com/skm248/vuln-checker/stargazers)

> ✨ A CLI tool to search CVEs from the NVD API based on product/version (CPE lookup).

---

## Features

- 🎯 Interactive mode to resolve multiple CPE matches
- 🔍 Filter CVEs by severity (LOW, MEDIUM, HIGH, CRITICAL)
- 💾 Export results in JSON, CSV, or HTML formats
- 🌐 Includes hyperlinks for CVE IDs in JSON, CSV, and HTML outputs
- 📋 Batch processing with CSV input or command-line product/version pairs
- ⚡ Requires NVD API key for enhanced access (rate limits apply)
- 🚀 Supports pagination for comprehensive CVE retrieval

---

## Installation

**Install via pip:**

```bash
pip install vuln-checker
```

**Or from GitHub:**

```bash
git clone https://github.com/skm248/vuln-checker.git
pip install -r requirements.txt
cd vuln-checker
pip install .
```

#### Usage
- **Prerequisites:**
      1.    Obtain an NVD API key from https://nvd.nist.gov/developers/request-an-api-key and set it as an environment variable NVD_API_KEY or replace the placeholder in the script. Follow these steps to request a key: 
            •	Open your preferred web browser and navigate to https://nvd.nist.gov/developers/request-an-api-key
            •     On the NVD - Request an API Key page, complete the following fields: 
      2.	Organization Name: Enter the name of your organization.
      3.	Email Address: Provide a valid business email address.
      4.	Organization Type: Select the type that best represents your organization from the dropdown menu.
            •	Carefully read and understand the NVD - Terms of Use section.
            •	Scroll to the bottom of the Terms of Use and check the "I agree to the Terms of Use" checkbox to accept the agreement.
            •	Click the submit button to send your request.
            •	Check your email (including spam/junk folders) for a message from NVD containing a single-use activation hyperlink. This email is sent to the address provided.
            •	Click the hyperlink within seven days to activate and view your API key. If not activated within this period, you must submit a new request.

- Set the `NVD_API_KEY` environment variable using one of the following methods based on your operating system:

#### Windows (Command Prompt)
- **Temporary (Current Session):**
    1. Open Command Prompt.
    2. Run the following command, replacing `your_actual_api_key` with your NVD API key:
       ```cmd
       set NVD_API_KEY=your_actual_api_key
       ```
      • Note: The variable is unset when the Command Prompt window is closed.

- **Persistent (All Future Sessions):**
    1. Open "System Properties":
    2. Right-click 'This PC' → 'Properties' → 'Advanced system settings' → 'Environment Variables'.
    3. In the "User variables" or "System variables" section, click "New" or edit an existing NVD_API_KEY variable.
    4. Set the Variable name to NVD_API_KEY and the Variable value to your_actual_api_key.
    5. Click "OK" to save, then close all dialog boxes.
    6. Open a new Command Prompt and verify with echo %NVD_API_KEY%.
    7. Run the script in the new session.

#### Windows (PowerShell)
- **Temporary (Current Session):**
      1. Open PowerShell.
      2. Run the following command, replacing your_actual_api_key with your NVD API key:
            $env:NVD_API_KEY = "your_actual_api_key"
      3. Run the script in the same PowerShell session:
            python main.py --products "jquery:1.11.3,1.11.5" --format json
                  • Note: The variable is unset when the PowerShell session is closed.

- **Persistent (All Future Sessions):**
      1. Open PowerShell with administrative privileges.
      2. Run the following command, replacing your_actual_api_key with your NVD API key:
            [Environment]::SetEnvironmentVariable("NVD_API_KEY", "your_actual_api_key", "User")
                  • Use "Machine" instead of "User" for system-wide persistence (requires admin rights).
      3. Open a new PowerShell session and verify with $env:NVD_API_KEY.
      4. Run the script in the new session.

#### Linux/macOS (Terminal)
- **Temporary (Current Session):**
      1. Open a terminal.
      2. Run the following command, replacing your_actual_api_key with your NVD API key:
      ```bash
      export NVD_API_KEY=your_actual_api_key
      ```
      3. Run the script in the same terminal session:
      ```bash
      python main.py --products "lodash:3.5.0" --format json
      ```
            • Note: The variable is unset when the terminal session is closed.

#### Persistent (All Future Sessions):
1. Open a terminal and edit your shell configuration file:
      • For Bash: nano ~/.bashrc or nano ~/.bash_profile
      • For Zsh: nano ~/.zshrc
2. Add the following line at the end, replacing your_actual_api_key with your NVD API key:
      ```bash
      export NVD_API_KEY=your_actual_api_key
      ```
3. Save the file and exit (e.g., Ctrl+O, Enter, Ctrl+X in nano).
4. Apply the changes by running:
      ```bash
      source ~/.bashrc  # or source ~/.bash_profile or source ~/.zshrc
      ```
5. Verify with echo $NVD_API_KEY.
6. Run the script in the same or a new terminal session.
      • After setting the environment variable, run the script. If the key is not detected, the script will prompt for manual input.


#### Command-Line Options

```bash
vuln-checker –-help
```
   **Examples:**
1. Single Product via Command-Line:
      ```bash
      vuln-checker --products "jquery:1.11.3,1.11.5 lodash:3.5.0" --format html --output custom_report.html
      ```
            • Fetches CVEs for multiple products/versions provided as a comma-separated list.

2. Batch Processing with CSV: 
            • Create a products.csv file with the following format:

      products,versions
      jquery,1.11.3,1.11.5
      lodash,3.5.0

      •	Run:
            ```bash
            vuln-checker --input-csv products.csv --format csv --output output.csv
            ```
      • Processes all product/version pairs from the CSV.

3. Filter by Severity: 
      ```bash
      vuln-checker --products "jquery:1.11.3,1.11.5" --severity critical,high --format json --output output.json
      ```
      • Filters CVEs with HIGH severity only.

4.	Specify Output File: 
      ```bash
      vuln-checker --input-csv products.csv --format html --output custom_report.html
      ```
      • Saves the report to a custom file name.


#### 📦 New Features
**--version**
You can now check the current installed version of the vuln-checker tool using:

      ```bash
      vuln-checker --version
      ```
      • This fetches the version directly from the pyproject.toml file, ensuring consistency with your package metadata.

**--upgrade**
Easily upgrade to the latest version of vuln-checker from PyPI using:

      ```bash
      vuln-checker --upgrade
      ```

This command will:
1. Check the latest available version on PyPI.
2. Compare it with your currently installed version.
3. Only upgrade if a newer version is available.

To auto-confirm the upgrade (without a prompt), use the --yes flag:

      ```bash
      vuln-checker --upgrade --yes
      ```
⚠️ If you already have the latest version installed, the tool will skip the upgrade.

#### Arguments
      --input-csv INPUT_CSV         Path to CSV file with 'product' and 'version' columns
      --products PRODUCTS           Product/version mapping. Supports one or multiple products and versions. E.g., 'jquery:1.11.3,1.11.5 lodash:3.5.0,3.59'
      --severity SEVERITY           Filter by comma-separated severities (e.g. LOW,HIGH,CRITICAL)
      --format {json,csv,html}      Output format
      --output OUTPUT               Output filename (e.g. report.html, results.csv, output.json)
      --version                     Show tool version
      --upgrade                     Upgrade vuln-checker to the latest version on PyPI
      --yes                         Auto-confirm prompts like upgrade confirmation

#### Notes
1. Exactly one of --input-csv or --products must be provided.
2. Hyperlinks in CSV are formatted as Excel =HYPERLINK formulas, and in JSON as a dictionary with url and value fields.
3. The tool includes a 0.5-second delay between API requests to respect NVD rate limits.
__________________________________________________________________________________________________________________________

#### License
This project is licensed under the by Sai Krishna Meda.