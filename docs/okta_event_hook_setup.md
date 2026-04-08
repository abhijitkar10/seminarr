# Okta Event Hook Setup Guide

This guide shows how to connect Okta Event Hooks to the local Auth Anomaly Detection API.

## 1. Start the API server

From the repository root:

```bash
cd /Users/abhijitkar/Documents/trae_projects/seminar/seminarr
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API should be available at:

- `http://localhost:8000`

## 2. Start ngrok for HTTPS tunneling

In a second terminal:

```bash
ngrok http 8000
```

Copy the public HTTPS URL that ngrok provides, for example:

- `https://unepigrammatically-uniformed-idella.ngrok-free.dev`

This is the URL Okta will call.

## 3. Configure Okta Event Hook

In your Okta org:

1. Open `https://integrator-2852306.okta.com`
2. Sign in and open the Admin console
3. Go to `Workflow` → `Event Hooks`
4. Click `Create Event Hook`

Fill in:

- **Name:** `Auth Anomaly Detection Hook`
- **URL:** `https://<your-ngrok-domain>/hooks/okta`
- **Authentication field:** `Authorization`
- **Authentication secret:** use your shared secret

For **Subscribe to events**, select auth-related events such as:

- `user.authentication.authenticate_user`
- `user.authentication.auth_via_password`
- `user.authentication.invalid_password`
- `user.authentication.auth_via_mfa`

Do not leave the subscribe field blank.

## 4. Set your local environment secret

Create or update `.env` in the repository root with the same secret used in Okta:

```env
OKTA_EVENT_HOOK_AUTH_SECRET=MyS3cureH00kSecret_2026
OKTA_EVENT_HOOK_AUTH_HEADER=authorization
```

**Important:** do not commit `.env` into source control.

## 5. Restart the API

Any time the `.env` file changes, restart:

```bash
uvicorn app.main:app --reload --port 8000
```

## 6. Verify the hook

Okta will send a verification request automatically when you save the hook. If the API is running and the ngrok tunnel is active, the hook should verify successfully.

## 7. Test a login

Trigger a new Okta login event by signing in at your Okta org URL or using an incognito browser session.

Then verify delivery locally by opening:

```bash
http://localhost:8000/events/recent
```

Your event should appear in the returned JSON.

## 8. Open the dashboard

Start the dashboard in another terminal:

```bash
streamlit run dashboard/app.py --server.port 8501
```

Open:

- `http://localhost:8501`

Use the **Activity** tab to inspect incoming events, and the **Users** tab to find a specific user.

## 9. Notes for collaborators

- Use `.env.example` as a template
- Do not commit real secrets in `.env`
- Restart the API whenever `.env` changes
- Keep the ngrok tunnel running while testing
