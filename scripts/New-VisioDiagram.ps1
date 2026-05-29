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

$script:StencilLookup = $null

function Resolve-StencilPath {
    param($Visio, [string]$FileOrPath)
    # 完整路径直接用
    if (Test-Path -LiteralPath $FileOrPath) { return (Resolve-Path -LiteralPath $FileOrPath).Path }

    # 懒加载路径索引（首次扫描 VISIO CONTENT 建缓存，30天有效）
    if ($null -eq $script:StencilLookup) {
        $cacheFile = Join-Path $env:TEMP 'visio-stencil-paths.json'
        $rebuild = $true
        if (Test-Path -LiteralPath $cacheFile) {
            $age = (Get-Date) - (Get-Item $cacheFile).LastWriteTime
            if ($age.TotalDays -lt 30) {
                try {
                    $obj = Get-Content $cacheFile -Raw -Encoding UTF8 | ConvertFrom-Json
                    $script:StencilLookup = @{}
                    foreach ($p in $obj.PSObject.Properties) { $script:StencilLookup[$p.Name] = $p.Value }
                    $rebuild = $false
                } catch { $rebuild = $true }
            }
        }
        if ($rebuild) {
            $content = Join-Path $Visio.Path 'VISIO CONTENT'
            $script:StencilLookup = @{}
            Get-ChildItem -Path $content -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -in '.vssx','.vss','.vssm' } |
                ForEach-Object { $script:StencilLookup[$_.Name.ToUpperInvariant()] = $_.FullName }
            $script:StencilLookup | ConvertTo-Json -Compress |
                Set-Content -LiteralPath $cacheFile -Encoding UTF8
        }
    }

    $key = (Split-Path -Leaf $FileOrPath).ToUpperInvariant()
    if ($script:StencilLookup.ContainsKey($key)) { return $script:StencilLookup[$key] }
    throw "Stencil '$FileOrPath' not found. Delete '$env:TEMP\visio-stencil-paths.json' to rebuild cache."
}

