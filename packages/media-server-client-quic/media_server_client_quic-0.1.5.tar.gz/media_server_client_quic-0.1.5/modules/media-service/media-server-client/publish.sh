#!/bin/bash

# Function to print a message with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Publish the media-server-client-quic Python package to PyPI or TestPyPI."
    echo ""
    echo "Options:"
    echo "  -h, --help                  Show this help message and exit"
    echo "  -t, --test                  Publish to TestPyPI instead of PyPI"
    echo "  -s, --skip-existing         Skip existing package versions on PyPI"
    echo "  -T, --token TOKEN           Use the provided PyPI token for authentication"
    echo ""
    echo "Example:"
    echo "  $0 --test                   # Publish to TestPyPI"
    echo "  $0                          # Publish to PyPI (requires confirmation)"
    echo "  $0 --token PYPI_TOKEN       # Publish to PyPI using token authentication"
}

# Function to extract the PyPI API key from environment.yaml
extract_pypi_api_key() {
    # Get the repository root directory (assuming we're in src/rust/modules/media-service/media-server-client)
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
    if [ -z "$REPO_ROOT" ]; then
        # Fallback if git command fails
        REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../" && pwd)"
    fi
    
    ENV_YAML_PATH="$REPO_ROOT/environment.yaml"
    
    if [ ! -f "$ENV_YAML_PATH" ]; then
        log "Error: environment.yaml not found at $ENV_YAML_PATH"
        return 1
    fi
    
    # Extract API key using grep and sed
    API_KEY=$(grep -A 1 "pypi:" "$ENV_YAML_PATH" | grep "api_key" | sed -E 's/.*api_key: "([^"]+)".*/\1/')
    
    if [ -z "$API_KEY" ]; then
        log "Error: Could not extract PyPI API key from environment.yaml"
        return 1
    fi
    
    echo "$API_KEY"
}

# Parse command line arguments
TEST_MODE=false
SKIP_EXISTING=""
API_TOKEN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -s|--skip-existing)
            SKIP_EXISTING="--skip-existing"
            shift
            ;;
        -T|--token)
            if [ -z "$2" ]; then
                log "Error: Token value is missing"
                exit 1
            fi
            API_TOKEN="$2"
            shift 2
            ;;
        *)
            log "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set publish flag based on mode
if [ "$TEST_MODE" = true ]; then
    PUBLISH_FLAG="--repository testpypi"
else
    PUBLISH_FLAG=""
fi

# Start the publishing process
log "Starting the media-server-client-quic Python package publishing process..."

# Build the wheel with name override
log "Building the Python wheel..."
maturin build --release

# If not in test mode, ask for confirmation
if [ "$TEST_MODE" = false ]; then
    log "You are about to publish the media-server-client-quic package to PyPI."
    log "This action cannot be undone. Are you sure you want to continue? (y/N)"
    read -r REPLY
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Publishing skipped."
        exit 0
    fi
    log "Publishing to PyPI..."
else
    log "Publishing to TestPyPI..."
fi

# Get API key from environment.yaml if no token is provided
if [ -z "$API_TOKEN" ]; then
    API_TOKEN=$(extract_pypi_api_key)
    if [ $? -eq 0 ] && [ -n "$API_TOKEN" ]; then
        log "Using API key from environment.yaml"
    else
        log "Warning: Could not extract API key from environment.yaml. Falling back to interactive authentication."
    fi
fi

# Set environment variable for maturin authentication
if [ -n "$API_TOKEN" ]; then
    export MATURIN_PYPI_TOKEN="$API_TOKEN"
    log "Using API token for authentication"
fi

# Publish the package
maturin publish $PUBLISH_FLAG $SKIP_EXISTING

log "Package published successfully!" 