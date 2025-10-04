### Overview
Robot Framework library providing an LLM-driven testing agent. It exposes high-level keywords to describe actions and checks in natural language; the agent then translates them into Appium (real device/emulator) and other UI interactions.


### Usage (Robot Framework)
In your `.robot` file:
```robot
*** Settings ***
Library    AiHelper.AgentKeywords    llm_client=openai    llm_model=gpt-4o-mini

*** Test Cases ***
Agent Example
    Agent.Do      accept cookies
    Agent.Check   the screen correctly shows the card
```

### Notes
- Provided keywords: `Agent.Do <instruction>`, `Agent.Check <instruction>`.
- Works with real mobile devices and BrowserStack; see more details below.


## Running Tests on BrowserStack

### Prerequisites
1. BrowserStack Account
   - Sign up at browserstack.com if you don't have an account
   - Get your username and access key from BrowserStack dashboard

2. Environment Setup
   ```bash
   # Install required dependencies
   pip install -r requirements.txt
   pip install browserstack-sdk
   ```

3. Configuration
   - Create/update `browserstack.yml` in your project root
   - Configure your credentials:
     ```yaml
     userName: YOUR_USERNAME
     accessKey: YOUR_ACCESS_KEY
     ```
   - Update app path with your app's BrowserStack URL:
     ```yaml
     app: bs://YOUR_APP_ID
     ```

### Running Tests
1. Single Test Execution
   ```bash
   browserstack-sdk robot tests/atest/your_test.robot
   ```

2. Running Test Suites
   ```bash
   browserstack-sdk robot tests/atest/
   ```

3. Parallel Execution
   ```bash
   browserstack-sdk robot --variable parallel_execution:true tests/atest/
   ```

### Device Configuration
- Edit `browserstack.yml` to specify target devices:
  ```yaml
  platforms:
    - deviceName: Samsung Galaxy S21
      platformVersion: 12.0
      platformName: Android
    # Add more devices as needed
  ```

### Development Tips
1. Debug Mode
   - Set `debug: true` in browserstack.yml
   - Enable detailed logs: `consoleLogs: info`

2. Local Testing
   - For testing with local apps/servers:
     ```yaml
     browserstackLocal: true
     ```

3. Build Identification
   - Set unique build names for tracking:
     ```yaml
     buildName: "Dev Build"
     buildIdentifier: ${BUILD_NUMBER}
     ```

### Viewing Results
1. Real-time monitoring: BrowserStack dashboard
2. Test reports: Available in `log/` directory after execution
3. Session videos: Automatically recorded and available in BrowserStack dashboard

### Troubleshooting
- Check BrowserStack status page for service issues
- Verify network connectivity
- Ensure correct app URL in configuration
- Review logs in BrowserStack dashboard for detailed error messages