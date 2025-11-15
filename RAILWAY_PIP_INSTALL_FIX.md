# 🔧 Railway Build Fix - pip Module Not Found

## The Problem

Railway was showing:
```
/root/.nix-profile/bin/python3: No module named pip
```

This happened because **Nix's Python 3.12 doesn't include pip by default**. Unlike standard Python distributions, Nix packages are minimal and don't bundle pip.

## ✅ The Fix

We need to install pip first before we can use it. The solution is to:

1. **Download get-pip.py** using curl
2. **Install pip** using Python
3. **Use pip** to install dependencies

## What Changed

**Updated `nixpacks.toml`:**

```toml
[phases.setup]
nixPkgs = ["python312", "curl"]  # Added curl to download get-pip.py

[phases.install]
cmds = [
  "curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py && export PATH=\"$HOME/.local/bin:$PATH\" && python3 -m pip install --upgrade pip && python3 -m pip install -r backend/requirements.txt"
]
```

## Why This Works

1. **curl** downloads the official pip installer script
2. **python3 get-pip.py** installs pip into `$HOME/.local/bin`
3. **export PATH** ensures pip is found in subsequent commands
4. All commands are combined with `&&` so they run in the same shell session
5. Then we can use `python3 -m pip` normally

## Environment Variables

You'll need to add these environment variables in Railway Dashboard:

### Required Variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your Railway domain (e.g., `your-app.railway.app`)
- `DATABASE_URL` - PostgreSQL connection string (Railway provides this automatically if you add a PostgreSQL service)
- `REDIS_URL` - Redis connection string (if using Redis)

### Optional (for AI features):
- `OPENAI_API_KEY` - For OpenAI text generation
- `HUGGINGFACE_API_KEY` - For Hugging Face models
- `STABILITY_API_KEY` - For Stability AI image generation
- `REPLICATE_API_KEY` - For Replicate image/video generation

## Next Steps

1. **Commit and push:**
   ```bash
   git add nixpacks.toml
   git commit -m "Fix Railway build - install pip using get-pip.py"
   git push
   ```

2. **Add Environment Variables in Railway:**
   - Go to Railway Dashboard → Your Service
   - Click **Variables** tab
   - Add all required environment variables
   - Railway will automatically redeploy

3. **Railway will now:**
   - Install Python 3.12
   - Download and install pip
   - Successfully install all dependencies
   - Build and deploy your app

The build should work now! 🚀

## Why Nix Python Doesn't Include pip

Nix is a functional package manager that keeps packages minimal and isolated. Python from Nix is just the interpreter - pip is considered a separate package. This is different from standard Python distributions (like from python.org) which bundle pip.

