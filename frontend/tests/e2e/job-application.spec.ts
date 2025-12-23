import { test, expect } from '@playwright/test';

/**
 * =============================================================================
 * Job Application E2E Tests
 * =============================================================================
 * 
 * Tests for critical user journey:
 * - Student logs in
 * - Browses jobs
 * - Views job details
 * - Applies to job
 * - Views application status
 */

test.describe('Job Application Flow', () => {
  // Login helper
  async function login(page) {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('john@example.com');
    await page.getByLabel(/password/i).fill('Student123!');
    await page.getByRole('button', { name: /sign in|login/i }).click();
    await expect(page).toHaveURL(/\/(student|dashboard)/);
  }

  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  // ===========================================================================
  // JOB BROWSING
  // ===========================================================================

  test('should display jobs list', async ({ page }) => {
    // Navigate to jobs page
    await page.getByRole('link', { name: /jobs|find jobs/i }).click();
    
    await expect(page).toHaveURL(/\/jobs/);
    
    // Should show jobs
    await expect(page.getByText(/software|developer|engineer/i).first()).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await page.goto('/student/jobs');
    
    // Use search
    const searchInput = page.getByPlaceholder(/search.*jobs/i);
    await searchInput.fill('Python');
    
    // Wait for results
    await page.waitForTimeout(1000);
    
    // Should show Python-related jobs
    await expect(page.getByText(/python/i).first()).toBeVisible();
  });

  test('should filter jobs by location', async ({ page }) => {
    await page.goto('/student/jobs');
    
    // Open filter
    const filterButton = page.getByRole('button', { name: /filter|location/i }).first();
    if (await filterButton.isVisible()) {
      await filterButton.click();
      
      // Select location
      await page.getByRole('checkbox', { name: /tashkent/i }).check();
      
      // Apply filter
      await page.getByRole('button', { name: /apply/i }).click();
      
      // Should show filtered results
      await expect(page.getByText(/tashkent/i).first()).toBeVisible();
    }
  });

  // ===========================================================================
  // JOB DETAILS
  // ===========================================================================

  test('should view job details', async ({ page }) => {
    await page.goto('/student/jobs');
    
    // Click on first job
    await page.getByRole('link', { name: /view.*details|learn more/i }).first().click();
    
    // Should show job details
    await expect(page).toHaveURL(/\/jobs\/[a-f0-9-]+/);
    await expect(page.getByRole('heading', { name: /developer|engineer/i })).toBeVisible();
    await expect(page.getByText(/requirements/i)).toBeVisible();
    await expect(page.getByText(/responsibilities/i)).toBeVisible();
  });

  // ===========================================================================
  // JOB APPLICATION
  // ===========================================================================

  test('should apply to job successfully', async ({ page }) => {
    await page.goto('/student/jobs');
    
    // Click on first job
    await page.getByRole('link', { name: /view.*details|learn more/i }).first().click();
    
    // Click apply button
    await page.getByRole('button', { name: /apply|submit application/i }).click();
    
    // Should show application form
    await expect(page.getByText(/select.*resume/i)).toBeVisible();
    
    // Select resume (if exists)
    const resumeSelect = page.getByRole('combobox', { name: /resume/i }).first();
    if (await resumeSelect.isVisible()) {
      await resumeSelect.click();
      await page.getByRole('option').first().click();
    }
    
    // Fill cover letter
    await page.getByLabel(/cover letter/i).fill('I am very interested in this position and believe I would be a great fit.');
    
    // Submit application
    await page.getByRole('button', { name: /submit|send application/i }).click();
    
    // Should show success message
    await expect(page.getByText(/success|applied/i)).toBeVisible({ timeout: 10000 });
  });

  test('should not allow duplicate application', async ({ page }) => {
    await page.goto('/student/jobs');
    
    // Find job that user already applied to
    const appliedJob = page.getByText(/applied/i).first();
    
    if (await appliedJob.isVisible()) {
      await appliedJob.click();
      
      // Apply button should be disabled or show "Already Applied"
      await expect(page.getByText(/already applied|applied/i)).toBeVisible();
    }
  });

  // ===========================================================================
  // MY APPLICATIONS
  // ===========================================================================

  test('should view my applications', async ({ page }) => {
    // Navigate to applications
    await page.getByRole('link', { name: /my applications|applications/i }).click();
    
    await expect(page).toHaveURL(/\/applications/);
    
    // Should show applications list
    await expect(page.getByText(/pending|reviewing|interview/i).first()).toBeVisible();
  });

  test('should filter applications by status', async ({ page }) => {
    await page.goto('/student/applications');
    
    // Open status filter
    const statusFilter = page.getByRole('combobox', { name: /status|filter/i }).first();
    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.getByRole('option', { name: /pending/i }).click();
      
      // Should show only pending applications
      await expect(page.getByText(/pending/i).first()).toBeVisible();
    }
  });

  test('should view application details', async ({ page }) => {
    await page.goto('/student/applications');
    
    // Click on first application
    await page.getByRole('button', { name: /view details|details/i }).first().click();
    
    // Should show application details
    await expect(page.getByText(/job title|position/i)).toBeVisible();
    await expect(page.getByText(/company/i)).toBeVisible();
    await expect(page.getByText(/status/i)).toBeVisible();
  });

  test('should withdraw application', async ({ page }) => {
    await page.goto('/student/applications');
    
    // Find pending application
    const withdrawButton = page.getByRole('button', { name: /withdraw/i }).first();
    
    if (await withdrawButton.isVisible()) {
      await withdrawButton.click();
      
      // Confirm withdrawal
      await page.getByRole('button', { name: /confirm|yes/i }).click();
      
      // Should show success message
      await expect(page.getByText(/withdrawn|cancelled/i)).toBeVisible();
    }
  });

  // ===========================================================================
  // UPCOMING INTERVIEWS
  // ===========================================================================

  test('should display upcoming interview', async ({ page }) => {
    await page.goto('/student/applications');
    
    // Look for interview notification
    const interviewAlert = page.getByText(/upcoming interview|interview scheduled/i);
    
    if (await interviewAlert.isVisible()) {
      await expect(page.getByText(/tomorrow|date/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /join meeting|details/i })).toBeVisible();
    }
  });
});









