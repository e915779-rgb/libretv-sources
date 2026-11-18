# LibreTV 自動更新點播源

本倉庫只維護 LibreTV 點播源資料與 API 可用性檢測，不再包含影视仓、TVBox 或其他聚合播放器配置。

## LibreTV 訂閱資料

- 點播源清單： https://raw.githubusercontent.com/e915779-rgb/libretv-sources/main/sources.json

## 自動化功能

GitHub Actions 每 6 小時執行一次，也可在 Actions 頁面手動執行：

1. 從上游同步有效來源。
2. 最多保留 57 個有效來源，輸出 LibreTV 使用的 sources.json。
3. 檢查各來源 API 的 HTTP 回應及 JSON 格式。
4. 將健康檢測報告保存為 Actions Artifact，保留 30 天。
5. 只有 sources.json 有變更時才提交。

## 上游

https://mylazily.github.io/ziyuanzhan/data/online.json

## 檢測說明

檢測只判斷 API 是否能連線並回傳可解析的 JSON，不代表每個影片都能播放，也不代表影片詳情、播放地址及搜索功能均正常。暫時失敗的來源不會自動刪除，避免網路波動造成誤刪。
