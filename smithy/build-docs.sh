#!/bin/bash

# Build Smithy docs script for macOS/Linux
# Usage: ./build-docs.sh [md|html|all]
#   md   - Build markdown docs only
#   html - Build HTML docs only (requires Python + Sphinx)
#   all  - Build both (default)

set -e

SMITHY_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTIONS_DIR="$SMITHY_DIR/build/smithyprojections/msrobot-smithy"
DOCS_DIR="$SMITHY_DIR/docs"

# Service projections
SERVICES=("docs:session" "docs-calibration:calibration" "docs-recording:recording" "docs-device:device")

# Default to all
FORMAT="${1:-all}"

echo "Building Smithy model..."
cd "$SMITHY_DIR"
"$SMITHY_DIR/gradlew" build

# Create output directories
mkdir -p "$DOCS_DIR/md"
mkdir -p "$DOCS_DIR/html"

build_md() {
    echo "Copying markdown docs for all services..."

    for service_pair in "${SERVICES[@]}"; do
        projection="${service_pair%%:*}"
        name="${service_pair##*:}"
        src_dir="$PROJECTIONS_DIR/$projection/docgen/content"

        if [[ -d "$src_dir" ]]; then
            echo "  - ${name^} Service"
            mkdir -p "$DOCS_DIR/md/$name"
            cp -R "$src_dir/"* "$DOCS_DIR/md/$name/"
        fi
    done

    echo "Markdown docs available at: $DOCS_DIR/md"
}

build_html() {
    echo "Building HTML docs with Sphinx for all services..."

    # Check for Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo "Python not found! Please install Python."
        exit 1
    fi

    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi

    # Install requirements if needed
    if [[ -f "$PROJECTIONS_DIR/docs/docgen/requirements.txt" ]]; then
        echo "Installing Sphinx requirements..."
        pip install -q -r "$PROJECTIONS_DIR/docs/docgen/requirements.txt" 2>/dev/null || true
    fi

    for service_pair in "${SERVICES[@]}"; do
        projection="${service_pair%%:*}"
        name="${service_pair##*:}"
        docgen_dir="$PROJECTIONS_DIR/$projection/docgen"

        if [[ -d "$docgen_dir/content" ]]; then
            echo "  - ${name^} Service"
            cd "$docgen_dir"
            $PYTHON_CMD -m sphinx -q -b html content build/html 2>/dev/null || echo "    Warning: Sphinx build had warnings"
            mkdir -p "$DOCS_DIR/html/$name"
            cp -R "build/html/"* "$DOCS_DIR/html/$name/"
        fi
    done

    # Create index page
    create_index

    echo "HTML docs available at: $DOCS_DIR/html/index.html"
}

create_index() {
    cat > "$DOCS_DIR/html/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
<title>MS-Robot API Documentation</title>
<style>
body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
h1 { color: #333; }
ul { list-style: none; padding: 0; }
li { margin: 10px 0; }
a { color: #0066cc; text-decoration: none; font-size: 18px; }
a:hover { text-decoration: underline; }
.desc { color: #666; font-size: 14px; margin-left: 20px; }
</style>
</head>
<body>
<h1>MS-Robot API Documentation</h1>
<p>Generated from Smithy model. Select a service to view its documentation:</p>
<ul>
<li><a href="session/index.html">Session Service</a><div class="desc">Manages user work sessions</div></li>
<li><a href="calibration/index.html">Calibration Service</a><div class="desc">Camera and hand-eye calibration</div></li>
<li><a href="recording/index.html">Recording Service</a><div class="desc">Sample recording and data export</div></li>
<li><a href="device/index.html">Device Service</a><div class="desc">Hardware device management</div></li>
</ul>
</body>
</html>
EOF
}

case "$FORMAT" in
    md)
        build_md
        ;;
    html)
        build_html
        ;;
    all)
        echo ""
        echo "=== Building Markdown docs ==="
        build_md
        echo ""
        echo "=== Building HTML docs ==="
        build_html
        ;;
    *)
        echo "Unknown format: $FORMAT"
        echo "Usage: ./build-docs.sh [md|html|all]"
        exit 1
        ;;
esac

echo ""
echo "Done!"
