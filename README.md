# LibreTV 自動更新點播源

## 訂閱地址

- LibreTV： https://raw.githubusercontent.com/e915779-rgb/libretv-sources/main/sources.json
- 影视仓 / TVBox： https://raw.githubusercontent.com/e915779-rgb/libretv-sources/main/tvbox.json

## 自動化功能

GitHub Actions 每 6 小時執行一次：
1. 從上游同步來源清單。
2. 重新產生只包含標準 HTTP API（type:1）的 tvbox.json。
3. 對每個 API 發出列表請求（ac=list），檢查 HTTP 回應及 JSON 格式。
4. 產生健康檢測報告，作為 Actions Artifact 保存 30 天。
5. 只有來源清單或 tvbox.json 有變更時才提交。

也可以在 GitHub 的 Actions 頁面手動執行。

## 上游

https://mylazily.github.io/ziyuanzhan/data/online.json

## 檢測規則

檢測只判斷 API 是否能連線並回傳可解析的 JSON，不代表每個影片都能播放，也不代表影片詳情、播放地址及搜索功能均正常。暫時失敗的來源不會自動刪除，避免網路波動造成誤刪。
