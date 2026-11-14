# LibreTV 自動更新點播源

## LibreTV 訂閱地址

https://raw.githubusercontent.com/e915779-rgb/libretv-sources/main/sources.json

## 影视仓 / TVBox 專用配置地址

https://raw.githubusercontent.com/e915779-rgb/libretv-sources/main/tvbox.json

此配置由 `build_tvbox.py` 從 `sources.json` 自動轉換產生。

### Jar / Spider 說明

目前生成的站點全部是標準 HTTP API（`type: 1`），不使用 `type: 3` 的 Spider 爬蟲站點，因此配置刻意不指定全域 `spider` JAR，也不會為了消除提示而載入未驗證的第三方 JAR。

若影視倉顯示「Jar 接口加載失敗」，這不代表這些 `type: 1` API 站點本身需要 JAR。請先確認影視倉的精確版本，以及錯誤是否來自 App 的獨立 Jar 接口設定。

### 自動更新

GitHub Actions 每 6 小時更新一次上游來源，並重新產生 `tvbox.json`。
支援手動執行 workflow。

上游資料：
https://mylazily.github.io/ziyuanzhan/data/online.json

LibreTV SourceList version 2。
來源收錄不代表每個 API 都能正常播放。
成人來源使用 `isAdult` 標記。
