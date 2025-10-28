# Global Browser Console Capture - Runbook

## Overview

This setup provides comprehensive browser console capture across **Chrome, Edge, and Firefox** for any URL/port. It includes:

- **Manual debugging** with VS Code debugger
- **Automated testing** with Playwright
- **Runtime telemetry** with console tap server
- **Cross-browser compatibility** without hardcoded URLs

## Quick Start

### 1. Initial Setup

```bash
# Install dependencies
npm run setup

# Or manually:
npm install
npm run install:browsers:deps
```

### 2. Manual Debugging (Any URL)

1. Open VS Code
2. Go to **Run and Debug** (Ctrl+Shift+D)
3. Select **"Launch All (Chrome + Edge + Firefox)"**
4. Enter target URL when prompted (e.g., `http://localhost:8018`)
5. Console errors will appear in VS Code Debug Console

### 3. Automated Testing (CI Gate)

```bash
# Test against default URL (localhost:3000)
npm run test:pw

# Test against specific URL
PW_BASE_URL=http://localhost:8018 npm run test:pw

# Test specific browser
npm run test:pw:chrome
npm run test:pw:firefox
npm run test:pw:webkit

# Interactive testing
npm run test:pw:ui
```

### 4. Runtime Telemetry (Any Browser)

```bash
# Start console tap server
npm run dev:tap

# In your app, include the bootstrap script:
# <script src="bootstrap_console_tap.js"></script>
```

## Detailed Usage

### VS Code Debug Configurations

#### Available Configurations:
- **Chrome: Launch & Attach (CDP)** - Full Chrome debugging
- **Edge: Launch & Attach (CDP)** - Full Edge debugging  
- **Chrome: Attach to Existing** - Attach to running Chrome
- **Firefox: Launch** - Requires Firefox Debugger extension
- **Launch All** - Launches Chrome + Edge + Firefox simultaneously

#### Firefox Setup:
1. Install VS Code extension: **Debugger for Firefox** (`firefox-devtools.vscode-firefox-debug`)
2. If not installed, use Playwright for Firefox coverage

### Playwright Testing

#### Configuration:
- **Base URL**: Set via `PW_BASE_URL` environment variable
- **Browsers**: Chromium, Firefox, WebKit
- **Reports**: HTML, JSON, and console output
- **Screenshots**: On failure
- **Videos**: Retained on failure

#### Test Files:
- `tests/no-console-errors.spec.ts` - Main console error detection
- `tests/global-setup.ts` - Test suite initialization
- `tests/global-teardown.ts` - Test suite cleanup

#### Available Commands:
```bash
# Basic testing
npm run test:pw                    # All browsers
npm run test:pw:chrome             # Chrome only
npm run test:pw:firefox            # Firefox only
npm run test:pw:webkit             # Safari only

# Interactive testing
npm run test:pw:ui                 # Playwright UI
npm run test:pw:headed             # Visible browser
npm run test:pw:debug              # Debug mode

# Custom URLs
PW_BASE_URL=https://staging.example.com npm run test:pw
```

### Console Tap Server

#### Features:
- **Real-time logging** of console errors
- **Batch processing** for efficiency
- **Cross-browser support** (Chrome, Edge, Firefox, Safari)
- **Health monitoring** endpoints
- **Statistics tracking**

#### Server Endpoints:
- `POST /__console_tap__` - Receive console messages
- `GET /__console_tap__/health` - Health check
- `GET /__console_tap__/stats` - Usage statistics

#### Client Integration:
```html
<!-- Include in your app -->
<script src="bootstrap_console_tap.js"></script>

<!-- Or configure manually -->
<script>
  window.__CONSOLE_TAP_PORT__ = 5055;
  window.__CONSOLE_TAP_URL__ = 'http://localhost:5055/__console_tap__';
  window.__CONSOLE_TAP_ENABLED__ = true;
</script>
```

#### Server Commands:
```bash
npm run dev:tap                    # Start server
npm run dev:tap:watch              # Start with auto-reload
npm run build:tap                  # Build TypeScript
npm run start:tap                  # Run built server
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PW_BASE_URL` | `http://localhost:3000` | Playwright test base URL |
| `CONSOLE_TAP_PORT` | `5055` | Console tap server port |
| `CONSOLE_TAP_HOST` | `localhost` | Console tap server host |

## Troubleshooting

### VS Code Debugging Issues

**Problem**: Firefox debugging not working
**Solution**: Install "Debugger for Firefox" extension or use Playwright

**Problem**: Chrome/Edge not launching
**Solution**: Check if ports 9222/9223 are available

**Problem**: Source maps not working
**Solution**: Verify `webRoot` and `sourceMapPathOverrides` in launch.json

### Playwright Issues

**Problem**: Browsers not installed
**Solution**: Run `npm run install:browsers:deps`

**Problem**: Tests timing out
**Solution**: Increase timeout in `playwright.config.ts`

**Problem**: Network errors
**Solution**: Check if target URL is accessible

### Console Tap Issues

**Problem**: Server not receiving messages
**Solution**: Check CORS settings and endpoint URL

**Problem**: Too many messages
**Solution**: Adjust `batchSize` and `flushInterval` in bootstrap script

**Problem**: Performance impact
**Solution**: Disable tap in production: `window.__CONSOLE_TAP_ENABLED__ = false`

## File Structure

```
├── .vscode/
│   └── launch.json                 # VS Code debug configurations
├── dev/
│   └── console_tap_server.ts       # Telemetry server
├── tests/
│   ├── no-console-errors.spec.ts   # Main test file
│   ├── global-setup.ts            # Test setup
│   └── global-teardown.ts          # Test cleanup
├── bootstrap_console_tap.js       # Client-side tap script
├── playwright.config.ts            # Playwright configuration
├── package.json                   # Dependencies and scripts
└── DEV_NOTES.md                   # This file
```

## Best Practices

### Development Workflow:
1. Start console tap server: `npm run dev:tap`
2. Include bootstrap script in your app
3. Use VS Code debugging for manual testing
4. Run Playwright tests before commits
5. Monitor console tap logs for runtime issues

### CI/CD Integration:
```yaml
# Example GitHub Actions
- name: Run Playwright Tests
  run: |
    export PW_BASE_URL=${{ env.APP_URL }}
    npm run test:pw
```

### Production Considerations:
- Disable console tap in production
- Use environment-specific base URLs
- Monitor Playwright test results
- Set up alerts for console errors

## Support

For issues or questions:
1. Check this runbook first
2. Review console output for errors
3. Verify all dependencies are installed
4. Test with different browsers/URLs
5. Check VS Code extension compatibility

---

**Last Updated**: $(date)
**Version**: 1.0.0
