# 馮煥曉 Lonny Pang Huan Hsiao — Resume

導演、攝影師、內容創作者，也和 AI 一起寫內容製作工具。

線上版：https://zero5phh-ops.github.io/resume/

五種語言：[中文](https://zero5phh-ops.github.io/resume/) · [English](https://zero5phh-ops.github.io/resume/en.html) · [Bahasa Melayu](https://zero5phh-ops.github.io/resume/ms.html) · [日本語](https://zero5phh-ops.github.io/resume/ja.html) · [한국어](https://zero5phh-ops.github.io/resume/ko.html)

## 結構

每種語言：一個簡單首頁（簡短介紹 + 六個選單卡片），點進去才看細節。

- 首頁：`index.html`（中文）、`en.html`、`ms.html`、`ja.html`、`ko.html`
- 細節頁：`<語言>/software.html`、`sol.html`、`onset.html`、`experience.html`、`awards.html`、`films.html`、`photo.html`、`skills.html`
- 完整履歷（所有內容一頁看完，列印或做 PDF 用）：`<語言>/all.html`

## 更新

不要直接改產生出來的 `.html`。版面在 `build.py` + `src/style.css`，文字在 `i18n/<語言>.json`（zh / en / ms / ja / ko，五份結構相同）。改完執行：

```bash
python3 build.py
```

英文 PDF：用 Chrome 把 `en/all.html` 印成 A4（本機檔案，不放進 repo）。
