# 📁 Malama FileParse

**Malama FileParse** is a flexible and extensible framework for querying content from **PDF, DOCX, and Excel** files using **any large language model (LLM)** such as OpenAI, Gemini, Claude, Mistral, DeepSeek, and more.

> 🔍 Upload a file → Load context (optionally with page/range control) → Ask intelligent questions → Get accurate LLM-powered responses.

---

## ✨ Features

- ✅ Extracts content from **PDF**, **DOCX**, and **XLSX** files
- 📄 Supports full-document or partial (page-based) extraction for applicable formats
- 🤖 Works with **any LLM** by passing the desired model name
- 🔌 Easily extendable to new AI providers or formats
- 🧠 Unified prompt structure and clean response interface
- ⚙️ Minimal dependencies and easy integration

---

## 📂 Supported File Types

| File Type | Description                                             |
|-----------|------------------------------------------               |
| **PDF**   | Supports full and paginated text extraction             |
| **DOCX**  | Extracts paragraphs and tables in document order        |
| **XLSX**  | Reads sheet names and cell contents in readable format  |

---

## 🤖 Supported LLMs

Malama FileParse accepts **any valid model name** for the provider you configure.  
Here are some examples you can use out of the box:

| Provider         | Example Models (not restricted)                    |
|------------------|----------------------------------------------------|
| **OpenAI**       | `gpt-3.5-turbo`, `gpt-4`                           |
| **Gemini**       | `gemini-1.5-pro`, `gemini-1.0`                     |
| **Anthropic**    | `claude-3-sonnet`, `claude-3-opus`                 |
| **Groq**         | `llama3-70b-8192`, `mixtral-8x7b`                  |
| **Mistral**      | `mistral-medium`, `mistral-tiny`                   |
| **Cohere**       | `command-r`, `command-r-plus`                      |
| **DeepSeek**     | `deepseek-coder`, `deepseek-r1`                    |
| **Together.ai**  | `Qwen2-72B`, `Falcon-180B` *(via API key)*         |
| **Amazon Titan** | *(Coming Soon via Boto3 integration)*              |

You can pass **any model name** recognized by your chosen provider—no hardcoded restrictions.
Prefer your own model name to work around different models of LLM provider.

---

## 📦 Installation

```bash
pip install malama
