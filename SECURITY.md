# Security Policy  
AI Blog Generator – Secure AI Engineering Demonstration  
SperksWerks LLC

## 🔐 Overview
This repository is intentionally designed as a **demonstration project** for modern AI security testing.  
It includes examples of:

- Secure SDLC workflows  
- Traditional SAST/DAST integration  
- LLM-specific security testing  
- Automated LLM fuzzing  
- Threat modeling for AI architectures  
- Secure coding best practices  
- Code scanning and dependency management  

The goal is to showcase my professional capabilities in **AI Security Engineering**, including emerging practices required for safe AI application development.

---

## 🛡 Supported Security Testing

### 1. Static Application Security Testing (SAST)
This project integrates:

- **GitHub CodeQL**
- **Python Bandit**
- **Dependency Scanning** (Dependabot/Mend)
- **Semgrep (optional profile)**

All findings are automatically surfaced in pull requests.

### 2. Dynamic Application Security Testing (DAST)
When deployed locally, the following can be run:

- **OWASP ZAP API scan**
- **Flask security headers validation**
- **Local runtime behavior checks**

DAST results are incorporated into the secure-SDLC workflow.

### 3. AI / LLM Security Testing
This repository includes:

#### **LLM Fuzzing Framework**
- Automated adversarial input generation  
- Prompt injection testing  
- Output safety and hallucination detection  
- Response boundary testing (long context, malformed input, nested inputs)

#### **AI Red Team Exercises**
- Model inversion attempts  
- Prompt-based evasion  
- Guardrail bypass attempts  
- Evaluation of model drift and unexpected reasoning behavior  

#### **Supply Chain Security for LLMs**
- Model hash verification  
- Model provenance tracking (Ollama / HuggingFace)  
- Container signing and rebuild transparency  

---

## 🔰 Threat Model
The architecture is threat-modeled using:

- **STRIDE**  
- **PASTA (AI-adapted)**  
- **LLM+AI Threat Matrix (MITRE ATLAS categories)**

You can view the full Threat Model in `/docs/threat-model/`.

---

## ❗ Reporting a Vulnerability
If you discover a vulnerability or unexpected model behavior:

### Please submit a report by opening a GitHub Security Advisory
**Security → Advisories → New draft advisory**

You may also email:  
**studio@sperkswerks.ai**

To keep disclosures responsible:

1. Please provide a clear reproduction path.  
2. Do not disclose publicly until discussed and remediated.  
3. If the issue relates to LLM behavior, include model name + version.  

---

## ✔ Responsible AI Use
This project is not intended for harmful generation or misuse.  

---

## 🙏 Acknowledgements
This project is part of the **Secure AI Studio** program at SperksWerks LLC, dedicated to elevating the security posture of AI-driven software.

