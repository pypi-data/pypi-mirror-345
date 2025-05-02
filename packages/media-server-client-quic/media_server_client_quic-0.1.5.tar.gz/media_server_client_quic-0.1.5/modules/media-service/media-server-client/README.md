# Media Server Client

A unified media streaming client library that supports both WebSocket and QUIC transport protocols.

## Features

- Stream H264-encoded video frames to media servers
- Send audio frames alongside video
- Choose between WebSocket and QUIC transport protocols
- Simple, consistent API regardless of transport protocol
- Python bindings for cross-platform compatibility
- High-performance Rust implementation

## Installation

### From PyPI

```bash
pip install media-server-client
```

### From Source

```bash
cd src/rust/modules/media-server-client
pip install maturin
maturin develop
```

### Using the Build Script

The repository includes a build script that simplifies the build process:

```bash
# Build in development mode (default)
./build.sh

# Build in release mode
./build.sh --release

# Build and install locally
./build.sh --install

# Clean before building
./build.sh --clean

# Build in release mode, clean first, and install locally
./build.sh --release --clean --install
```

## Usage

### Python Example

```python
from media_server_client import MediaStreamingClient

# Create a client with the desired transport (websocket or quic)
client = MediaStreamingClient(transport_type="websocket")  # or "quic"

# Connect to server
client.connect("localhost", 8080)

# Send video frames
with open("frame.h264", "rb") as f:
    frame_data = f.read()
    client.send_video_frame(
        frame_data,
        is_keyframe=True,
        width=1920,
        height=1080
    )

# Disconnect when done
client.disconnect()
```

See the `examples/stream_example.py` for a complete example that streams a video file to a media server.

## Example Script

The repository includes an example script that demonstrates how to use the library to stream a video file:

```bash
# Using WebSocket transport (default)
python examples/stream_example.py --host localhost --port 8080

# Using QUIC transport
python examples/stream_example.py --host localhost --port 8080 --transport quic

# Custom video file
python examples/stream_example.py --video path/to/video.mp4

# Control streaming frame rate
python examples/stream_example.py --fps 30
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.