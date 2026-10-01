# 🌙 Loona — AI Desktop Companion

Loona is a personal AI desktop companion designed to understand natural language, communicate through **voice and text**, and interact with a Windows PC.

The goal is to build an AI that can understand what the user wants, use the appropriate tools, perform actions on the computer, verify the result, and respond naturally through **voice or text**.

## ✨ Vision

Loona is being developed to become a capable personal AI companion that works alongside the user and interacts with their digital environment.

Unlike a traditional chatbot, Loona is designed to go beyond conversations by interacting directly with the user's Windows environment.

Her core workflow is:

**Understand → Plan → Act → Verify → Report**

For example:

> "Loona, open the Oblivion movie."

Loona can understand the request, search the user's local drives, identify the appropriate file, open it, verify the action, and report the result through voice or text.

> **Loona:** "Done, Sir. Oblivion is playing."

## 🚀 Current Features

- 🤖 Gemini-powered AI agent
- 🌙 Custom Loona identity and personality
- 🎙️ Voice interaction and voice commands
- 🔊 AI voice responses
- 💬 Text-based interaction
- 🧠 Persistent user profile and memory
- 📁 Local file searching
- 🎬 Media and file opening
- 🖥️ Windows application searching
- ▶️ Application launching
- ⏹️ Application closing
- 🕐 Date and time information
- 💻 System information
- 🔧 Custom Loona tools
- 🛡️ Safety and confirmation rules
- 🔄 Agent tool workflow
- ⚙️ Automation framework support
- 🖥️ Interactive terminal interface
- 🎭 Animated Eikon interface

## 🖥️ Loona Interface

Loona uses a custom **Herm TUI** interface built on top of the Hermes Agent framework.

The interface provides an interactive terminal environment for communicating with Loona, while displaying the current session, model information, context usage, and the animated **Nous Eikon** interface.

Loona can be started with:

cd /d D:\AI-Desktop-Agent
| Classic CLI | `hermes` | Official Hermes CLI |
| Native TUI | `hermes --tui` | Official Hermes TUI |
| Herm TUI | `bunx herm-tui` | Third-party OpenTUI frontend |

## 🎙️ Voice Interaction

Loona supports voice-based communication in addition to traditional text interaction.

The user can speak naturally to Loona, allowing commands and conversations to be handled without requiring everything to be typed.

The voice interaction flow is:

```text
User Voice
    ↓
Speech Recognition
    ↓
Loona
    ↓
AI Model
    ↓
Agent / Tool Loop
    ↓
Loona Tools
    ↓
Windows PC
    ↓
Loona Response
    ↓
Text-to-Speech
    ↓
User
