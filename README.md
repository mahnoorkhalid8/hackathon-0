# Hackathon-0: Digital FTE System

## Bronze Tier

```powershell
cd bronze-tier
python inbox_watcher.py

python status.py
```

---

## Silver Tier

### Bronze Tier Commands

```powershell
cd silver-tier

python inbox_watcher.py

python status.py
```

### Gmail Commands

```powershell
# CEO Briefing
python run_agent.py ceo-report

# Gmail Watcher
python run_agent.py gmail-watcher       

# Send Custom Email
python send_custom_email.py draft-email.yaml

# Test Gmail API
python test_gmail_api.py
```

### WhatsApp Commands
```powershell

cd whatsapp-node
npm start

python send_message.py
```

### LinkedIn Commands
```powershell

cd linkedin
python post_linkedin.py
```
---

## Gold Tier
### Facebook Commands
```powershell

cd facebook
python facebook_watcher.py
```

### Instagram Commands
```powershell

cd instagram
cd workflow
cd public
# run ngrok to publically push image on server
# terminal 1
python -m http.server 8001      

#terminal 2 (powershell) ----> to run ngrok
ngrok http 8000

#terminal 3
cd instagram
python ig_workflow_manager.py
```

### Twitter Commands
cd twitter
python twitter_poster_improved.py
---

**Terminal:** PowerShell or CMD
