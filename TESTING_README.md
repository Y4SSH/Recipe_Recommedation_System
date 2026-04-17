# Testing Quick Start Guide

Welcome! You have comprehensive testing documentation. This page helps you get started quickly.

---

## 📋 Documentation Files Created

1. **[MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md)** ⭐ START HERE
   - Complete step-by-step instructions for all tests
   - 14 backend API tests with expected responses
   - 15 frontend UI tests
   - 4 end-to-end user flows
   - 10 edge case scenarios
   - Performance benchmarking guide
   - **Total coverage: 2-3 hours of testing**

2. **[TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md)** ✅ USE DURING TESTING
   - Print this or keep it open
   - Quick checkboxes for each test
   - Must-pass vs should-pass vs nice-to-have criteria
   - Test data to save as you go
   - Troubleshooting reference

3. **[API_TESTING_COMMANDS.md](./API_TESTING_COMMANDS.md)** 🔧 FOR BACKEND TESTING
   - Ready-to-copy curl commands for every endpoint
   - PowerShell examples
   - Quick test scripts
   - Copy-paste scenarios for common flows

4. **[BROWSER_CONSOLE_TESTING.md](./BROWSER_CONSOLE_TESTING.md)** 🌐 FOR FRONTEND TESTING
   - JavaScript snippets for browser console
   - Helper functions for API calls
   - UI element verification
   - Performance measurement scripts

---

## 🚀 Quick Start (10 Minutes)

### Step 1: Start Services (2 minutes)

**Terminal 1 - Backend:**
```bash
cd d:\Projects\Major-Project\backend-python
set RECOMMENDER_WARMUP_ON_STARTUP=1
python main.py
```

Wait for: `INFO: Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
cd d:\Projects\Major-Project\frontend
npm run dev
```

Wait for: `VITE v4.x.x ready in XXX ms`

### Step 2: Verify Health (1 minute)

Open browser and test:
```
http://localhost:8000/health
```

Should see: `{"status":"healthy"}`

### Step 3: Run Quick Test (5 minutes)

**Option A: Browser Console** (Easiest)
1. Open `http://localhost:5173` in browser
2. Press `F12` to open DevTools → Console tab
3. Copy-paste this:
```javascript
// Quick Test Suite
(async () => {
  console.log('🧪 Starting Quick Tests...\n');
  
  const health = await fetch('http://localhost:8000/health').then(r => r.json());
  console.log('✅ Health:', health.status);
  
  const recipes = await fetch('http://localhost:8000/recipes/?limit=3').then(r => r.json());
  console.log(`✅ Recipes: ${recipes.total} total`);
  
  const veg = await fetch('http://localhost:8000/recipes/?diet=veg&limit=3').then(r => r.json());
  console.log(`✅ Veg recipes: ${veg.recipes.length} found`);
  
  console.log('\n✅ Basic tests passed!');
})();
```

**Option B: PowerShell** (More detailed)

See [API_TESTING_COMMANDS.md](./API_TESTING_COMMANDS.md) → "Quick Test Script" section

---

## 📊 Test Coverage Overview

| Component | Type | Tests | Time | File |
|-----------|------|-------|------|------|
| Backend API | 14 endpoints | Auth, Recipes, Recommendations, Saved, Ratings, Feedback | ~45 min | MANUAL_TESTING_GUIDE.md |
| Frontend UI | 15 screens | Landing, Dashboard, Explore, Recipe Detail, Saved, Recommendations | ~30 min | MANUAL_TESTING_GUIDE.md |
| End-to-End | 4 flows | Signup→Dashboard→Save, AI Recommendations, Filters, Performance | ~30 min | MANUAL_TESTING_GUIDE.md |
| Edge Cases | 10 scenarios | Invalid inputs, network errors, concurrency | ~20 min | MANUAL_TESTING_GUIDE.md |
| Performance | Benchmarking | Cold start, warmup, API latency | ~20 min | MANUAL_TESTING_GUIDE.md |

