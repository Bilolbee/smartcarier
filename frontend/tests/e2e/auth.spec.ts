import { test, expect } from '@playwright/test';

/**
 * =============================================================================
 * Authentication E2E Tests
 * =============================================================================
 * 
 * Tests for user authentication flows:
 * - Landing page
 * - Registration
 * - Login
 * - Logout
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Go to landing page
    await page.goto('/');
  });

  // ===========================================================================
  // LANDING PAGE
  // ===========================================================================

  test('should display landing page correctly', async ({ page }) => {
    // Check hero section
    await expect(page.getByRole('heading', { name: /SmartCareer AI/i })).toBeVisible();
    
    // Check navigation
    await expect(page.getByRole('link', { name: /login/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /register/i })).toBeVisible();
    
    // Check CTA buttons
    await expect(page.getByRole('button', { name: /get started/i })).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.getByRole('link', { name: /login/i }).first().click();
    
    await expect(page).toHaveURL('/login');
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.getByRole('link', { name: /register/i }).first().click();
    
    await expect(page).toHaveURL('/register');
    await expect(page.getByRole('heading', { name: /sign up/i })).toBeVisible();
  });

  // ===========================================================================
  // REGISTRATION
  // ===========================================================================

  test('should register new student successfully', async ({ page }) => {
    await page.goto('/register');
    
    // Generate unique email
    const timestamp = Date.now();
    const email = `test.student.${timestamp}@example.com`;
    
    // Fill registration form
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/full name/i).fill('Test Student');
    await page.getByLabel(/password/i).first().fill('TestPassword123!');
    await page.getByLabel(/confirm password/i).fill('TestPassword123!');
    
    // Select student role (if needed)
    const studentRadio = page.getByRole('radio', { name: /student/i });
    if (await studentRadio.isVisible()) {
      await studentRadio.click();
    }
    
    // Submit form
    await page.getByRole('button', { name: /sign up|register/i }).click();
    
    // Should redirect to dashboard or show success
    await expect(page).toHaveURL(/\/(student|dashboard)/, { timeout: 10000 });
  });

  test('should show error for invalid email', async ({ page }) => {
    await page.goto('/register');
    
    await page.getByLabel(/email/i).fill('invalid-email');
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/password/i).first().fill('TestPassword123!');
    
    await page.getByRole('button', { name: /sign up|register/i }).click();
    
    // Should show validation error
    await expect(page.getByText(/invalid.*email/i)).toBeVisible();
  });

  test('should show error for weak password', async ({ page }) => {
    await page.goto('/register');
    
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/password/i).first().fill('weak');
    
    // Should show password strength indicator or error
    await expect(page.getByText(/password.*weak|password.*short/i)).toBeVisible();
  });

  test('should show error for duplicate email', async ({ page }) => {
    await page.goto('/register');
    
    // Use known existing email (from seed data)
    await page.getByLabel(/email/i).fill('john@example.com');
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/password/i).first().fill('TestPassword123!');
    await page.getByLabel(/confirm password/i).fill('TestPassword123!');
    
    await page.getByRole('button', { name: /sign up|register/i }).click();
    
    // Should show duplicate email error
    await expect(page.getByText(/email.*already.*exists/i)).toBeVisible({ timeout: 5000 });
  });

  // ===========================================================================
  // LOGIN
  // ===========================================================================

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Use test account from seed data
    await page.getByLabel(/email/i).fill('john@example.com');
    await page.getByLabel(/password/i).fill('Student123!');
    
    await page.getByRole('button', { name: /sign in|login/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/(student|dashboard)/, { timeout: 10000 });
    
    // Should show user info
    await expect(page.getByText(/john/i)).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByLabel(/email/i).fill('john@example.com');
    await page.getByLabel(/password/i).fill('WrongPassword123!');
    
    await page.getByRole('button', { name: /sign in|login/i }).click();
    
    // Should show error message
    await expect(page.getByText(/invalid.*password|incorrect/i)).toBeVisible();
  });

  test('should show error for non-existent user', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByLabel(/email/i).fill('nonexistent@example.com');
    await page.getByLabel(/password/i).fill('SomePassword123!');
    
    await page.getByRole('button', { name: /sign in|login/i }).click();
    
    // Should show error
    await expect(page.getByText(/invalid|not found/i)).toBeVisible();
  });

  // ===========================================================================
  // LOGOUT
  // ===========================================================================

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('john@example.com');
    await page.getByLabel(/password/i).fill('Student123!');
    await page.getByRole('button', { name: /sign in|login/i }).click();
    
    await expect(page).toHaveURL(/\/(student|dashboard)/);
    
    // Logout
    // Look for logout button in dropdown or menu
    const profileButton = page.getByRole('button', { name: /profile|account|john/i }).first();
    await profileButton.click();
    
    await page.getByRole('menuitem', { name: /logout|sign out/i }).click();
    
    // Should redirect to home or login
    await expect(page).toHaveURL(/\/(|login)/);
  });

  // ===========================================================================
  // LANGUAGE SWITCHING
  // ===========================================================================

  test('should switch between languages', async ({ page }) => {
    await page.goto('/');
    
    // Find language switcher
    const languageSwitcher = page.getByRole('button', { name: /uz|ru|language/i }).first();
    
    if (await languageSwitcher.isVisible()) {
      await languageSwitcher.click();
      
      // Click Russian option
      await page.getByRole('menuitem', { name: /russian|ru|русский/i }).click();
      
      // Check if content changed to Russian
      await expect(page.getByText(/войти|регистрация/i)).toBeVisible();
      
      // Switch back to Uzbek
      await languageSwitcher.click();
      await page.getByRole('menuitem', { name: /uzbek|uz|o'zbek/i }).click();
      
      await expect(page.getByText(/kirish|ro'yxatdan/i)).toBeVisible();
    }
  });
});









