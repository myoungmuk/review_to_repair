param(
    [string]$Model = "qwen2.5-coder:3b",
    [string]$Backend = "ollama",
    [string]$Prefix = "crn_pilot100_qwen25coder3b",
    [string]$BaseUrl = "",
    [int]$Seed = 42,
    [double]$Temperature = 0.0,
    [double]$TimeoutSeconds = 300.0
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot | Split-Path -Parent)

function Count-Lines {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return 0
    }
    return (Get-Content $Path | Measure-Object -Line).Lines
}

function Invoke-RunnerUntilComplete {
    param(
        [string]$Baseline,
        [string]$PromptPath,
        [string]$OutputPath,
        [string]$ErrorPath
    )

    while ((Count-Lines $OutputPath) -lt 100) {
        Write-Host "Running $Baseline. Current lines: $(Count-Lines $OutputPath)"
        $args = @(
            "scripts/run_local_predictions.py",
            "--input", $PromptPath,
            "--output", $OutputPath,
            "--model", $Model,
            "--backend", $Backend,
            "--temperature", "$Temperature",
            "--seed", "$Seed",
            "--timeout-seconds", "$TimeoutSeconds",
            "--resume",
            "--continue-on-error",
            "--error-log", $ErrorPath
        )
        if ($BaseUrl) {
            $args += @("--base-url", $BaseUrl)
        }

        try {
            & python @args
        }
        catch {
            Write-Host "Runner exited with an exception for $Baseline. Retrying..." -ForegroundColor Yellow
        }

        Start-Sleep -Seconds 2
    }

    Write-Host "$Baseline complete: $(Count-Lines $OutputPath) lines"
}

$reportDir = "reports/$Prefix"
$predictionDir = "predictions"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$noReviewPath = "$predictionDir/${Prefix}_no_review.jsonl"
$directPath = "$predictionDir/${Prefix}_direct.jsonl"
$goldPath = "$predictionDir/${Prefix}_gold_location.jsonl"

Invoke-RunnerUntilComplete -Baseline "no_review" -PromptPath "prompts/crn_pilot100/no_review_prompts.jsonl" -OutputPath $noReviewPath -ErrorPath "$reportDir/no_review_errors.jsonl"
Invoke-RunnerUntilComplete -Baseline "direct" -PromptPath "prompts/crn_pilot100/direct_prompts.jsonl" -OutputPath $directPath -ErrorPath "$reportDir/direct_errors.jsonl"
Invoke-RunnerUntilComplete -Baseline "gold_location" -PromptPath "prompts/crn_pilot100/gold_location_prompts.jsonl" -OutputPath $goldPath -ErrorPath "$reportDir/gold_location_errors.jsonl"

$mergedPath = "$predictionDir/$Prefix.jsonl"
Get-Content $noReviewPath, $directPath, $goldPath | Set-Content -Encoding utf8 $mergedPath

& python scripts/evaluate_predictions.py --gold data/processed/crn_pilot100.jsonl --pred $mergedPath --outdir $reportDir

$gainSummaryPath = "$reportDir/gain_summary.md"
$sections = @()
$gainCommands = @(
    @("direct - no_review exact_match_line_trim", @("scripts/bootstrap_gain.py","--per-example","$reportDir/per_example_metrics.csv","--baseline-a","no_review","--baseline-b","direct","--metric","exact_match_line_trim","--iters","1000","--seed","$Seed")),
    @("gold_location - direct exact_match_line_trim", @("scripts/bootstrap_gain.py","--per-example","$reportDir/per_example_metrics.csv","--baseline-a","direct","--baseline-b","gold_location","--metric","exact_match_line_trim","--iters","1000","--seed","$Seed")),
    @("direct - no_review location_overlap_f1", @("scripts/bootstrap_gain.py","--per-example","$reportDir/per_example_metrics.csv","--baseline-a","no_review","--baseline-b","direct","--metric","location_overlap_f1","--iters","1000","--seed","$Seed")),
    @("gold_location - direct location_overlap_f1", @("scripts/bootstrap_gain.py","--per-example","$reportDir/per_example_metrics.csv","--baseline-a","direct","--baseline-b","gold_location","--metric","location_overlap_f1","--iters","1000","--seed","$Seed"))
)

$gainLines = @("# Gain Summary", "")
foreach ($pair in $gainCommands) {
    $title = $pair[0]
    $cmdArgs = $pair[1]
    $out = & python @cmdArgs | Out-String
    $gainLines += "## $title"
    $gainLines += ""
    $gainLines += "```text"
    $gainLines += $out.TrimEnd()
    $gainLines += "```"
    $gainLines += ""
}
$gainLines += "Interpretation should be cautious and snippet-level only."
$gainLines += "Use 'suggests' or 'is consistent with' rather than strong causal claims."
Set-Content -Encoding utf8 $gainSummaryPath $gainLines

& python scripts/make_error_analysis_sample.py --per-example "$reportDir/per_example_metrics.csv" --gold data/processed/crn_pilot100.jsonl --pred $mergedPath --output "$reportDir/error_analysis_sample.csv" --max-per-group 10 --seed $Seed

Write-Host "Pilot 1 local pipeline completed."
