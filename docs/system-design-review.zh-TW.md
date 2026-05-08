# pptx-design-md 系統設計審查（繁體中文）

## 1. 系統總覽
`pptx-design-md` 是前後端分離系統，將 `.pptx` 簡報轉換為：
- `design.md`（給 LLM 使用的設計規範）
- `analysis.json`（結構化分析結果）

主要流程：
1. 使用者透過 Web UI 或 CLI 上傳一個或多個 `.pptx`。
2. 後端驗證檔案類型、內容與大小限制。
3. 解析流程擷取投影片元素並執行啟發式推論。
4. 回傳 analysis 與產生的 markdown。
5. 選擇性落地儲存執行結果到 `backend/runs/<run_id>/`。

---

## 2. 架構說明

### 2.1 核心元件
- 前端（靜態頁面）：`frontend/index.html`、`frontend/app.js`、`frontend/styles.css`
- 後端 API（FastAPI）：`backend/app/main.py`
- 解析與推論引擎：
  - 解析：`backend/app/extractor.py`（python-pptx）
  - 啟發式：`backend/app/heuristics.py`
  - Markdown 組裝：`backend/app/design_md.py`
- 資料模型契約：`backend/app/models.py`
- 結果儲存：`backend/app/storage.py`
- CLI：`backend/app/cli.py`

### 2.2 請求路徑
1. `POST /extract` 或 `POST /extract/batch`
2. `_read_validated_pptx_upload` 進行驗證：
   - 副檔名檢查
   - content-type 檢查
   - 上傳大小限制
   - ZIP signature 檢查（`PK`）
3. 將檔案寫入暫存 `.pptx`
4. `extract_pptx(...)` 產生 `DeckAnalysis`
5. `generate_design_md(...)` 產出可給 LLM 的文本
6. `save_run(...)` 持久化並回傳 `run_id`

### 2.3 儲存模型
- MVP 採用檔案系統儲存（而非 DB）。
- 每次執行一個資料夾：
  - `design.md`
  - `analysis.json`
  - `meta.json`
  - 可選 `design.edited.md`

此設計的目標是降低 MVP 初期複雜度與維運門檻。

---

## 3. 資料結構選型與取捨

### 3.1 使用 Pydantic 模型做 API 與分析契約
**目前選擇：** 巢狀 Pydantic 模型（`DeckAnalysis`、`SlideAnalysis`、`ElementAnalysis` 等）

**為什麼這樣選：**
- API 回應結構具備強型別與一致性。
- 抽取器、markdown 生成器、前端之間的資料契約清楚。
- 比鬆散 dict 更容易演進，且可及早發現 schema 偏移。

**替代方案：**
1. 純 dict
   - 優點：快速、輕量
   - 缺點：型別安全弱，重構容易出錯
2. 僅 dataclass
   - 優點：結構清楚、輕量
   - 缺點：runtime 驗證與 API 序列化保障不如 Pydantic

---

### 3.2 投影片/元素用 `list`，統計排名用 `Counter`
**目前選擇：**
- `list`：保留順序的 `slides`、`elements`
- `Counter`：字型/顏色/元件簽章的頻率排名

**為什麼這樣選：**
- 投影片順序本身有語意。
- 啟發式規則常以順序掃描元素。
- `Counter` 非常適合做「主導風格」頻率排序。

**替代方案：**
1. NumPy / DataFrame 管線
   - 優點：向量化統計強
   - 缺點：依賴與複雜度提高，對 MVP 偏重
2. 每頁建空間索引樹
   - 優點：幾何查詢更快
   - 缺點：目前資料量下性價比不高

---

### 3.3 Bounding box 同時存英吋與百分比
**目前選擇：** 每個元素儲存 `inches` 與 `%`。

**為什麼這樣選：**
- 英吋保留 PPT 座標精度，利於除錯。
- 百分比可跨畫布尺寸做版面規則泛化。
- 同時服務精準分析與可遷移設計建議。

**替代方案：**
1. 只存英吋
   - 優點：簡單
   - 缺點：跨尺寸遷移能力弱
2. 只存百分比
   - 優點：標準化容易
   - 缺點：失去精準數值對照能力

---

### 3.4 間距/錨點使用容差分群（clustered values）
**目前選擇：** 以容差做浮點分群，推估 margin/gap/anchor。

**為什麼這樣選：**
- 對手工排版造成的微小誤差有韌性。
- 輸出可讀性高，利於人與 LLM 使用。
- 不需導入重型 ML 依賴。

