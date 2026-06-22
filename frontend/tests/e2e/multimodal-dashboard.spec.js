import path from "node:path";
import { expect, test } from "@playwright/test";

test("runs multimodal demo workflow and exports a report", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Multimodal Health Risk Digital Twin" })).toBeVisible();
  await expect(page.getByText("This system is for educational and research purposes only").first()).toBeVisible();

  const signalCsv = path.resolve(process.cwd(), "..", "backend", "app", "data", "sample_ppg.csv");
  const reportImage = path.resolve(process.cwd(), "..", "backend", "app", "data", "sample_report.png");

  await page.locator('input[type="file"][accept=".csv,.txt"]').setInputFiles(signalCsv);
  await page
    .locator('input[type="file"][accept=".png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff,.pdf"]')
    .setInputFiles(reportImage);

  await page.getByLabel("Symptoms").fill("Dizziness, fatigue, shortness of breath, and occasional palpitations");
  await page.getByLabel("Lifestyle notes").fill("Low activity, poor sleep, and recent stress.");

  const fusionResponse = page.waitForResponse((response) =>
    response.url().includes("/multimodal-risk") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: /run analysis/i }).click();
  await expect((await fusionResponse).ok()).toBeTruthy();

  await expect(page.getByText(/Low Risk|Mild Risk|Moderate Risk|High Risk/).first()).toBeVisible();
  await expect(page.getByText("Live Digital Twin")).toBeVisible();
  await expect(page.getByText("Alert Status").first()).toBeVisible();
  await expect(page.getByText("Signal Quality Graph")).toBeVisible();
  await expect(page.getByText("Modality Contribution")).toBeVisible();
  await expect(page.getByText("Doctor Summary")).toBeVisible();
  await expect(page.getByText("Patient Explanation")).toBeVisible();
  await expect(page.getByText(/Warning Flags/)).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /download health report/i }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/multimodal_health_risk_report\.(pdf|txt)$/);
});

