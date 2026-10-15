# How to Run and Test Memorix Application

## ⚠️ Important Note About PowerShell Timeout
When you run `python main.py` in PowerShell, the interface will appear to "hang" or timeout after 2 minutes. **This is normal behavior** - the PowerShell interface is waiting for the process to complete, but the server is actually running correctly in the background.

## ✅ Correct Way to Run the Application

### Method 1: Run in Background (Recommended for Testing)
1. Open PowerShell in the Track 2 directory:
   ```powershell
   cd F:\hackathon\Track 2
   ```

2. Start the server:
   ```powershell
   python main.py
   ```

3. **Do not wait for the "Uvicorn running" message to disappear** - the server is running even though PowerShell appears stuck.

4. Open a **NEW PowerShell window** (don't close the first one) and test the endpoints:
   ```powershell
   curl http://localhost:8000/api/health
   ```

### Method 2: Run in Separate Process (Best for Demos)
1. Open PowerShell in the Track 2 directory:
   ```powershell
   cd F:\hackathon\Track 2
   ```

2. Start the server in a background process:
   ```powershell
   Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
   ```

3. Wait 3 seconds, then test:
   ```powershell
   Start-Sleep -seconds 3
   curl http://localhost:8000/api/health
   ```

4. To stop the server when done:
   ```powershell
   Get-Process python | Where-Object { $_.Path -like "*python*" } | Stop-Process
   ```

## 🧪 Quick Test Sequence
Once the server is running (using either method above), test in this order:

1. **Health Check**:
   ```powershell
   curl http://localhost:8000/api/health
   ```
   Expected: `{"status":"healthy","falkor_fallback":true,...}`

2. **Load Test Data**:
   ```powershell
   curl -X POST http://localhost:8000/api/seed/MULTI-SESSION-01
   ```
   Expected: `{"success":true,"scenario_id":"MULTI-SESSION-01",...}`

3. **Start a Session**:
   ```powershell
   curl -X POST http://localhost:8000/api/session/start `
     -H "Content-Type: application/json" `
     -d '{
       "session_id":"TEST-SESSION-001",
       "tenant_id":"tenant_corp",
       "user_id":"test_user",
       "agents":["CustomerBot","MemoryAgent","KnowledgeBase"]
     }'
   ```
   Expected: Success response with session details

4. **View the Session**:
   ```powershell
   curl http://localhost:8000/api/sessions/TEST-SESSION-001
   ```
   Expected: Session details with turns and metadata

## 🖥️ Accessing the GUI
Once you've confirmed the API is working (above steps), open your browser to:
```
http://localhost:8000
```

## 🛑 To Stop the Server
- If you used Method 1: Press `Ctrl+C` in the original PowerShell window
- If you used Method 2: Run the stop command shown above

## 📝 Troubleshooting
If you see "Unable to connect" errors:
1. Make sure you started the server with `python main.py`
2. Wait at least 3 seconds after starting before testing
3. Verify no other process is using port 8000 with: `netstat -ano | findstr :8000`
4. Try accessing `http://127.0.0.1:8000` instead of `localhost`

## 🎯 GUI Testing Examples
See `GUI_TESTING_EXAMPLES.md` for step-by-step instructions on testing all features through the web interface.

---

**Remember**: The server IS running when you see "Uvicorn running on http://0.0.0.0:8000" - the PowerShell timeout is just the interface waiting for the process to finish, which it won't do until you stop the server.