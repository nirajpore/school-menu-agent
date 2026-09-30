# 🏫 School Menu Agent - GitHub Actions Cloud Setup

## ✅ Cloud-Based Solution

This setup runs **entirely in the cloud** using GitHub Actions - no need to keep your laptop running!

## 🚀 How It Works

1. **GitHub runs daily** at 6:00 PM UTC (7:00 PM UK time)
2. **Downloads your menu PDF** (from URL or repository)
3. **Parses the menu** and checks UK holidays
4. **Sends email** via SMTP
5. **Completely automated** - runs even when your laptop is off

## 📋 Setup Steps

### 1. Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial school menu agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/school-menu-agent.git
git push -u origin main
```

### 2. Add Menu PDF to Repository
Place your school menu PDF file in the repository as `menu.pdf`

### 3. Configure Secrets in GitHub
Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:
- `EMAIL_TO`: your.email@example.com
- `SMTP_SERVER`: smtp.gmail.com (or your provider)
- `SMTP_PORT`: 587
- `SMTP_USERNAME`: your.email@gmail.com
- `SMTP_PASSWORD`: your-app-password (not regular password)

### 4. SMTP Configuration Examples

**Gmail:**
- Server: `smtp.gmail.com`
- Port: `587`
- Username: your Gmail address
- Password: [App password](https://myaccount.google.com/apppasswords)

**Outlook/Hotmail:**
- Server: `smtp.office365.com`
- Port: `587`

**Other providers:** Check your email provider's SMTP settings

### 5. Manual Test Run
Go to your repository → Actions → School Menu Agent → Run workflow

## 🔧 Alternative: Web-Based PDF Download

If your school publishes menus online, update the workflow:

```yaml
- name: Download latest menu PDF
  run: |
    curl -o menu.pdf "https://school-website.com/menu.pdf"
```

## 📊 GitHub Actions Features

- **Free**: 2000 minutes/month free for public repos
- **Reliable**: Runs on GitHub's infrastructure
- **Scheduled**: Daily automatic runs
- **Notifications**: Get email alerts on failures
- **Logs**: Full execution history available

## 🎯 What You Get

- Daily email at ~7:00 PM UK time with tomorrow's menu
- Automatic holiday/weekend skipping
- No local computer required
- Completely free cloud solution

## 🚨 Important Notes

1. **App Passwords**: For Gmail, use app passwords, not your regular password
2. **PDF Availability**: Ensure the menu PDF is accessible (in repo or via URL)
3. **Time Zone**: Runs at 6:00 PM UTC (7:00 PM UK summer time)
4. **Monitoring**: Check GitHub Actions tab for any failures

## 📞 Support

If the workflow fails:
1. Check Actions → School Menu Agent for error logs
2. Verify SMTP credentials are correct
3. Ensure PDF file is accessible

The cloud solution will work perfectly even when your laptop is turned off!