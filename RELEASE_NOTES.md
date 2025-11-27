# Release Notes - v2.4.0

## 🚀 Key Features & Improvements

### 1. Production UI Polish
- **Fixed Feedback Text**: Resolved character corruption in the feedback section ("Was this classification correct?").
- **Restored Icons**: Fixed regression where theme toggle and other icons appeared as `??`.
- **Evaluation Page**: Replaced text-based GitHub link with a proper SVG icon and added a **Latency** column to the results table for better visibility of updates.
- **Favicon**: Added a ticket emoji (🎫) favicon to fix 404 errors.

### 2. Accuracy & Performance
- **Accuracy**: Achieved **90% accuracy** on the production test dataset (27/30 correct).
- **Latency**: Sub-second average response time (0.742s).
- **Gemini 2.0 Flash**: Now handling ~57% of traffic with high precision.

### 3. Repository Cleanup
- Moved debug and verification scripts to `scripts/` directory.
- Removed temporary generated JSON files.
- Updated `.gitignore` to exclude production artifacts.
- Suppressed Tailwind CSS development warning in console.

## 🐛 Bug Fixes
- Fixed "Missing Third Card" in "Why Automate?" section.
- Fixed layout issues in "Cost Efficiency" card.
- Resolved encoding issues with emoji characters.

## 📦 Dependency Updates
- No major dependency changes.

## 📝 Documentation
- Updated `README.md` to reflect v2.4.0 status.
- Updated `walkthrough.md` with final verification results.
