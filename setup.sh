#!/bin/bash
set -euo pipefail

echo "🤖 Gemini CLI Workshop — Environment Setup"
echo "============================================"
echo ""

# 1. Check prerequisites
echo "📋 Checking prerequisites..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Install: https://nodejs.org (v18+)"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git not found. Install: https://git-scm.com"; exit 1; }
command -v jq >/dev/null 2>&1 || echo "⚠️  jq not found (needed for hook examples). Install: brew install jq"
echo "   Node.js: $(node --version)"
echo "   npm:     $(npm --version)"
echo "   Git:     $(git --version)"
echo ""

# 2. Install/update Gemini CLI
echo "📦 Installing Gemini CLI..."
npm install -g @google/gemini-cli
echo ""

# 3. Initialize demo app submodule
echo "📂 Setting up demo app (proshop-v2)..."
git submodule update --init --recursive
if [ -d "demo-app" ]; then
  cd demo-app && npm install && cd ..
elif [ -d "submodules/proshop-v2" ]; then
  # Fallback if submodule is at a different path
  ln -sf submodules/proshop-v2 demo-app
  cd demo-app && npm install && cd ..
else
  echo "⚠️  Demo app submodule not found. Run: git submodule add https://github.com/bradtraversy/proshop-v2.git demo-app"
fi
echo ""

# 4. Copy sample configs into demo-app
echo "⚙️  Configuring Gemini CLI for demo app..."
mkdir -p demo-app/.gemini/agents demo-app/.gemini/hooks demo-app/.gemini/policies

# Settings
if [ -f "samples/config/settings.json" ]; then
  cp samples/config/settings.json demo-app/.gemini/settings.json
fi

# Policy
if [ -f "samples/config/policy.toml" ]; then
  cp samples/config/policy.toml demo-app/.gemini/policies/team-guardrails.toml
fi

# Agents
if [ -d "samples/agents" ]; then
  cp samples/agents/*.md demo-app/.gemini/agents/ 2>/dev/null || true
fi

# Hooks
if [ -d "samples/hooks" ]; then
  cp samples/hooks/*.sh demo-app/.gemini/hooks/ 2>/dev/null || true
  chmod +x demo-app/.gemini/hooks/*.sh 2>/dev/null || true
fi
echo ""

# 5. Copy sample GEMINI.md hierarchy
echo "📝 Setting up GEMINI.md context hierarchy..."
if [ -f "samples/gemini-md/project-gemini.md" ]; then
  cp samples/gemini-md/project-gemini.md demo-app/GEMINI.md
fi
if [ -f "samples/gemini-md/backend-gemini.md" ]; then
  mkdir -p demo-app/backend
  cp samples/gemini-md/backend-gemini.md demo-app/backend/GEMINI.md
fi
echo ""

# 6. Verify auth
echo "🔑 Verifying Gemini CLI authentication..."
if gemini -p "Say 'Workshop ready!' in exactly two words." 2>/dev/null; then
  echo ""
  echo "✅ Authentication works!"
else
  echo "⚠️  Auth check failed. Run 'gemini' interactively to authenticate."
fi

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. cd demo-app && gemini"
echo "  2. Open: https://pauldatta.github.io/gemini-cli-field-workshop/"
echo ""
echo "Workshop order:"
echo "  → Use Case 1: SDLC Productivity Enhancement"
echo "  → Use Case 2: Legacy Code Modernization"
echo "  → Use Case 3: Agentic DevOps Orchestration"
echo "  → Advanced Patterns (self-paced)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Optional: Advanced Agentic Tooling (self-paced)"
echo ""
echo "  # Install engineering skills for structured SDLC workflows"
echo "  # Prereqs: Gemini CLI already installed (done above)"
echo "  gemini skills install https://github.com/addyosmani/agent-skills.git --path skills"
echo ""
echo "  # Install agents-cli for building/deploying ADK agents"
echo "  # Prereqs: Python 3.11+, uv (https://docs.astral.sh/uv)"
echo "  uvx google-agents-cli setup"
echo ""
echo "  # Add Developer Knowledge MCP for doc-grounded answers"
echo "  # Prereqs: API key from Google Cloud console"
echo "  gemini mcp add -t http -H \"X-Goog-Api-Key: YOUR_KEY\" \\"
echo "    google-developer-knowledge \\"
echo "    https://developerknowledge.googleapis.com/mcp --scope user"
echo ""
echo "  See: docs/advanced-patterns.md for full walkthroughs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
