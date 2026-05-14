# Plateful — Testing Documentation

## Overview

This document covers manual testing for the Plateful web application.
Automated tests are not yet in place; all test cases below are manual.

**Test environment**
- Python 3.13, Flask, SQLite (local dev)
- Seed data: run `python seed.py` or call `create_test_data()` in Flask shell
- Base URL: `http://localhost:5000`

---

## 1. Authentication

### 1.1 Sign up — valid input
**Steps:** Open `/`, click "Create account", fill in all fields, accept terms, submit.  
**Expected:** Redirected to dashboard, session set, username visible in nav.  
**Status:** Pass

### 1.2 Sign up — duplicate username
**Steps:** Register with a username that already exists in the DB.  
**Expected:** Stays on signup tab, error message "That username is already taken."  
**Status:** Pass

### 1.3 Sign up — duplicate email
**Steps:** Register with an email already in the DB.  
**Expected:** Stays on signup tab, error message "An account with that email already exists."  
**Status:** Pass

### 1.4 Sign up — missing required fields
**Steps:** Submit signup form with one or more fields blank.  
**Expected:** Stays on signup tab, error message "Please fill in all required fields..."  
**Status:** Pass

### 1.5 Login — valid credentials
**Steps:** Log in with correct email and password.  
**Expected:** Redirected to `/dashboard`.  
**Status:** Pass

### 1.6 Login — wrong password / unknown email
**Steps:** Submit login form with bad credentials.  
**Expected:** Stays on login tab, error message "Invalid email or password."  
**Status:** Pass

### 1.7 Logout
**Steps:** Click logout from any authenticated page.  
**Expected:** Session cleared, redirected to `/`.  
**Status:** Pass

---

## 2. Follow / Unfollow

### 2.1 Follow a user from the Following page
**Steps:** Navigate to `/following`, click "Follow back" on a follower.  
**Expected:** Button changes to "Following", follower count updates on next page load.  
**Status:** Pass

### 2.2 Unfollow a user from the Following page
**Steps:** Navigate to `/following`, click "Following" on a followed user.  
**Expected:** User is removed from the list.  
**Status:** Pass

### 2.3 Follow / unfollow from Profile tab
**Steps:** Go to `/profile` → Followers tab, use follow/unfollow buttons.  
**Expected:** Same behaviour as 2.1 / 2.2.  
**Status:** Pass

### 2.4 Cannot follow yourself
**Steps:** Attempt a POST to `/follow/<own user id>` directly.  
**Expected:** No Follow record created, silent redirect.  
**Status:** Pass

---

## 3. Recipe Upload & Edit

### 3.1 Upload recipe with all fields
**Steps:** Go to `/upload`, fill in title, cuisine, difficulty, meal type, prep time, servings, description, at least one ingredient and step, submit.  
**Expected:** Redirected to recipe detail page with all fields displayed.  
**Status:** Pass

### 3.2 Upload recipe — meal type saved correctly
**Steps:** Upload a recipe with Meal Type set to "Breakfast".  
**Expected:** Recipe appears in the Breakfast row of the meal planner when added.  
**Status:** Pass

### 3.3 Edit recipe — fields persist
**Steps:** Edit an existing recipe, change title and meal type, save.  
**Expected:** Recipe detail page reflects updated values.  
**Status:** Pass

---

## 4. Seed Data

### 4.1 seed.py
**Steps:** With a fresh DB, run `python seed.py`.  
**Expected:** Users, recipes, ingredients, steps, follows, and saved recipes are created without errors.  
**Status:** Pass

### 4.2 create_test_data() via Flask shell
**Steps:** Run `flask shell`, then `from main.models import create_test_data; create_test_data()`.  
**Expected:** Same result as 4.1.  
**Status:** Pass

---

## 5. Dashboard — _To be completed by teammate_

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 5.1 | Dashboard loads for logged-in user | Shows tip, followed users, recent activity | — |
| 5.2 | Unauthenticated access redirects | Redirected to `/` | — |

---

## 6. Explore — _To be completed_

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 6.1 | Explore page shows all public recipes | Recipe cards visible | — |
| 6.2 | Search / filter (if implemented) | Results match filter | — |

---

## 7. Meal Planner — _To be completed 

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 7.1 | Add recipe to a day/meal slot | Recipe appears in cell | — |
| 7.2 | Remove recipe from slot | Cell clears | — |
| 7.3 | Meal type tag matches recipe's meal_type | Correct tag shown | — |

---

## 8. Save / Unsave Recipes — _To be completed _

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 8.1 | Save a recipe | Appears under `/saved` | — |
| 8.2 | Save same recipe twice | No duplicate, unique constraint holds | — |
| 8.3 | Unsave a recipe | Removed from saved list | — |

---

## 9. Profile & Settings — _To be completed_

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 9.1 | Profile page shows correct counts | Recipes, followers, following match DB | — |
| 9.2 | Settings — update display name | Name updates across nav and profile | — |

---

## Known issues / out of scope

- Google OAuth ("Continue with Google") button is not yet functional.
- Forgot password flow is a placeholder.
