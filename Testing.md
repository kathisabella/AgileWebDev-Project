# Plateful — Testing Documentation

## Overview

This document covers both automated and manual testing for the Plateful web application.

**Test environment**
- Python 3.13, Flask, SQLite (local dev)
- Seed data: run `python seed.py` or call `create_test_data()` in Flask shell
- Base URL: `http://localhost:5000`

**Running automated tests**
```bash
# Unit tests
python -m pytest tests/test_unit.py -v

# Selenium tests (requires Chrome + chromedriver)
python -m pytest tests/test_selenium.py -v
```

---

## Automated Unit Tests (`tests/test_unit.py`)

All 22 tests use an in-memory SQLite database (`sqlite:///:memory:`) via `TestConfig`.
Each test class creates a fresh DB in `setUp` and drops it in `tearDown`.

### Password & Authentication

| Test | Description | Expected |
|------|-------------|----------|
| `test_password_correct` | `check_password` with correct password | Returns `True` |
| `test_password_wrong` | `check_password` with wrong password | Returns `False` |
| `test_password_not_stored_as_plaintext` | Password hash differs from raw password | `password_hash != 'correctpassword'` |

### User Model

| Test | Description | Expected |
|------|-------------|----------|
| `test_user_created_in_db` | User exists in DB after creation | Not `None` |
| `test_duplicate_username_rejected` | Insert user with existing username | Raises `IntegrityError` |
| `test_duplicate_email_rejected` | Insert user with existing email | Raises `IntegrityError` |
| `test_user_joined_date_set_automatically` | `joined_date` set on creation | Not `None` |

### Recipe Model

| Test | Description | Expected |
|------|-------------|----------|
| `test_recipe_linked_to_author` | Recipe's `author.username` matches creator | `'testchef'` |
| `test_recipe_count_for_user` | Count recipes for a user | `1` |
| `test_recipe_has_ingredient` | Ingredient linked to recipe | Name is `'Pasta'` |
| `test_recipe_has_step` | Step linked to recipe | Instruction is `'Boil pasta'` |
| `test_recipe_fields_stored_correctly` | All recipe fields persist correctly | Cuisine, difficulty, prep_time, servings, meal_type match |

### Save / Unsave

| Test | Description | Expected |
|------|-------------|----------|
| `test_save_recipe` | Save a recipe | `SavedRecipe` row exists |
| `test_duplicate_save_rejected` | Save same recipe twice | Raises `IntegrityError` |
| `test_unsave_recipe` | Delete a saved recipe | `SavedRecipe` row gone |

### Follow / Unfollow

| Test | Description | Expected |
|------|-------------|----------|
| `test_follow_user` | Follow another user | `Follow` row exists |
| `test_unfollow_user` | Delete follow relationship | `Follow` row gone |
| `test_cannot_follow_yourself` | No self-follow row in DB | `None` |
| `test_duplicate_follow_rejected` | Follow same user twice | Raises `IntegrityError` |

### Meal Plan

| Test | Description | Expected |
|------|-------------|----------|
| `test_meal_plan_entry_saved` | Create a `MealPlanEntry` with recipe | Row exists, references correct recipe |
| `test_meal_plan_entry_without_recipe` | Create empty meal slot (`recipe_id=None`) | Row exists, `recipe_id` is `None` |

### Activity

| Test | Description | Expected |
|------|-------------|----------|
| `test_activity_recorded_for_upload` | Log `uploaded_recipe` activity | Row exists with correct `related_recipe_id` |
| `test_activity_recorded_for_follow` | Log `followed_user` activity | Row exists with correct `related_user_id` |
| `test_multiple_activities_for_user` | Log 2 activities for same user | Count is `2` |

---

## Automated Selenium Tests (`tests/test_selenium.py`)

All 6 tests use a file-based SQLite DB (`sqlite:///selenium_test.db`) via `SeleniumTestConfig`.
Flask runs on a daemon thread at `http://localhost:5001`. Chrome runs headless.

| Test | Description | Expected |
|------|-------------|----------|
| `test_login_page_loads` | Navigate to `/` | Page title contains `'Plateful'` |
| `test_valid_login_redirects_to_dashboard` | Login with valid credentials | URL contains `/dashboard` |
| `test_invalid_login_shows_error` | Login with wrong password | Error element visible on page |
| `test_explore_requires_login` | Navigate to `/explore` without login | Redirected to `/` |
| `test_explore_shows_recipes_after_login` | Login then visit `/explore` | At least 1 recipe card visible |
| `test_logout_redirects_to_login` | Click logout | Redirected to `/` |

---

