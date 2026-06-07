# Master Deployment Script: Inbox Analytics Manager Stack
# --------------------------------------------------
$PROJECT_ID = gcloud config get-value project
$REGION = if ($env:CHOSEN_REGION) { $env:CHOSEN_REGION } else { "us-central1" }
$IMAGE = "$REGION-docker.pkg.dev/$PROJECT_ID/agent-repo/inbox-analytics-agent:latest"

Write-Host "[*] Project: $PROJECT_ID | Region: $REGION" -ForegroundColor Cyan

# 1. Build and Push Container
Write-Host "[*] Building container image..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE .

# 2. Deploy to Cloud Run
Write-Host "[*] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy inbox-analytics-agent `
    --image $IMAGE `
    --platform managed --region $REGION --allow-unauthenticated `
    --memory 2Gi --cpu 1 `
    --set-env-vars="MONGO_URI=$($env:MONGO_URI),VOYAGE_API_KEY=$($env:VOYAGE_API_KEY),PROJECT_ID=$PROJECT_ID"

# 3. Final Sync
$service_info = gcloud run services describe inbox-analytics-agent --platform managed --region $REGION
$service_info_str = $service_info -join "`n"
if ($service_info_str -match "URL:\s+(https?://\S+)") {
    $SERVICE_URL = $Matches[1]
}
Write-Host "`n[*] Inbox Analytics Agent URL: $($SERVICE_URL)" -ForegroundColor Green
