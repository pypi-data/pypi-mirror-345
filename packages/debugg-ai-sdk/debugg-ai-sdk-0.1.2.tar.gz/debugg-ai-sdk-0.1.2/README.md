<!-- Replace with your own logo -->
![DebuggAI logo](media/header-comm.jpg)

</div>

<h1 align="center">DebuggAI (debugg-ai-python)</h1>

Debugg AI's Python sdk for enabling your personal AI QA engineer


<div align="center">

DebuggAI super‑charges engineers with an AI‑powered application‑monitoring platform that _finds_ and _fixes_ bugs while your app runs locally, in production, or in CI. Get deep contextual insights about how your app is performing, how it's being used, and where the problems are. 

</div>

<div align="center">

<a href="https://docs.debugg.ai" target="_blank">
  <img src="https://img.shields.io/badge/docs-debuggai-%235D0E41" height="22" />
</a>
[![PyPi page link -- version](https://img.shields.io/pypi/v/sentry-sdk.svg)](https://pypi.python.org/pypi/sentry-sdk)

<a href="https://discord.gg/vapESyrFmJ" target="_blank">
  <img src="https://img.shields.io/badge/discord-join-debuggai.svg?labelColor=191937&color=6F6FF7&logo=discord" height="22" />
</a>

</div>

---

## ✨ Why DebuggAI?

Most AI coding tools focus on **writing** code.  
DebuggAI focuses on the other 50 % of an engineer’s life: **getting it to run.**

* **1‑line monitoring SDK** — drop‑in client (Node, Python, Go) that captures rich runtime context remotely similar to Sentry or Datadog  
* **AI Debug Chat** — ask “Why is this `KeyError` happening?” and get a pinpointed answer with links to the offending lines  
* **Instant Fix Suggestions** — one‑click patches and PRs generated from stack‑trace + context  
* **Source‑map de‑minification** — readable traces even for bundled / minified front‑end code  
* **Branch‑aware log search** — slice errors by branch, release, or feature flag to zero in fast  
* **Works anywhere you code** — VS Code, JetBrains IDEs, or CLI

---

## 📺 Demo - Get Instant Insight Into Runtime Issues

### 🔍 Typical workflows:

1. You use your favorite AI agent to write code
2. You run your app and it crashes (ah whyyyyy!)
3. DebuggAI sees the error, grabs the full stack trace + context, and uses it to generate a solution & show you EXACTLY where to look
4. You review the solution, edit it locally if needed, and apply it

### 🔍 How it works

![DebuggAI Demo](https://debuggai.s3.us-east-2.amazonaws.com/trimmed-screen%20%281%29.gif)

---

## 🖥️ Core IDE Features

| Feature | Description | Demo |
|---------|-------------|------|
| **AI Debug Chat** | Conversational agent with full stack context | ![chat](docs/static/img/chat.gif) |
| **Inline Fix Suggestions** | Autocomplete patches directly in diff‑view | ![autocomplete](docs/static/img/autocomplete.gif) |
| **Code Edit Commands** | Select > “Improve error handling” to refactor | ![edit](docs/static/img/edit.gif) |
| **Debug Actions** | One‑click shortcuts: *Explain Trace*, *Add Test*, *Generate Fix PR* | ![actions](docs/static/img/actions.gif) |

---

## 🚀 Getting Started

1. **Install the extension**  
   - [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=debugg-ai.debuggai)  
   - Jetbrains coming soon

2. **Create a project**  
    - [Sign up & create a project in the DebuggAI app](https://app.debugg.ai)

        ![Create a project](https://debuggai.s3.us-east-2.amazonaws.com/issues-page.png)

3. **Add the Python Logging SDK** (using `pip`)  

   # Python
   pip install debugg-ai-sdk

4. **Initialize** (one line):

   * Get the initialization code from the DebuggAI app

     ![Get the initialization code](https://static-debugg-ai.s3.us-east-2.amazonaws.com/debugg-ai-init-code.png)

   * Initialize the SDK

     ```python
     # app.py
     from debugg_ai_sdk import DebuggAiLogger

     logger = DebuggAiLogger(project_key="<YOUR_KEY>")
     ```

5. **Trigger an error** – head back to the IDE and watch DebuggAI suggest a fix ⚡

Full walkthrough ▶ [docs.debugg.ai/getting-started](https://docs.debugg.ai)

---

## 🛠️ Configuration

You can log in to your DebuggAI account directly in the extension, and then it will automatically connect to your project.

---

## 🤝  Interested in Contributing?

We're looking to expand the DebuggAI team!

If you're interested in joining the team or contributing to the project, please reach out to us at [hello@debugg.ai](mailto:hello@debugg.ai).

---

## 📜 License & Credits

* **Code:** [Apache 2.0](LICENSE) © 2025 Debugg, Inc.
* **Foundation:** proudly built on open-source technology.

---

## Attribution

We at Debugg AI want to thank the open-source community for their contributions. Particularly Sentry for the work on this SDK. DebuggAI is building the first fully AI QA Engineer that can automatically generate test suites and highlight issues in your app, but Sentry continues to be a great option for Application Monitoring. Use both for 
best results!

---

<div align="center">
  <sub>Made with ❤️ and too many stack traces in San Francisco.</sub>
</div>
```
