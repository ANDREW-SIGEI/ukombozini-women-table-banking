# Troubleshooting Flask Connection Issues

## "Connection Refused" Error

If you're seeing "Connection Refused" errors when trying to access the Flask application, try the following solutions:

### Solution 1: Use netstat to Check Port Usage

Check if any service is already using the port:

```bash
sudo netstat -tuln | grep 5000
```

If the port is in use, you can:
1. Stop the service using that port, or
2. Use a different port for your Flask application

### Solution 2: Start Flask with Different Network Configuration

Try running the Flask app with these different configurations:

```bash
# Option 1: Use loopback interface only
python run.py
```

```bash
# Option 2: Use a different port
PORT=8080 python run.py
```

```bash
# Option 3: Modify run.py to listen on all interfaces
# Edit run.py to include:
# app.run(host='0.0.0.0', port=port, debug=True)
```

### Solution 3: Check Firewall Settings

Your firewall might be blocking connections to the Flask development server:

```bash
# Check if UFW is enabled
sudo ufw status

# If enabled, allow connections to your Flask port
sudo ufw allow 5000/tcp
# or
sudo ufw allow 8080/tcp
```

### Solution 4: Access via the Correct URL

Make sure you're using the correct URL to access the application:

- From the same machine: http://localhost:5000/ or http://127.0.0.1:5000/
- From another machine on the network: http://your_ip_address:5000/

### Solution 5: Try a Different Browser

Sometimes browser caching or extensions can cause connection issues. Try:
- A different browser
- Incognito/private browsing mode
- Clearing your browser cache

### Solution 6: Check Network Proxy Settings

If you're using a proxy, make sure it's configured correctly or try disabling it temporarily.

## If All Else Fails

You might try completely restarting your computer, which can resolve persistent network issues.

If you're in a restricted network environment (like a corporate network), contact your network administrator as they might have specific policies in place that are blocking your connections. 