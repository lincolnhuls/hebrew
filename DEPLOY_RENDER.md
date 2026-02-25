# Deploying to Render

Deploy the Django app (with Neon Postgres) to Render as a Web Service.

---

## 1. Push your code

Ensure the `hebrew` project (with `requirements.txt`, `manage.py`, and `hebrew/` settings) is in a Git repo and push to GitHub (or GitLab). Render will clone from there.

If your repo root is **one level above** the Django project (e.g. `biblical_hebrew/hebrew/`), set **Root Directory** in Render to `hebrew` so that `manage.py` is at the root of the build context.

---

## 2. Create a Web Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com), sign in, and click **New +** → **Web Service**.
2. Connect your repo (GitHub/GitLab) and select the repository.
3. Configure:
   - **Name:** e.g. `biblical-hebrew`
   - **Region:** pick one close to you or your users.
   - **Root Directory:** if the Django app lives in a subfolder (e.g. `hebrew`), set it to that folder; otherwise leave blank.
   - **Runtime:** Python 3.
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     gunicorn hebrew.wsgi:application
     ```

---

## 3. Environment variables

In the Render service → **Environment** tab, add:

| Key | Value | Notes |
|-----|--------|--------|
| `DJANGO_SECRET_KEY` | (random secret string) | Generate a new one for production; do not use your local key. |
| `DJANGO_DEBUG` | `False` | Must be `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | `your-app-name.onrender.com` | Add your Render URL; use comma to add more (e.g. `yourapp.onrender.com,www.yourapp.com`). |
| `DATABASE_URL` | Your Neon connection string | From Neon dashboard, e.g. `postgresql://user:pass@host/db?sslmode=require`. |
| `FIREBASE_CREDENTIALS_JSON` | (entire Firebase service account JSON) | Copy the **whole** contents of your Firebase service account JSON file (single line or minified). Render cannot mount files; this env var is used instead of `GOOGLE_APPLICATION_CREDENTIALS`. |

Optional:

- `PYTHON_VERSION` = `3.12` (or the version you use locally) so Render uses the same Python.

Do **not** commit `.env` or your Firebase JSON to the repo. Set everything in Render’s Environment UI.

---

## 4. Run migrations on the first deploy

After the first successful deploy, run migrations and seed data once against the production DB (Render uses your `DATABASE_URL`, so this will run against Neon):

1. In Render dashboard → your service → **Shell** tab (or use **Manual Deploy** and run a one-off command if available).
2. Run:
   ```bash
   python manage.py migrate
   python manage.py seed_lessons_and_letters
   ```
   (Optional: run `import_wlc` if you want Bible data and have the WLC files in the repo or mounted.)

If Render does not offer a shell, you can run the same commands locally **with `DATABASE_URL` set to your Neon URL** so they run against the production database.

---

## 5. Go live

Save the environment variables and trigger a deploy (or push a commit). Your app will be at `https://<your-service-name>.onrender.com`. The first request after idle may be slow (Neon cold start; Render free tier spin-up).

---

## Summary

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start:** `gunicorn hebrew.wsgi:application`
- **Required env:** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `FIREBASE_CREDENTIALS_JSON`
- **First-time DB:** run `migrate` and `seed_lessons_and_letters` (and optionally `import_wlc`) against Neon.
