# 📸 Screenshot Capture Instructions

Since browser automation is not available, please capture these screenshots manually:

## Required Screenshots

### 1. Landing Page (`landing-page.png`)
1. Navigate to: https://ai-ticket-classifier-production.up.railway.app/
2. Wait for page to fully load
3. Capture full-page screenshot
4. Save as: `docs/screenshots/landing-page.png`

### 2. Classification Demo (`classification-demo.png`)
1. On the landing page, enter text: "My internet connection keeps dropping every few minutes"
2. Click "Classify Ticket" button
3. Wait for result to appear
4. Capture screenshot showing the result
5. Save as: `docs/screenshots/classification-demo.png`

### 3. Swagger UI (`swagger-ui.png`)
1. Navigate to: https://ai-ticket-classifier-production.up.railway.app/docs/
2. Wait for Swagger UI to load
3. Expand the "POST /api/v1/classify" endpoint
4. Capture screenshot showing the API documentation
5. Save as: `docs/screenshots/swagger-ui.png`

### 4. Metrics Endpoint (`metrics.png`)
1. Navigate to: https://ai-ticket-classifier-production.up.railway.app/metrics
2. Wait for metrics to load
3. Capture screenshot
4. Save as: `docs/screenshots/metrics.png`

## Optional: GIF Recording

For a demo GIF showing the classification flow:

1. Use a screen recording tool (e.g., ScreenToGif, LICEcap)
2. Record the following sequence:
   - Landing page loads
   - Type ticket text
   - Click classify button
   - Result appears
3. Save as: `docs/gifs/classification-demo.gif`
4. Keep file size under 5MB for GitHub

## Tools Recommended

- **Windows**: Snipping Tool, ShareX, ScreenToGif
- **Mac**: Screenshot (Cmd+Shift+4), Kap
- **Linux**: Flameshot, Peek

After capturing, commit the screenshots:
```bash
git add docs/screenshots/* docs/gifs/*
git commit -m "Add visual assets for README"
```
