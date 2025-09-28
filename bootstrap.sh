#!/bin/bash
set -e

echo "========================================="
echo "Politics QA (polqa) - Bootstrap Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
echo ""
echo "Checking for virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi


# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
.venv/bin/python -m pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies from pyproject.toml..."
.venv/bin/python -m pip install -e . --quiet

# Run smoke test
echo ""
echo "========================================="
echo "Running smoke test..."
echo "========================================="
echo ""

echo "Executing: polqa run --providers dummy --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42"
.venv/bin/python -m polqa run --providers dummy --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42

# Generate report
echo ""
echo "========================================="
echo "Generating report..."
echo "========================================="
echo ""

echo "Executing: polqa report --input results/last_run.json --output results/report.html"
.venv/bin/python -m polqa report --input results/last_run.json --output results/report.html

# Success message
echo ""
echo "========================================="
echo "✅ Bootstrap completed successfully!"
echo "========================================="
echo ""
echo "📊 Report generated at: results/report.html"
echo ""
echo "To use polqa:"
echo " "
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo " "
echo "  2. Configure your API keys:"
echo "     polqa config apikey openai <your-key>"
echo "     polqa config apikey gemini <your-key>"
echo "     polqa config apikey abacus <your-key>"
echo "     polqa config apikey claude <your-key>"
echo " "
echo "  3. Run evaluations:"
echo "     polqa run --providers gemini:gemini-2.5-flash --dataset polqa/datasets/politics_v1.jsonl --lite --force --seed 42"
echo " "
echo "  4. Generate reports:"
echo "     polqa report --input results/last_run.json --output results/report.html"
echo ""
echo "For more information, see README.md"