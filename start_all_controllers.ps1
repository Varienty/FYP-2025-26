# Start All Controllers Script
# Launches all 7 controllers for the Student Attendance System
# Press Ctrl+C in this window to stop all controllers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting All Controllers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting controllers..." -ForegroundColor Yellow
Write-Host ""

# Get current directory
$workspaceRoot = Get-Location

# Define controller configurations with absolute paths
$controllers = @(
    @{Name="System Admin"; Path="System Administrator\controller\sysadmin_main.py"; Port=5009},
    @{Name="Student Service Admin"; Path="Student Service Administrator\controller\ssa_main.py"; Port=5008},
    @{Name="Lecturer Auth"; Path="Lecturer\controller\lecturer_auth_controller.py"; Port=5003},
    @{Name="Lecturer Attendance"; Path="Lecturer\controller\lecturer_attendance_controller.py"; Port=5004},
    @{Name="Lecturer Reports"; Path="Lecturer\controller\lecturer_report_controller.py"; Port=5005},
    @{Name="Lecturer Schedule"; Path="Lecturer\controller\lecturer_schedule_controller.py"; Port=5006},
    @{Name="Lecturer Notifications"; Path="Lecturer\controller\lecturer_notification_controller.py"; Port=5007}
)

# Store process IDs globally
$Global:processList = @()

# Start each controller
foreach ($controller in $controllers) {
    Write-Host "► Starting $($controller.Name) on port $($controller.Port)..." -ForegroundColor Cyan
    
    # Build absolute path
    $scriptPath = Join-Path $workspaceRoot $controller.Path
    
    # Start controller - use Start-Process with no new window, track main python.exe
    $process = Start-Process python -ArgumentList "`"$scriptPath`"" -WorkingDirectory $workspaceRoot -PassThru -NoNewWindow
    $Global:processList += $process.Id
    
    Start-Sleep -Milliseconds 800
    
    # Check if process is still running
    $runningProcess = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    if ($runningProcess) {
        Write-Host "  ✓ Started (PID: $($process.Id))" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to start" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Controllers Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Controller Status:" -ForegroundColor Yellow
Write-Host "  • System Admin:           http://localhost:5009" -ForegroundColor White
Write-Host "  • Student Service Admin:  http://localhost:5008" -ForegroundColor White
Write-Host "  • Lecturer Auth:          http://localhost:5003" -ForegroundColor White
Write-Host "  • Lecturer Attendance:    http://localhost:5004" -ForegroundColor White
Write-Host "  • Lecturer Reports:       http://localhost:5005" -ForegroundColor White
Write-Host "  • Lecturer Schedule:      http://localhost:5006" -ForegroundColor White
Write-Host "  • Lecturer Notifications: http://localhost:5007" -ForegroundColor White
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  • System Admin:           file:///$PWD/System Administrator/boundary/dashboard.html" -ForegroundColor Cyan
Write-Host "  • Student Service Admin:  file:///$PWD/Student Service Administrator/boundary/dashboard.html" -ForegroundColor Cyan
Write-Host "  • Lecturer:               file:///$PWD/Lecturer/boundary/dashboard.html" -ForegroundColor Cyan
Write-Host "  • Unified Login:          file:///$PWD/common/login.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  • System Admin:           admin@attendance.com / password" -ForegroundColor White
Write-Host "  • Student Service Admin:  studentservice@attendance.com / password" -ForegroundColor White
Write-Host "  • Lecturer:               john.smith@university.com / password" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all controllers..." -ForegroundColor Yellow
Write-Host ""

# Keep script running and wait for Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 5
    }
} finally {
    Write-Host ""
    Write-Host "Stopping all controllers..." -ForegroundColor Yellow
    
    # Kill all tracked process IDs
    foreach ($pid in $Global:processList) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  ✓ Stopping PID: $pid" -ForegroundColor Green
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Also kill any remaining Python processes on our ports (backup)
    $ports = @(5003, 5004, 5005, 5006, 5007, 5008, 5009)
    foreach ($port in $ports) {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process -and $process.ProcessName -eq "python") {
                Write-Host "  ✓ Stopping remaining process on port $port (PID: $($process.Id))" -ForegroundColor Green
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    Write-Host ""
    Write-Host "All controllers stopped." -ForegroundColor Green
}
