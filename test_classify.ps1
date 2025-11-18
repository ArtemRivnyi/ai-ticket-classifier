# PowerShell script for testing ticket classification
# Usage: .\test_classify.ps1

$baseUrl = "http://localhost:5000"
$apiKey = Read-Host "Enter your API Key (or press Enter to register new)"

# Register if no API key provided
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "`n=== Registering new user ===" -ForegroundColor Cyan
    $registerBody = @{
        email = "test@example.com"
        tier = "professional"
    } | ConvertTo-Json
    
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" `
        -Method Post `
        -Body $registerBody `
        -ContentType "application/json"
    
    $apiKey = $registerResponse.api_key
    Write-Host "API Key: $apiKey" -ForegroundColor Green
}

$headers = @{
    "X-API-Key" = $apiKey
    "Content-Type" = "application/json"
}

# Test tickets
$testTickets = @(
    @{ticket = "I cannot connect to the internet. WiFi shows connected but no websites load."; category = "Network Issue"},
    @{ticket = "I forgot my password and cannot log into my account."; category = "Account Problem"},
    @{ticket = "My credit card was charged twice. I need a refund."; category = "Payment Issue"},
    @{ticket = "Please add dark mode to the application."; category = "Feature Request"},
    @{ticket = "General question about service hours."; category = "Other"}
)

Write-Host "`n=== Testing Classification ===" -ForegroundColor Cyan

foreach ($test in $testTickets) {
    Write-Host "`nTicket: $($test.ticket)" -ForegroundColor Yellow
    Write-Host "Expected: $($test.category)" -ForegroundColor Gray
    
    $body = @{
        ticket = $test.ticket
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/classify" `
            -Method Post `
            -Body $body `
            -Headers $headers
        
        Write-Host "Result: $($response.category)" -ForegroundColor Green
        Write-Host "Confidence: $($response.confidence)" -ForegroundColor Gray
        Write-Host "Provider: $($response.provider)" -ForegroundColor Gray
        
        if ($response.category -eq $test.category) {
            Write-Host "✓ Correct!" -ForegroundColor Green
        } else {
            Write-Host "✗ Mismatch" -ForegroundColor Red
        }
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

Write-Host "`n=== Health Check ===" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get
Write-Host "Status: $($health.status)" -ForegroundColor Green
Write-Host "Version: $($health.version)" -ForegroundColor Gray

Write-Host "`n=== Metrics Summary ===" -ForegroundColor Cyan
$metrics = Invoke-WebRequest -Uri "$baseUrl/metrics" | Select-Object -ExpandProperty Content
$requestCount = ($metrics | Select-String "api_requests_total" | Select-Object -First 1).ToString()
Write-Host $requestCount -ForegroundColor Gray

Write-Host "`n✓ Testing complete!" -ForegroundColor Green
Write-Host "`nView metrics at: http://localhost:9090" -ForegroundColor Cyan
Write-Host "View dashboards at: http://localhost:3000" -ForegroundColor Cyan