---

## ✅ Success Criteria (Must Pass)

These 5 items **MUST** work for production readiness:

1. ✅ **Cuisine filter shows EXACTLY 2 options** (Any Indian, Indian only)
   - NOT the old 16 generic options
   - Check on Dashboard and Explore pages

2. ✅ **Recipe metadata is visible**
   - On Recipe Detail page
   - Shows: variant_type, cooking_method, protein_type, base_recipe
   - Displayed as tags or in quick info section

3. ✅ **Recommendations fallback works**
   - Search with fake ingredients (e.g., "xyz_fake_ingredient")
   - Still returns results (not empty)
   - Shows "broadened search" explanation

4. ✅ **Diet labels are consistent**
   - All recipes show "Veg" or "Non-Veg" (not mixed terminology)
   - Filter applies correctly

5. ✅ **No console errors**
   - Open DevTools → Console
   - No red error messages
   - Only warnings/info logs acceptable

---

## 🎯 Recommended Testing Path

### Path 1: Quick Smoke Test (30 minutes)
**Use when:** Validating a fresh deployment or quick sanity check
1. Pre-Flight Checks (5 min) - [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#pre-flight-checks)
2. API Test 1-3 (Auth) - [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#-test-1-user-signup)
3. Frontend Test 4-6 (Filters) - [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#-test-4-dashboard---recipe-search)
4. End-to-End Flow 1 (Quick Journey) - [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#-flow-1-complete-recommendation-journey)
5. Check Success Criteria - [Above](#-success-criteria-must-pass)

### Path 2: Full QA Test (2-3 hours)
**Use when:** Pre-production validation or comprehensive quality check
1. Complete [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md) in order
2. Use [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) to track progress
3. Record metrics from Performance section
4. Document any issues found

### Path 3: Developer Integration Test (1 hour)
**Use when:** Adding new features or validating changes
1. API Tests 1-14 using [API_TESTING_COMMANDS.md](./API_TESTING_COMMANDS.md)
2. Browser Console Tests using [BROWSER_CONSOLE_TESTING.md](./BROWSER_CONSOLE_TESTING.md)
3. Check specific modified endpoints
4. Verify no regressions in adjacent features

---

## 🛠️ Tools You'll Need

- **Browser** - Chrome, Firefox, or Edge
- **PowerShell** - For running curl commands
- **DevTools** - Built into all modern browsers (F12)
- **Text Editor** - To track results (optional)

---

## 📝 Testing Data

As you test, save these for reference:

```
Test User Email: _______________________
Test User Password: _______________________
JWT Token: _______________________
Test Recipe ID: _______________________
Backend Startup Time: _______ seconds
First Recommendation Time: _______ ms
```

---

## 🔍 Key Tests to Focus On

### Highest Priority (Must Work)
1. **Login/Signup Flow** - If broken, nothing else works
2. **Recipe List & Filter** - Core functionality
3. **Recommendations API** - Main feature
4. **Metadata Display** - New feature, verify fully present

### High Priority (Should Work)  
5. **Save/Rate/Feedback** - User engagement
6. **Fallback Logic** - Edge case handling
7. **Performance** - User experience

### Medium Priority (Nice to Have)
8. **Image Loading** - Visual polish
9. **Error Messages** - UX clarity
10. **Edge Cases** - Robustness

---

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Frontend can't connect to backend | Check backend running on :8000, no CORS errors in console |
| Cuisine filter shows wrong options | Hard refresh (Ctrl+Shift+R), clear localStorage |
| Metadata not showing | Frontend might be using cached code; npm run build fresh |
| Recommendations take >3 seconds | Check if warmup is enabled; first request expected to be slow |
| Auth token not persisting | Check localStorage in DevTools; verify token saving code |
| Recipe images broken | Check `/static/recipes/` path in backend; try hard refresh |
| Tests passing but UI looks wrong | Clear browser cache and localStorage |

See **Troubleshooting** section in [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#troubleshooting-quick-reference) for more.

---

## 📈 Performance Baselines

These are expected ranges. Faster is better!

| Metric | Expected | Notes |
|--------|----------|-------|
| Backend startup (no warmup) | 2-5 sec | Backend only |
| Backend startup (with warmup) | 10-20 sec | Includes embedding precompute |
| First recommendation request | 300-2000 ms | Cold start penalty if no warmup |
| Second recommendation request | 300-1500 ms | Should be similar or faster |
| Recipe list API | 50-200 ms | Simple database query |
| Recipe detail API | 30-100 ms | Single record lookup |
| Frontend page load | <2 sec | After login |

Run the Performance section in [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md#performance--warmup-testing) to measure your actual times.

---

## 💾 Saving Your Results

**Create a results file:**

```markdown
# Testing Results - April 17, 2026

## Smoke Test: ✅ PASSED

- ✅ Backend health check
- ✅ Frontend loads
- ✅ Login works
- ✅ Recipes display
- ✅ Metadata visible

## API Tests: 14/14 PASSED
- ✅ Auth endpoints
- ✅ Recipe endpoints
- ✅ Recommendation endpoints
- ✅ All response codes correct

## Frontend Tests: 15/15 PASSED
- ✅ All pages load
- ✅ Filters work correctly
- ✅ Metadata displays
- ✅ Save/Rate features work

## Performance
- First recommendation: 450ms
- Second recommendation: 320ms
- Backend startup: 12 seconds (with warmup)

## Issues Found
- None critical
- Minor UI polish needed on recommendation cards

## Recommendation
✅ READY FOR PRODUCTION
```

---

## 🎬 Getting Started Now

**Choose one:**

### Quick Smoke (30 min)
→ Go to [Section: Recommended Testing Path > Path 1](./README.md#path-1-quick-smoke-test-30-minutes)

### Full QA Testing (2-3 hours)
→ Open [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md)  
→ Go to "Pre-Testing Setup"  
→ Work through in order  
→ Use [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) to track

### API Testing Only
→ Open [API_TESTING_COMMANDS.md](./API_TESTING_COMMANDS.md)  
→ Copy commands to PowerShell  
→ Run scenarios in order

### Frontend Testing Only
→ Open [BROWSER_CONSOLE_TESTING.md](./BROWSER_CONSOLE_TESTING.md)  
→ Open DevTools Console (F12)  
→ Copy-paste snippets one by one

---

## 📞 Getting Help

All guides have:
- ✅ Clear instructions
- ✅ Expected outputs
- ✅ Verification checklists
- ✅ Error handling tips
- ✅ Troubleshooting sections

**Before asking for help, check:**
1. [MANUAL_TESTING_GUIDE.md - Troubleshooting](./MANUAL_TESTING_GUIDE.md#troubleshooting-quick-reference)
2. [TESTING_CHECKLIST.md - Critical Success Criteria](./TESTING_CHECKLIST.md#critical-success-criteria)
3. Browser DevTools Console for error messages

---

## ✨ Summary

You now have **4 comprehensive testing documents**:

| Document | Use When | Time |
|----------|----------|------|
| MANUAL_TESTING_GUIDE.md | Detailed, comprehensive testing | 2-3 hours |
| TESTING_CHECKLIST.md | Quick reference during testing | Print or keep open |
| API_TESTING_COMMANDS.md | Testing backend API with curl | 45 minutes |
| BROWSER_CONSOLE_TESTING.md | Testing frontend from dev console | 30 minutes |

**Combined, these cover 100% of your application's functionality.**

---

## 🚀 Ready to Test?

1. **Start services** (backend + frontend)
2. **Open [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md)**
3. **Follow Pre-Flight Checks**
4. **Work through tests in order**
5. **Use [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) to track progress**

**Estimated total time: 2-3 hours for complete coverage**

Good luck! 🎉
