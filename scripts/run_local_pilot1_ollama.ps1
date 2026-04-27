param(
    [string]$Model = "qwen2.5-coder:3b",
    [string]$GoldPath = "data/processed/crn_pilot100.jsonl",
    [string]$PromptDir = "prompts/crn_pilot100",
    [string]$PredictionPrefix = "crn_pilot100_qwen25coder3b",
    [string]$ReportDir = "reports/crn_pilot100_qwen25coder3b",
    [string]$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
)

$ErrorActionPreference = "Stop"

function Get-LineCount {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return 0
    }
    return (Get-Content $Path | Measure-Object -Line).Lines
}

function Ensure-OllamaServer {
    if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 11434 -WarningAction SilentlyContinue).TcpTestSucceeded) {
        return
    }
    Start-Process -FilePath $OllamaExe -ArgumentList "serve"
    Start-Sleep -Seconds 5
    if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 11434 -WarningAction SilentlyContinue).TcpTestSucceeded) {
        throw "Ollama server did not start on 127.0.0.1:11434"
    }
}

function Run-Baseline {
    param(
        [string]$Baseline,
        [string]$PromptPath,
        [string]$OutputPath
    )

    while ((Get-LineCount $OutputPath) -lt 100) {
        $before = Get-LineCount $OutputPath
        Write-Host "Running $Baseline (current lines=$before)"
        python scripts/run_local_predictions.py `
            --input $PromptPath `
            --output $OutputPath `
            --model $Model `
            --backend ollama `
            --timeout-seconds 900 `
            --resume
        $after = Get-LineCount $OutputPath
        Write-Host "Finished pass for $Baseline (lines=$after)"
        if ($after -le $before) {
            throw "Baseline $Baseline did not make progress; stopping to avoid an infinite loop."
        }
    }
}

function Invoke-BootstrapGain {
    param(
        [string]$PerExamplePath,
        [string]$BaselineA,
        [string]$BaselineB,
        [string]$Metric
    )

    $args = @(
        "scripts/bootstrap_gain.py",
        "--per-example", $PerExamplePath,
        "--baseline-a", $BaselineA,
        "--baseline-b", $BaselineB,
        "--metric", $Metric,
        "--iters", "1000",
        "--seed", "42"
    )
    return (& python @args | Out-String).TrimEnd()
}

function Write-GainSummary {
    param([string]$PerExamplePath, [string]$OutputPath)

    $reviewGain = Invoke-BootstrapGain -PerExamplePath $PerExamplePath -BaselineA "no_review" -BaselineB "direct" -Metric "exact_match_line_trim"
    $goldGain = Invoke-BootstrapGain -PerExamplePath $PerExamplePath -BaselineA "direct" -BaselineB "gold_location" -Metric "exact_match_line_trim"
    $reviewLoc = Invoke-BootstrapGain -PerExamplePath $PerExamplePath -BaselineA "no_review" -BaselineB "direct" -Metric "location_overlap_f1"
    $goldLoc = Invoke-BootstrapGain -PerExamplePath $PerExamplePath -BaselineA "direct" -BaselineB "gold_location" -Metric "location_overlap_f1"

    @(
        '# Gain Summary',
        '',
        '## direct - no_review on exact_match_line_trim',
        '```text',
        $reviewGain,
        '```',
        '',
        '## gold_location - direct on exact_match_line_trim',
        '```text',
        $goldGain,
        '```',
        '',
        '## direct - no_review on location_overlap_f1',
        '```text',
        $reviewLoc,
        '```',
        '',
        '## gold_location - direct on location_overlap_f1',
        '```text',
        $goldLoc,
        '```'
    ) | Set-Content -Path $OutputPath -Encoding UTF8
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Ensure-OllamaServer

$noReviewPath = "predictions/${PredictionPrefix}_no_review.jsonl"
$directPath = "predictions/${PredictionPrefix}_direct.jsonl"
$goldPath = "predictions/${PredictionPrefix}_gold_location.jsonl"
$mergedPath = "predictions/${PredictionPrefix}.jsonl"

Run-Baseline -Baseline "no_review" -PromptPath "$PromptDir/no_review_prompts.jsonl" -OutputPath $noReviewPath
Run-Baseline -Baseline "direct" -PromptPath "$PromptDir/direct_prompts.jsonl" -OutputPath $directPath
Run-Baseline -Baseline "gold_location" -PromptPath "$PromptDir/gold_location_prompts.jsonl" -OutputPath $goldPath

Get-Content $noReviewPath, $directPath, $goldPath | Set-Content -Path $mergedPath -Encoding UTF8

python scripts/evaluate_predictions.py --gold $GoldPath --pred $mergedPath --outdir $ReportDir

$perExamplePath = "$ReportDir/per_example_metrics.csv"
$gainSummaryPath = "$ReportDir/gain_summary.md"
$errorSamplePath = "$ReportDir/error_analysis_sample.csv"

Write-GainSummary -PerExamplePath $perExamplePath -OutputPath $gainSummaryPath

python scripts/make_error_analysis_sample.py `
    --per-example $perExamplePath `
    --gold $GoldPath `
    --pred $mergedPath `
    --output $errorSamplePath `
    --max-per-group 10 `
    --seed 42

Write-Host "Local Pilot 1 run completed."
