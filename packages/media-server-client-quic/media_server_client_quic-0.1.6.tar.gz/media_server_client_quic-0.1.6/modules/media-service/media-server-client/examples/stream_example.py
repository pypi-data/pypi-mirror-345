#!/usr/bin/env python3

"""
Example script demonstrating how to use the unified media streaming module.
This example creates a streaming client that connects to a server and streams H264 video data
using either WebSocket or QUIC transport.
"""

import os
import sys
import signal
import logging
import argparse
import tempfile
import requests
from typing import Optional
from fractions import Fraction
from contextlib import contextmanager
from tqdm import tqdm
import time

try:
    from media_server_client import MediaStreamingClient
except ImportError:
    print("Error: media_server_client module not found.")
    print("Make sure the module is installed or PYTHONPATH is set correctly.")
    sys.exit(1)

import av

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("media-streaming-example")

# Default video URL for testing
VIDEO_URL = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "sample_video.mp4")


def download_video(url: str = VIDEO_URL, path: str = VIDEO_PATH) -> str:
    """
    Download a sample video file if it doesn't exist.
    
    Args:
        url: URL of the video to download
        path: Local path to save the video
        
    Returns:
        The path to the downloaded video file
    """
    if os.path.exists(path):
        logger.info(f"Using existing video file: {path}")
        return path
    
    logger.info(f"Downloading sample video from {url}")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        
        with open(path, "wb") as f, tqdm(
            desc="Downloading video",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress_bar.update(len(chunk))
    
    logger.info(f"Video downloaded to {path}")
    return path


class StreamingClient:
    """
    Wrapper for the MediaStreamingClient that handles connection and streaming.
    """
    
    def __init__(self, transport_type: str = "websocket"):
        """
        Initialize the streaming client.
        
        Args:
            transport_type: Transport type to use ('websocket' or 'quic')
        """
        self.client = MediaStreamingClient(transport_type)
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self, host: str, port: int) -> bool:
        """
        Connect to the media server.
        
        Args:
            host: Server hostname or IP address
            port: Server port
            
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            logger.info(f"Connecting to media server at {host}:{port}")
            self.client.connect(host, port)
            self.running = True
            logger.info(f"Connected to media server using {self.client.get_transport_type()} transport")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to media server: {e}")
            return False
    
    def stop(self):
        """Disconnect from the media server."""
        if self.running:
            try:
                logger.info("Disconnecting from media server")
                self.client.disconnect()
                logger.info("Disconnected from media server")
            except Exception as e:
                logger.error(f"Error disconnecting from media server: {e}")
            finally:
                self.running = False
    
    def is_running(self) -> bool:
        """
        Check if the client is running.
        
        Returns:
            True if the client is running, False otherwise
        """
        if not self.running:
            return False
        try:
            return self.client.is_running()
        except Exception:
            return False
    
    def get_frame_count(self) -> Optional[int]:
        """
        Get the number of frames sent.
        
        Returns:
            Number of frames sent or None if not connected
        """
        if not self.running:
            return None
        try:
            return self.client.get_frame_count()
        except Exception:
            return None
    
    def send_h264_frame(self, frame_data: bytes, is_keyframe: bool, width: int = 1920, height: int = 1080) -> bool:
        """
        Send an H264 frame to the server.
        
        Args:
            frame_data: H264 encoded frame data
            is_keyframe: Whether this frame is a keyframe
            width: Frame width
            height: Frame height
            
        Returns:
            True if the frame was sent successfully, False otherwise
        """
        if not self.running:
            return False
        
        try:
            result = self.client.send_video_frame(
                frame_data,
                is_keyframe=is_keyframe,
                width=width,
                height=height
            )
            return result
        except Exception as e:
            logger.error(f"Error sending video frame: {e}")
            return False
    
    @contextmanager
    def connect(self, host: str, port: int):
        """
        Context manager for connecting to the server.
        
        Args:
            host: Server hostname or IP address
            port: Server port
        """
        try:
            self.start(host, port)
            yield self
        finally:
            self.stop()


def stream_from_video(client: StreamingClient, video_path: str, fps: float = 30.0):
    """
    Stream a video file to the media server.
    
    Args:
        client: StreamingClient instance
        video_path: Path to the video file
        fps: Target frames per second
    """
    logger.info(f"Opening video file: {video_path}")
    
    # Open the video file with PyAV
    container = av.open(video_path)
    video_stream = container.streams.video[0]
    
    # Get video information
    original_fps = float(video_stream.average_rate)
    width = video_stream.width
    height = video_stream.height
    total_frames = video_stream.frames
    duration = video_stream.duration * video_stream.time_base
    
    logger.info(f"Video info: {width}x{height}, {original_fps} fps, {total_frames} frames, {duration:.2f}s")
    
    # Calculate the frame interval for the target FPS
    if fps <= 0:
        fps = original_fps
    frame_interval = 1.0 / fps
    logger.info(f"Streaming at target FPS: {fps}")
    
    # Set up H264 encoder
    codec = av.CodecContext.create("h264", "w")
    codec.width = width
    codec.height = height
    codec.bit_rate = 1000000  # 1 Mbps
    codec.pix_fmt = "yuv420p"
    codec.framerate = Fraction(fps)
    codec.options = {
        "preset": "ultrafast",
        "tune": "zerolatency",
    }
    
    try:
        # Create a progress bar
        with tqdm(total=total_frames, desc="Streaming frames", unit="frames") as progress:
            # Stream each frame
            frame_count = 0
            last_frame_time = time.time()
            
            for frame in container.decode(video=0):
                if not client.is_running():
                    logger.warning("Client is no longer running, stopping streaming")
                    break
                
                # Encode the frame to H264
                frame.pts = None  # Let the encoder handle timestamps
                packets = codec.encode(frame)
                
                for packet in packets:
                    # Send the encoded packet
                    is_keyframe = packet.is_keyframe
                

                    client.send_h264_frame(
                        bytes(packet),
                        is_keyframe=is_keyframe,
                        width=width,
                        height=height
                    )
                    
                    # Update frame count and progress
                    frame_count += 1
                    progress.update(1)
                    
                    # Control the frame rate
                    current_time = time.time()
                    elapsed = current_time - last_frame_time
                    sleep_time = max(0, frame_interval - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    last_frame_time = time.time()
                    
            # Flush the encoder
            packets = codec.encode(None)
            for packet in packets:
                client.send_h264_frame(
                    packet.to_bytes(),
                    is_keyframe=packet.is_keyframe,
                    width=width,
                    height=height
                )
                frame_count += 1
                progress.update(1)
                
        logger.info(f"Finished streaming {frame_count} frames")
        
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
    finally:
        container.close()
        

def main():
    """Main function for the streaming example."""
    parser = argparse.ArgumentParser(description="Media Streaming Example")
    parser.add_argument("--host", default="127.0.0.1", help="Server hostname or IP address")
    parser.add_argument("--port", type=int, default=25502, help="Server port")
    parser.add_argument("--video", default=VIDEO_PATH, help="Path to video file (downloads sample if not provided)")
    parser.add_argument("--fps", type=float, default=30.0, help="Target frames per second")
    parser.add_argument("--transport", default="websocket", choices=["websocket", "quic"], 
                        help="Transport type (websocket or quic)")
    
    args = parser.parse_args()
    
    # Download the video if needed
    video_path = args.video
    if not os.path.exists(video_path):
        video_path = download_video(VIDEO_URL, video_path)
    
    # Create the streaming client
    client = StreamingClient(args.transport)
    
    # Connect and stream
    with client.connect(args.host, args.port):
        logger.info(f"Connected to server at {args.host}:{args.port}")
        stream_from_video(client, video_path, args.fps)
    
    logger.info("Streaming example completed")


if __name__ == "__main__":
    main() 