function Add-Node {
    param($Page, $Node, $StencilsById)

    # 模具图标分支：声明了 stencil + master 时，从模具 Drop 真实图标，而不是画几何形状
    if ($Node.stencil -and $Node.master) {
        $stencilId = [string]$Node.stencil
        if ($null -eq $StencilsById -or -not $StencilsById.ContainsKey($stencilId)) {
            throw "Node references stencil '$stencilId' not declared in top-level 'stencils' array."
        }
        $stencilDoc = $StencilsById[$stencilId]
        $masterName = [string]$Node.master
        $master = $null
        try { $master = $stencilDoc.Masters.ItemU($masterName) } catch { }   # 先按通用名(NameU)
        if ($null -eq $master) { try { $master = $stencilDoc.Masters.Item($masterName) } catch { } } # 再按显示名(Name)
        if ($null -eq $master) { throw "Master '$masterName' not found in stencil '$stencilId'." }
        $shape = $Page.Drop($master, [double]$Node.x, [double]$Node.y)  # x,y 为图标中心点
        if ($Node.text) { $shape.Text = [string]$Node.text }
        if ($null -ne $Node.w) { $shape.CellsU("Width").ResultIU = [double]$Node.w }
        if ($null -ne $Node.h) { $shape.CellsU("Height").ResultIU = [double]$Node.h }
        return $shape
    }

    $x = [double]$Node.x
    $y = [double]$Node.y
    $w = if ($null -ne $Node.w) { [double]$Node.w } else { 2.0 }
    $h = if ($null -ne $Node.h) { [double]$Node.h } else { 0.8 }
    $shapeKind = if ($Node.shape) { [string]$Node.shape } else { "roundrect" }

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
    $fillColor = if ($Node.fill) { [string]$Node.fill } else { "#EFF6FF" }
    $lineColor = if ($Node.line) { [string]$Node.line } else { "#3B82F6" }
    Set-FormulaIfPresent $shape "FillForegnd" (Convert-HexToRgbFormula $fillColor)
    Set-FormulaIfPresent $shape "LineColor" (Convert-HexToRgbFormula $lineColor)
    $fontName = if ($Node.fontName) { [string]$Node.fontName } else { "Microsoft YaHei" }
    $fontSize = if ($null -ne $Node.fontSize) { $Node.fontSize } else { 11 }
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
    $connLine = if ($Connection.line) { [string]$Connection.line } else { "#475569" }
    Set-FormulaIfPresent $connector "LineColor" (Convert-HexToRgbFormula $connLine)
    $fontName = if ($Connection.fontName) { [string]$Connection.fontName } else { "Microsoft YaHei" }
    $fontSize = if ($null -ne $Connection.fontSize) { $Connection.fontSize } else { 10 }
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

function Get-ActorTypeColors {
    param([string]$Type)
    switch ($Type.ToLowerInvariant()) {
        "actor"    { return @{ Fill = "#EFF6FF"; Line = "#3B82F6" } }
        "system"   { return @{ Fill = "#F5F3FF"; Line = "#8B5CF6" } }
        "database" { return @{ Fill = "#FEF3C7"; Line = "#D97706" } }
        "external" { return @{ Fill = "#ECFDF5"; Line = "#10B981" } }
        default    { return @{ Fill = "#EFF6FF"; Line = "#3B82F6" } }
    }
}

function Add-SequenceDiagram {
    param($Visio, $Page, $Spec)

    $actors = @($Spec.actors)
    $messages = @($Spec.messages)
    $layout = $Spec.layout

    # Default layout values
    $actorSpacing = if ($layout.actorSpacing) { [double]$layout.actorSpacing } else { 3.0 }
    $messageSpacing = if ($layout.messageSpacing) { [double]$layout.messageSpacing } else { 0.6 }
    $startY = if ($layout.startY) { [double]$layout.startY } else { 8.0 }
    $lifelineHeight = if ($layout.lifelineHeight) { [double]$layout.lifelineHeight } else { 6.0 }

    $actorBoxWidth = 1.6
    $actorBoxHeight = 0.6
    $lifelineWidth = 0.02
    $activationWidth = 0.15

    # Calculate starting X position to center the diagram
    $totalWidth = ($actors.Count - 1) * $actorSpacing + $actorBoxWidth
    $startX = 1.0

    # Track actor positions and shapes
    $actorData = @{}
    $activationStack = @{}  # Track activation depth for each actor

    # Draw actors and lifelines
    for ($i = 0; $i -lt $actors.Count; $i++) {
        $actor = $actors[$i]
        $actorId = [string]$actor.id
        $centerX = $startX + ($i * $actorSpacing)
        $boxX = $centerX - ($actorBoxWidth / 2)
        $boxY = $startY - $actorBoxHeight

        # Get colors
        $colors = Get-ActorTypeColors $actor.type
        $fillColor = if ($actor.fill) { [string]$actor.fill } else { $colors.Fill }
        $lineColor = if ($actor.line) { [string]$actor.line } else { $colors.Line }

        # Draw actor box
        $actorBox = $Page.DrawRectangle($boxX, $boxY, $boxX + $actorBoxWidth, $boxY + $actorBoxHeight)
        $actorBox.Text = if ($actor.name) { [string]$actor.name } else { $actorId }
        Set-FormulaIfPresent $actorBox "FillForegnd" (Convert-HexToRgbFormula $fillColor)
        Set-FormulaIfPresent $actorBox "LineColor" (Convert-HexToRgbFormula $lineColor)
        Set-FontFamilyIfPresent $actorBox "Microsoft YaHei"
        Set-FontSizeIfPresent $actorBox 10

        # Draw lifeline (dashed vertical line)
        $lifelineX = $centerX - ($lifelineWidth / 2)
        $lifelineBottom = $boxY - $lifelineHeight
        $lifeline = $Page.DrawLine($centerX, $boxY, $centerX, $lifelineBottom)
        $lifeline.CellsU("LinePattern").ResultIU = 2  # Dashed line
        Set-FormulaIfPresent $lifeline "LineColor" (Convert-HexToRgbFormula "#94A3B8")
        $lifeline.CellsU("LineWeight").FormulaU = "0.5 pt"

        $actorData[$actorId] = @{
            CenterX = $centerX
            BoxY = $boxY
            LifelineBottom = $lifelineBottom
            Box = $actorBox
            Lifeline = $lifeline
        }

        $activationStack[$actorId] = @()
    }

    # Draw messages
    $currentY = $startY - $actorBoxHeight - 0.3

    foreach ($msg in $messages) {
        $fromId = [string]$msg.from
        $toId = [string]$msg.to

        if (-not $actorData.ContainsKey($fromId)) { throw "Message source '$fromId' not found in actors." }
        if (-not $actorData.ContainsKey($toId)) { throw "Message target '$toId' not found in actors." }

        $fromX = $actorData[$fromId].CenterX
        $toX = $actorData[$toId].CenterX
        $msgType = if ($msg.type) { [string]$msg.type } else { "sync" }

        # Draw message arrow
        $arrow = $Page.DrawLine($fromX, $currentY, $toX, $currentY)

        if ($msg.text) {
            $arrow.Text = [string]$msg.text
            $arrow.CellsU("TxtPinX").FormulaU = "Width*0.5"
            $arrow.CellsU("TxtPinY").FormulaU = "Height*0.5+0.15 in"
        }

        Set-FormulaIfPresent $arrow "LineColor" (Convert-HexToRgbFormula "#475569")
        Set-FontFamilyIfPresent $arrow "Microsoft YaHei"
        Set-FontSizeIfPresent $arrow 9

        # Set arrow style based on message type
        if ($msgType -eq "return") {
            $arrow.CellsU("LinePattern").ResultIU = 2  # Dashed
            $arrow.CellsU("EndArrow").ResultIU = 1     # Simple arrow
        } else {
            $arrow.CellsU("EndArrow").ResultIU = 4     # Filled arrow
        }

        $currentY -= $messageSpacing
    }
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

    # Check if this is a sequence diagram
    $diagramType = if ($json.type) { [string]$json.type } else { "standard" }

    if ($diagramType -eq "sequence") {
        # Handle sequence diagram
        $page = $visio.ActivePage
        if ($json.title) { $page.Name = [string]$json.title }

        $pageWidth = if ($json.pageWidth) { [double]$json.pageWidth } else { 11 }
        $pageHeight = if ($json.pageHeight) { [double]$json.pageHeight } else { 8.5 }
        $page.PageSheet.CellsU("PageWidth").ResultIU = $pageWidth
        $page.PageSheet.CellsU("PageHeight").ResultIU = $pageHeight

        Add-SequenceDiagram $visio $page $json

        if ($Diagnostics) {
            Write-Output "Sequence diagram '$($page.Name)' has $($page.Shapes.Count) shapes."
        }
    }
    else {
        # Handle standard diagrams (original logic)
        # 先打开 spec 里声明的所有模具：自动解析路径 + 隐藏只读方式加载(flag 66 = 只读2 + 隐藏64)
        $stencilsById = @{}
        foreach ($s in @($json.stencils)) {
            if (-not $s.id) { throw "Every stencil entry must include an id." }
            $stencilPath = Resolve-StencilPath $visio ([string]$s.file)
            $stencilsById[[string]$s.id] = $visio.Documents.OpenEx($stencilPath, 66)
            if ($Diagnostics) { Write-Output "Opened stencil '$($s.id)' -> $stencilPath" }
        }
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
                $shapesById[[string]$node.id] = Add-Node $page $node $stencilsById
            }

            foreach ($connection in @($pageSpec.connections)) {
                Add-Connection $visio $page $shapesById $connection | Out-Null
            }

            if ($Diagnostics) {
                Write-Output "Page '$($page.Name)' has $($page.Shapes.Count) shapes before save."
            }
        }
    }

    $doc.SaveAs($resolvedOutput)
    Write-Output $resolvedOutput
}
finally {
    if ($doc) { $doc.Close() }
    if ($visio) { $visio.Quit() }
}
