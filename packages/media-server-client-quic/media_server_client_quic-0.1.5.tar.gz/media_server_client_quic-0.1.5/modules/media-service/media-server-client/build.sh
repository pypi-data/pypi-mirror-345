#!/bin/bash

# Function to print a message with a timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Build the media-server-client module for both Rust and Python."
    echo ""
    echo "Options:"
    echo "  -h, --help                  Show this help message and exit"
    echo "  -d, --dev                   Build in development mode (default)"
    echo "  -r, --release               Build in release mode"
    echo "  -i, --install               Install the built package locally"
    echo "  -c, --clean                 Clean build artifacts before building"
    echo ""
    echo "Example:"
    echo "  $0 --release --install      # Build in release mode and install locally"
    echo "  $0 --dev                    # Build in development mode"
    echo "  $0 --clean                  # Clean and build in development mode"
}

# Parse command line arguments
DEV_MODE=true
INSTALL=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -r|--release)
            DEV_MODE=false
            shift
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        *)
            log "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set build mode
if [ "$DEV_MODE" = true ]; then
    BUILD_MODE="debug"
    MATURIN_MODE=""
    CARGO_MODE=""
    log "Building in development mode..."
else
    BUILD_MODE="release"
    MATURIN_MODE="--release"
    CARGO_MODE="--release"
    log "Building in release mode..."
fi

# Current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || { log "Failed to change to script directory"; exit 1; }

# Clean if requested
if [ "$CLEAN" = true ]; then
    log "Cleaning build artifacts..."
    cargo clean
    rm -rf target/wheels
    rm -rf *.egg-info
fi

# Build the Rust library
log "Building Rust library..."
cargo build $CARGO_MODE

if [ $? -ne 0 ]; then
    log "Failed to build Rust library. Exiting."
    exit 1
fi

# Build the Python wheel
log "Building Python wheel with maturin..."
maturin build $MATURIN_MODE

if [ $? -ne 0 ]; then
    log "Failed to build Python wheel. Exiting."
    exit 1
fi

# Install locally if requested
if [ "$INSTALL" = true ]; then
    log "Installing package locally..."
    if [ "$DEV_MODE" = true ]; then
        maturin develop
    else
        maturin develop --release
    fi
    
    if [ $? -ne 0 ]; then
        log "Failed to install package locally. Exiting."
        exit 1
    fi
    
    log "Package installed successfully."
else
    log "Skip local installation. Use --install to install locally."
fi

log "Build completed successfully!"

# Show the build artifacts
log "Build artifacts:"
if [ "$DEV_MODE" = true ]; then
    ls -lh target/debug/libmedia_server_client.* 2>/dev/null || echo "No debug library files found."
else
    ls -lh target/release/libmedia_server_client.* 2>/dev/null || echo "No release library files found."
fi

ls -lh target/wheels/*.whl 2>/dev/null || echo "No wheel files found."

log "To install the wheel, run: pip install <path-to-wheel-file>" 