## Manual Tests

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
**Steps:** Navigate to `/following`, click "Follow" on a suggested account.  
**Expected:** User moves from suggested to following list.  
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

### 2.5 Follow from recipe details
**Steps:** View a recipe by another user, click "+ Follow" in the author card.  
**Expected:** Button changes to "Following".  
**Status:** Pass

### 2.6 Follow activity logged
**Steps:** Follow a user, check dashboard activity feed.  
**Expected:** "Followed [name]" appears in the activity feed.  
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

### 3.4 Delete recipe — cascades to ingredients and steps
**Steps:** Delete a recipe from `/my-recipes`.  
**Expected:** Recipe, its ingredients, steps, and saved records all removed from DB.  
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

## 5. Dashboard

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 5.1 | Dashboard loads for logged-in user | Shows tip, followed users, recent activity | Pass |
| 5.2 | Unauthenticated access redirects | Redirected to `/` | Pass |
| 5.3 | Recipe count reflects actual recipes | Count matches DB | Pass |
| 5.4 | Activity feed shows recent actions | Upload/save/follow events visible | Pass |

---

## 6. Explore

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 6.1 | Explore page shows all recipes | Recipe cards visible for all users | Pass |
| 6.2 | Author name links to public profile | Clicking author name navigates to `/user/<id>` | Pass |
| 6.3 | Unauthenticated access redirects | Redirected to `/` | Pass |

---

## 7. Meal Planner

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 7.1 | Add a day to meal plan | Day row appears in planner | Pass |
| 7.2 | Delete a day | Row removed, remaining days renumbered | Pass |
| 7.3 | Clear all | All rows removed | Pass |
| 7.4 | Meal plan persists across page reload | Entries saved in `MealPlanEntry` table | Pass |

---

## 8. Save / Unsave Recipes

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 8.1 | Save a recipe | Appears under `/saved`, button shows "Saved ✓" | Pass |
| 8.2 | Save same recipe twice | No duplicate, unique constraint holds | Pass |
| 8.3 | Unsave a recipe | Removed from saved list | Pass |

---

## 9. Public User Profile

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 9.1 | Visit another user's profile | Shows their name, bio, recipe grid | Pass |
| 9.2 | Follow from public profile | Button changes to "Following" | Pass |
| 9.3 | Visit own profile via `/user/<own id>` | Redirects to `/profile` | Pass |
| 9.4 | Follower / following counts correct | Counts match DB | Pass |

---

## 10. Profile & Settings

| # | Test case | Expected | Status |
|---|-----------|----------|--------|
| 10.1 | Profile page shows correct counts | Recipes, followers, following match DB | Pass |
| 10.2 | Settings — update display name | Name updates across nav and profile | Pass |
| 10.3 | Settings — update bio | Bio visible on profile page | Pass |

---

## 11. Rate Limiting

### 11.1 Login — brute-force blocked
**Steps:** Submit the login form with wrong credentials more than 3 times within one minute.  
**Expected:** Returns a `429 Too Many Requests` response.  
**Status:** Pass

### 11.2 Signup — rate limited
**Steps:** Submit the signup form more than 3 times within one minute.  
**Expected:** Returns a `429 Too Many Requests` response.  
**Status:** Pass

### 11.3 Normal usage not affected
**Steps:** Log in successfully within the first 3 attempts in a minute.  
**Expected:** Login proceeds normally with no rate limit error.  
**Status:** Pass

---

## 12. Image Upload

### 12.1 Upload recipe with image
**Steps:** Go to `/upload`, fill in required fields, attach a `.jpg` or `.png` image, submit.  
**Expected:** Redirected to recipe detail page; image displays in the image area.  
**Status:** Pass

### 12.2 Image shows on recipe cards
**Steps:** After uploading a recipe with an image, check the Explore and Dashboard pages.  
**Expected:** Recipe card thumbnail shows the uploaded image.  
**Status:** Pass

### 12.3 Edit recipe — existing image preserved
**Steps:** Edit an existing recipe without selecting a new image file, save.  
**Expected:** Original image still displays on the recipe detail page.  
**Status:** Pass

### 12.4 Edit recipe — replace image
**Steps:** Edit an existing recipe and attach a new image file, save.  
**Expected:** New image replaces the old one on the recipe detail page.  
**Status:** Pass

### 12.5 Upload without image
**Steps:** Submit the upload form without attaching an image.  
**Expected:** Recipe is created successfully; image area shows the blank placeholder.  
**Status:** Pass

---

## Known issues / out of scope

- Google OAuth ("Continue with Google") button is not yet functional.
- Forgot password flow is a placeholder.
- Ingredient quantity and unit fields exist in the DB schema but are not yet collected via the upload form.