**替代方案：**
1. K-means
   - 優點：正式分群方法
   - 缺點：需調參，解釋性較弱
2. 固定 histogram bins
   - 優點：實作簡單
   - 缺點：邊界脆弱、語意穩定性較差

---

### 3.5 MVP 使用檔案系統儲存 run，而非資料庫
**目前選擇：** `backend/runs/` 本地落地儲存。

**為什麼這樣選：**
- 上線速度快。
- 便於人工檢查與除錯。
- 初期不需承擔 DB 架構與維運成本。

**替代方案：**
1. RDB + 物件儲存
   - 優點：可查詢性、可擴充性較佳
   - 缺點：建置與維運成本高
2. Redis-only
   - 優點：快速
   - 缺點：不適合長期保存產物

---

## 4. 架構取捨

### 4.1 優勢
- 模組邊界清楚：API / 解析 / 啟發式 / 生成 / 儲存。
- 檔案上傳有基本安全防護（型別/大小/signature）。
- 啟發式可解釋、可審查（比黑盒 ML 更可控）。
- 後端有測試覆蓋，回歸風險可控。

### 4.2 目前限制
- 解析偏同步 CPU 工作，高併發下有瓶頸。
- 本地檔案儲存不適合多實例部署。
- 對複雜簡報（母片繼承、SmartArt、群組）仍有 underfit 風險。
- API 為安全而做錯誤訊息收斂，除錯資訊較少。

### 4.3 為何對 MVP 合理
- 產品目標是「設計抽象」而非「完整還原」。
- 複雜度控制良好，迭代速度快。
- 具備清楚的後續擴充路徑，不需推倒重來。

---

## 5. 可擴充節點
1. 以工作佇列解耦解析（Celery/RQ + workers）。
2. 將 run 儲存改為 S3 相容儲存 + metadata DB。
3. 以 feature flag 支援多種啟發式策略。
4. 增加每條規則的可解釋證據區塊。
5. 增加投影片縮圖與版面 overlay 供人工 QA。

---

## 6. Deep Dive 問答準備（含回答方向）

### Q1. 為什麼不用 ML 直接做版面/角色推論？
**回答方向：**
- MVP 重視可解釋與可預測。
- 啟發式延遲低、依賴少、可審核。
- 後續可把 ML 當加分器，不需取代現有核心。

### Q2. 如何避免 schema drift？
**回答方向：**
- 用 Pydantic 統一契約。
- API / extractor / markdown 同用一套模型。
- 測試覆蓋序列化與關鍵路徑。

### Q3. 高併發上傳時的風險是什麼？
**回答方向：**
- 解析為 CPU/記憶體密集，現況為同步處理。
- 目前靠檔案大小與 batch 限制先控風險。
- 擴充方案：佇列化、限流、水平擴展。

### Q4. 為什麼同時保存 `analysis.json` 與 `design.md`？
**回答方向：**
- `analysis.json` 提供機器可重現與下游工具串接。
- `design.md` 提供人與 LLM 直接使用。
- 雙輸出兼顧可觀測性與產品可用性。

### Q5. 為什麼 bbox 要存兩種單位？
**回答方向：**
- 英吋：精準除錯與對照。
- 百分比：跨畫布泛化能力。

### Q6. 若要達企業級治理要補什麼？
**回答方向：**
- 認證授權、多租戶隔離、加密儲存。
- 稽核日誌與保留策略。
- run 存取改為簽名 URL / 權限控管。

### Q7. 非像素級還原，怎麼判斷是否「正確」？
**回答方向：**
- 指標不是視覺像素一致，而是設計語言可遷移性。
- 看 token/layout 推論一致性與生成新頁面的可用度。

### Q8. 現在最大的資料結構瓶頸是什麼？
**回答方向：**
- 元素多時仍需多次線性掃描。
- 若規模上升可加入每頁空間索引。

### Q9. 若目標 1000 decks/hour，前三步？
**回答方向：**
1. 佇列化 + worker 池。
2. 外部儲存與 metadata DB。
3. 觀測指標（p95 解析時間、錯誤分類、佇列延遲）。

### Q10. 為何這套架構適合小團隊維護？
**回答方向：**
- 依賴少、邊界清楚、測試可驗證。
- 每個模組都可獨立演進與替換。

---

## 7. 建議練習題
- 逐步走讀一次 `/extract` 請求生命週期。
- 針對 confidence diagnostics 做 failure case 討論。
- 設計本地檔案儲存到雲端物件儲存的遷移方案。
- 討論 `analysis` schema 版本化與向後相容策略。
