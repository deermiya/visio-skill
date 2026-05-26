param(
    [Parameter(Mandatory = $true)]
    [string]$SpecPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Visible,

    [switch]$Diagnostics
)

$ErrorActionPreference = "Stop"

function Convert-HexToRgbFormula {
    param([string]$Hex)
    if ([string]::IsNullOrWhiteSpace($Hex)) { return $null }
    $clean = $Hex.Trim().TrimStart("#")
    if ($clean.Length -ne 6) {
        throw "Color '$Hex' must use #RRGGBB format."
    }
    $r = [Convert]::ToInt32($clean.Substring(0, 2), 16)
    $g = [Convert]::ToInt32($clean.Substring(2, 2), 16)
    $b = [Convert]::ToInt32($clean.Substring(4, 2), 16)
    return "RGB($r,$g,$b)"
}

function Set-FormulaIfPresent {
    param($Shape, [string]$CellName, [string]$Formula)
    if (-not [string]::IsNullOrWhiteSpace($Formula)) {
        $Shape.CellsU($CellName).FormulaU = $Formula
    }
}

function Set-ResultIfPresent {
    param($Shape, [string]$CellName, $Value)
    if ($null -ne $Value) {
        $Shape.CellsU($CellName).ResultIU = [double]$Value
    }
}

function Set-FontSizeIfPresent {
    param($Shape, $Value)
    if ($null -ne $Value) {
        $Shape.CellsU("Char.Size").FormulaU = "$([double]$Value) pt"
    }
}

function Set-FontFamilyIfPresent {
    param($Shape, [string]$FontName)
    if (-not [string]::IsNullOrWhiteSpace($FontName)) {
        $escaped = $FontName.Replace('"', '""')
        $Shape.CellsU("Char.Font").FormulaU = "FONT(""$escaped"")"
    }
}

function Add-Node {
    param($Page, $Node)

    $x = [double]$Node.x
    $y = [double]$Node.y
    $w = if ($null -ne $Node.w) { [double]$Node.w } else { 2.0 }
    $h = if ($null -ne $Node.h) { [double]$Node.h } else { 0.8 }
    $shapeKind = if ($Node.shape) { [string]$Node.shape } else { "rectangle" }

    switch ($shapeKind.ToLowerInvariant()) {
        "ellipse" {
            $shape = $Page.DrawOval($x, $y, $x + $w, $y + $h)
        }
        "diamond" {
            [double[]]$points = @(
                ($x + ($w / 2)), ($y + $h),
                ($x + $w), ($y + ($h / 2)),
                ($x + ($w / 2)), $y,
                $x, ($y + ($h / 2)),
                ($x + ($w / 2)), ($y + $h)
            )
            $shape = $Page.DrawPolyline($points, 0)
        }
        "roundrect" {
            $shape = $Page.DrawRectangle($x, $y, $x + $w, $y + $h)
            Set-FormulaIfPresent $shape "Rounding" "0.15 in"
        }
        default {
            $shape = $Page.DrawRectangle($x, $y, $x + $w, $y + $h)
        }
    }

    if ($Node.text) { $shape.Text = [string]$Node.text }
    Set-FormulaIfPresent $shape "FillForegnd" (Convert-HexToRgbFormula $Node.fill)
    Set-FormulaIfPresent $shape "LineColor" (Convert-HexToRgbFormula $Node.line)
    $fontName = if ($Node.fontName) { [string]$Node.fontName } else { "Microsoft YaHei" }
    $fontSize = if ($null -ne $Node.fontSize) { $Node.fontSize } else { 16 }
    Set-FontFamilyIfPresent $shape $fontName
    Set-FontSizeIfPresent $shape $fontSize
    return $shape
}

function Add-Connection {
    param($Visio, $Page, $ShapesById, $Connection)

    $fromId = [string]$Connection.from
    $toId = [string]$Connection.to
    if (-not $ShapesById.ContainsKey($fromId)) { throw "Connection source '$fromId' was not found." }
    if (-not $ShapesById.ContainsKey($toId)) { throw "Connection target '$toId' was not found." }

    $connector = $Page.Drop($Visio.ConnectorToolDataObject, 0, 0)
    $connector.CellsU("BeginX").GlueTo($ShapesById[$fromId].CellsU("PinX"))
    $connector.CellsU("EndX").GlueTo($ShapesById[$toId].CellsU("PinX"))

    if ($Connection.text) { $connector.Text = [string]$Connection.text }
    Set-FormulaIfPresent $connector "LineColor" (Convert-HexToRgbFormula $Connection.line)
    $fontName = if ($Connection.fontName) { [string]$Connection.fontName } else { "Microsoft YaHei" }
    $fontSize = if ($null -ne $Connection.fontSize) { $Connection.fontSize } else { 16 }
    Set-FontFamilyIfPresent $connector $fontName
    Set-FontSizeIfPresent $connector $fontSize
    $textPinX = if ($null -ne $Connection.textPinX) { [double]$Connection.textPinX } else { 0.35 }
    $textOffsetY = if ($null -ne $Connection.textOffsetY) { [double]$Connection.textOffsetY } else { 0.18 }
    $connector.CellsU("TxtPinX").FormulaU = "Width*$textPinX"
    $connector.CellsU("TxtPinY").FormulaU = "Height*0.5+$textOffsetY in"
    $endArrow = if ($null -ne $Connection.endArrow) { [int]$Connection.endArrow } else { 4 }
    $connector.CellsU("EndArrow").ResultIU = $endArrow
    return $connector
}

$resolvedSpec = Resolve-Path -LiteralPath $SpecPath
$json = Get-Content -LiteralPath $resolvedSpec -Raw -Encoding UTF8 | ConvertFrom-Json
$resolvedOutput = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
$outputDir = Split-Path -Parent $resolvedOutput
if ($outputDir -and -not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

$visio = $null
$doc = $null
try {
    $visio = New-Object -ComObject Visio.Application
    $visio.Visible = [bool]$Visible
    $doc = $visio.Documents.Add("")

    if ($null -ne $json.pages) {
        [object[]]$pages = @($json.pages)
    }
    else {
        [object[]]$pages = @($json)
    }
    for ($i = 0; $i -lt $pages.Count; $i++) {
        $pageSpec = $pages[$i]
        $page = if ($i -eq 0) { $visio.ActivePage } else { $doc.Pages.Add() }
        if ($pageSpec.name) { $page.Name = [string]$pageSpec.name }

        $pageWidth = if ($pageSpec.pageWidth) { $pageSpec.pageWidth } elseif ($json.pageWidth) { $json.pageWidth } else { 11 }
        $pageHeight = if ($pageSpec.pageHeight) { $pageSpec.pageHeight } elseif ($json.pageHeight) { $json.pageHeight } else { 8.5 }
        $page.PageSheet.CellsU("PageWidth").ResultIU = [double]$pageWidth
        $page.PageSheet.CellsU("PageHeight").ResultIU = [double]$pageHeight

        $shapesById = @{}
        foreach ($node in @($pageSpec.nodes)) {
            if (-not $node.id) { throw "Every node must include an id." }
            $shapesById[[string]$node.id] = Add-Node $page $node
        }

        foreach ($connection in @($pageSpec.connections)) {
            Add-Connection $visio $page $shapesById $connection | Out-Null
        }

        if ($Diagnostics) {
            Write-Output "Page '$($page.Name)' has $($page.Shapes.Count) shapes before save."
        }
    }

    $doc.SaveAs($resolvedOutput)
    Write-Output $resolvedOutput
}
finally {
    if ($doc) { $doc.Close() }
    if ($visio) { $visio.Quit() }
}
