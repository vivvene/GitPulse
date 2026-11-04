# ⚡ GitPulse

### Understand the error. Recover with confidence.

**An AI-powered Git recovery assistant that turns confusing Git errors into clear diagnoses and ordered, safety-first recovery plans.**

[🌐 Live Demo](https://git-pulsez.vercel.app/) · [💻 GitHub Repository](https://github.com/vivvene/GitPulse)

---

## 🎯 The Problem

Git errors can be intimidating, especially for beginners. A rejected push, a detached HEAD, or a stuck rebase can leave developers unsure what went wrong or which command is safe to run next.

A single risky command can make the situation worse.

**GitPulse helps developers understand the problem before attempting to fix it.**

## ✨ Features

- **Error Analysis:** Paste Git errors or terminal output to identify the likely issue.
- **Five Sample Incidents:** Explore rejected pushes, merge conflicts, detached HEAD states, stuck rebases, and lost commits.
- **Evidence-Based Diagnosis:** Separates detected evidence from assumptions and communicates diagnostic confidence.
- **Step-by-Step Recovery:** Generates an ordered recovery plan with explanations for each command.
- **Safety Labels:** Distinguishes safe actions from steps that require additional caution.
- **Copyable Commands:** Copy individual commands and execute them manually after reviewing the instructions.
- **Recent Analyses:** Revisit recent incident analyses during your session.
- **Deterministic Demo Mode:** Provides fallback analysis when the live AI service is unavailable or not configured.

## 🛡️ Safety First

GitPulse is designed to guide recovery, not take control of a developer's repository.

- It does not execute Git commands on the user's machine.
- It explains the purpose and risk level of recovery steps.
- It distinguishes observed evidence from assumptions.
- It warns users to review commands before running them.
- It avoids presenting an inferred diagnosis as guaranteed fact.

**The developer stays in control of every recovery action.**

## 🖥️ How It Works

1. **Paste:** Provide a Git error message or terminal output.
2. **Analyze:** GitPulse identifies the likely incident and supporting evidence.
3. **Understand:** Review the diagnosis, confidence, assumptions, and severity.
4. **Recover:** Follow the ordered plan, reviewing each command before executing it manually.

## 🧪 Example: Recovering from a Rejected Push

Suppose Git reports that the remote branch contains commits missing from your local branch.

GitPulse can recommend a workflow such as:

1. Check the current branch and working-tree status.
2. Fetch remote changes without modifying local files.
3. Inspect commits missing from the local branch.
4. Integrate remote changes using a reviewed rebase or merge strategy.
5. Push again without force-pushing.

Each step includes an explanation so developers understand what they're doing, rather than blindly copying commands.

## 🛠️ Technology

- **Frontend:** React, TypeScript, Vite
- **Styling and UI:** Tailwind CSS, Lucide icons
- **Testing:** Vitest
- **AI and analysis:** Incident classification, diagnostic reasoning, and deterministic fallback handling
- **Deployment:** Vercel

_Cloud services and optional AI integrations should be listed as deployed components only when they are implemented and verified._

## 🚀 Try GitPulse

Visit the live application:

**[https://git-pulsez.vercel.app/](https://git-pulsez.vercel.app/)**

Choose a sample incident or paste a Git error into the analyzer. Review the diagnosis and recovery plan before manually running any suggested commands.

## 🧠 Built with Kiro

GitPulse is being developed for the **AWS SBG JISU GenAI Sprint 1.0 — Track 3: Build with Kiro**.

The project emphasizes spec-driven engineering: defining requirements, documenting architecture, breaking implementation into verifiable tasks, and treating safety as a core product requirement.

The goal is not simply to generate a fix, but to build a recovery assistant whose recommendations are understandable, structured, and reviewable.

## 👥 Team

Built collaboratively for the AWS SBG JISU GenAI Sprint 1.0.
with :
nayanikaporel-droid and soumyadeepmagnusx

## 📌 Project Status

GitPulse currently provides a web-based Git incident analysis and recovery-planning experience. Its supported scenarios, integrations, and deployment capabilities should be assessed against the current implementation.

---

**GitPulse — Better recovery starts with understanding.**
