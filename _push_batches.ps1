$ErrorActionPreference = 'Continue'
Set-Location 'D:\AAA\text\假钦差\短剧'
$env:GIT_TERMINAL_PROMPT = '0'

$batches = @(
  @{ msg = '分镜图：第01集 18 张（768×1344）'; paths = @('03_图片\第01集') },
  @{ msg = '分镜图：第02集 18 张'; paths = @('03_图片\第02集') },
  @{ msg = '分镜图：第03集 18 张'; paths = @('03_图片\第03集') },
  @{ msg = '参考图库（上）：人物与场景定型图'; paths = @() },
  @{ msg = '参考图库（下）+ 封面 + 素材根级测试帧'; paths = @('06_素材\封面') }
)

foreach ($b in $batches) {
  if ($b.paths.Count -eq 0) {
    # 参考库分两半：按文件名排序取前 19 / 后 18
    $files = Get-ChildItem '06_素材\参考库' -File | Sort-Object Name
    $half = [math]::Ceiling($files.Count / 2)
    $pick = $files | Select-Object -First $half
    foreach ($f in $pick) { git add ("06_素材/参考库/" + $f.Name) }
  } else {
    foreach ($p in $b.paths) { git add $p }
  }
  if ($b.msg -like '*根级*') {
    Get-ChildItem '06_素材' -File -Include *.png | ForEach-Object { git add ("06_素材/" + $_.Name) }
    Get-ChildItem '05_成片' -File -Include *.ass,*.srt,*.json | ForEach-Object { git add ("05_成片/" + $_.Name) }
  }
  $staged = (git diff --cached --name-only | Measure-Object).Count
  if ($staged -eq 0) { Write-Output "[skip] $($b.msg) 无新文件"; continue }
  git -c core.quotepath=false commit -q -m $b.msg
  Write-Output "[commit] $($b.msg) 文件 $staged"
  for ($i = 1; $i -le 3; $i++) {
    git push origin main 2>&1 | Out-File -Append _push.log -Encoding utf8
    if ($LASTEXITCODE -eq 0) { Write-Output "[push ok] $($b.msg)"; break }
    Write-Output "[push retry $i] $($b.msg)"
    Start-Sleep -Seconds (10 * $i)
  }
}
Write-Output "[done]"
git log --oneline | Select-Object -First 8
git status --porcelain | Measure-Object | ForEach-Object { "未提交剩余: $($_.Count)" }
