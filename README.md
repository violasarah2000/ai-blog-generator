# 🧠 AI Blog Generator  
### A Secure by Design AI Engineering Demonstration Project  
Built by **SperksWerks LLC** — Showcasing Modern AI Security Testing

---

## 🚀 Overview
The **AI Blog Generator** is a Python-based application that produces structured, high-quality blog content using open-source LLMs (Ollama, HuggingFace, etc.).  

But the *real* purpose of this repo?

### 👉 To demonstrate what what I can do as modern **AI Security Engineer**.

This project showcases the complete secure SDLC for AI systems — from traditional code security to emerging LLM-specific testing methodologies.

You will find examples of:

- Secure coding with Python + Flask  
- GitHub Actions CI/CD with **SAST**, **DAST**, and **AI-focused scans**  
- Model safety evaluation  
- LLM fuzzing  
- AI red teaming  
- Threat modeling  
- Secure supply chain practices  
- Signed commits and protected branches  

This repository acts as a **portfolio piece** to demonstrate capability in securing AI/ML pipelines for organizations.

---

## 🎯 Primary Goals

1. Build a functional AI blog generator  
2. Integrate traditional AppSec testing (SAST/DAST)  
3. Add LLM-specific testing and fuzzing  
4. Show how to secure an AI app end-to-end  
5. Demonstrate enterprise-ready secure SDLC workflows  
6. Provide a real world project with objective results  

---

# 🛡 Security Engineering Capabilities Demonstrated

## 1. Static Application Security Testing (SAST)
Integrated into GitHub Actions:

- CodeQL  
- Bandit  
- Semgrep (optional ruleset)  
- Dependency scanning (Dependabot/Mend)

## 2. Dynamic Application Security Testing (DAST)
The app can be scanned using:

- OWASP ZAP (API mode)
- Flask security header validation
- Local runtime checks

## 3. LLM-Specific Security Testing (core feature)

This repo includes an **AI Fuzzing Module** to test:

### ✦ Prompt Injection  
### ✦ Jailbreak Attempts  
### ✦ Response Boundary Handling  
### ✦ Refusal / Guardrail Testing  
### ✦ Context Window Attacks  
### ✦ Malicious Output Attempts (code, security bypass, etc.)  

Plus:

### ✦ AI Red Team Scripts  
Following MITRE ATLAS techniques.

---
📢 About the Author

This project is maintained by SperksWerks LLC — a Secure AI Engineering company specializing in:

- AI development and deployment
- LLM architecture security
- Threat modeling
- AI SDLC implementation
- Secure software consulting

---
# 🔧 Installation and Run Instructions

```bash
git clone https://github.com/violasarah2000/ai-blog-generator
cd ai-blog-generator
pip install -r requirements.txt
python app.py
python -m security.fuzzing.fuzz_runner


