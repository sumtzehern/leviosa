# 🧠 Leviosa AI – Intelligent Document Parser with Layout-Aware Markdown Conversion

Leviosa AI is a full-stack document understanding tool that takes scanned PDFs or images, performs layout-aware OCR, and transforms them into clean, structured Markdown — ready to read, edit, or export.

Built to explore **OCR + LLM integration** with a focus on **real-world layout parsing**, **modular AI pipelines**, and **clean UX**.

![demo-gif](demo.gif) <!-- Optional: Insert Loom or screen recording here -->

---

## ✨ Key Features

✅ **Drag-and-Drop Upload** — supports `.pdf`, `.jpg`, `.png`  
✅ **Layout-Aware OCR** — powered by [PaddleOCR PPStructure]  
✅ **LLM-Powered Markdown Conversion** — uses GPT-4o for structured output  
✅ **Real-Time UI** — split-screen PDF viewer + editable Markdown display  
✅ **Custom Prompt Support** — guide GPT to follow specific formatting styles  
✅ **Multi-Page Support** — handles long PDFs with progress tracking  
✅ **Download Options** — export as `.md`, `.txt`, and soon `.json`

---

## 🧱 Tech Stack

**Frontend**: React, TypeScript, Tailwind, `react-pdf`  
**Backend**: FastAPI, Python, PaddleOCR  
**LLM**: OpenAI GPT-4o (with modular design to support Qwen or local models)  

---

## 🧠 Architecture Highlights

- **OCR + Layout Parsing**:
  - Uses `PPStructure` for detecting text blocks, tables, and visual structure
  - Outputs normalized bounding boxes and reading order

- **Markdown Generation**:
  - Custom prompt to GPT-4o for converting structured layout JSON to readable Markdown
  - Optional refinement step via second LLM pass

- **Pipeline Design**:
  - Modular: easily swap OCR engine or LLM
  - Graceful fallback: outputs partial Markdown even if LLM fails

---

## 🎥 Demo Preview (2-min Loom)

> *See the pipeline in action: from upload → OCR → GPT → live Markdown rendering*  
[🔗 Watch Demo](#) <!-- Replace with Loom link -->

---

## 🛠️ Run Locally

```bash
git clone https://github.com/yourusername/leviosa-ai
cd leviosa-ai
# Start backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
# Start frontend
cd ../frontend && npm install && npm run dev
