#!/bin/bash

# Multi-CPU Assembler - GitHub Setup Script
# This script initializes the repository and prepares it for GitHub upload

set -e  # Exit on any error

echo "🚀 Multi-CPU Assembler - GitHub Setup"
echo "======================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "compiler" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo "⚠️  Git repository already exists. Skipping initialization."
else
    echo "📝 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Test outputs
test_output.bin
*.bin

# Temporary files
*.tmp
*.temp
EOF
    echo "✅ .gitignore created"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
git commit -m "feat: initial commit - Multi-CPU Assembler

- Multi-CPU assembler supporting 65C02, 6800, and 8086
- Modular architecture with extensible CPU profiles
- Enhanced error reporting and validation
- Two-pass assembly with symbol resolution
- Comprehensive test suite
- Complete documentation and GitHub templates"

echo "✅ Initial commit created"

echo ""
echo "🎉 Repository setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: multi-cpu-assembler"
echo "   - Description: Multi-CPU assembler supporting 65C02, 6800, and 8086 architectures"
echo "   - Make it public"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""
echo "2. Link your local repository to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/multi-cpu-assembler.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Enable GitHub features:"
echo "   - Go to Settings → Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main, folder: / (root)"
echo "   - Save"
echo ""
echo "4. Create initial issues to attract contributors:"
echo "   - Z80 CPU support implementation"
echo "   - ARM Cortex-M support"
echo "   - Macro system implementation"
echo "   - Conditional assembly directives"
echo ""
echo "5. Invite collaborators and share on social media!"
echo ""
echo "📖 Your repository will be available at:"
echo "https://github.com/YOUR_USERNAME/multi-cpu-assembler"
echo ""
echo "🌐 GitHub Pages site will be available at:"
echo "https://YOUR_USERNAME.github.io/multi-cpu-assembler"
echo ""
echo "Happy coding! 🎯"