use crate::{AudioChannel, VideoChannel};
use crate::{AudioFrame, ConnectionEvents, H264Message, MediaSource, StreamType};
use anyhow::Result;
use async_trait::async_trait;

use flume;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use tracing::{info, warn};

pub struct SourceState {
    frame_count: AtomicU64,
    running: AtomicBool,
    connected: AtomicBool,
}

impl SourceState {
    pub fn new() -> Self {
        Self {
            frame_count: AtomicU64::new(0),
            running: AtomicBool::new(false),
            connected: AtomicBool::new(false),
        }
    }

    pub fn increment_frame_count(&self) -> u64 {
        self.frame_count.fetch_add(1, Ordering::SeqCst)
    }

    pub fn get_frame_count(&self) -> u64 {
        self.frame_count.load(Ordering::SeqCst)
    }

    pub fn set_running(&self, running: bool) {
        self.running.store(running, Ordering::SeqCst)
    }

    pub fn is_running(&self) -> bool {
        self.running.load(Ordering::SeqCst)
    }

    pub fn set_connected(&self, connected: bool) {
        self.connected.store(connected, Ordering::SeqCst)
    }

    pub fn is_connected(&self) -> bool {
        self.connected.load(Ordering::SeqCst)
    }
}

impl Default for SourceState {
    fn default() -> Self {
        Self::new()
    }
}

pub struct DummySource {
    state: Arc<SourceState>,
    video_channel: Arc<VideoChannel>,
    audio_channel: Arc<AudioChannel>,
    start_time: Mutex<Option<std::time::Instant>>,
    last_stats_time: Mutex<Option<std::time::Instant>>,
    bytes_sent: AtomicU64,
}

impl Default for DummySource {
    fn default() -> Self {
        Self::new()
    }
}

impl DummySource {
    pub fn new() -> Self {
        Self {
            state: Arc::new(SourceState::default()),
            video_channel: Arc::new(VideoChannel::default()),
            audio_channel: Arc::new(AudioChannel::default()),
            start_time: Mutex::new(None),
            last_stats_time: Mutex::new(None),
            bytes_sent: AtomicU64::new(0),
        }
    }

    /// Add a video frame to the stream
    pub fn add_frame(&self, frame: H264Message, is_keyframe: bool) -> bool {
        if !self.state.is_running() {
            return false;
        }

        // Initialize timing if not done yet
        {
            let mut start_time = self.start_time.lock().unwrap();
            if start_time.is_none() {
                let now = std::time::Instant::now();
                *start_time = Some(now);
                *self.last_stats_time.lock().unwrap() = Some(now);
            }
        }

        let frame_size = frame.data.len();

        if is_keyframe {
            let frame_count = self.state.get_frame_count();
            info!(
                "Sending keyframe {} - Size: {:.2}KB",
                frame_count,
                frame_size as f64 / 1024.0
            );
        }

        // Try to send frame, if channel is full it will drop oldest frame
        match self.video_channel.tx.try_send(frame) {
            Ok(_) => {
                self.bytes_sent
                    .fetch_add(frame_size as u64, Ordering::SeqCst);

                self.state.increment_frame_count();

                // Print statistics every 5 seconds
                let now = std::time::Instant::now();
                {
                    let mut last_stats_time = self.last_stats_time.lock().unwrap();
                    if let Some(last_stats) = *last_stats_time {
                        if now.duration_since(last_stats).as_secs() >= 5 {
                            let start_time = self.start_time.lock().unwrap();
                            let elapsed = now.duration_since(start_time.unwrap()).as_secs_f64();
                            let frame_count = self.state.get_frame_count();
                            let actual_fps = frame_count as f64 / elapsed;

                            let bytes_sent = self.bytes_sent.load(Ordering::SeqCst);
                            let mbps = (bytes_sent as f64 * 8.0) / (elapsed * 1_000_000.0);

                            info!("Stats: FPS: {:.2}, Bitrate: {:.2}Mbps", actual_fps, mbps);

                            // Update last stats time
                            *last_stats_time = Some(now);
                        }
                    }
                }

                true
            }
            Err(flume::TrySendError::Full(_)) => {
                // Channel is full, just drop the frame
                warn!("Video channel full, dropping frame");
                true
            }
            Err(e) => {
                warn!("Failed to send video frame: {}", e);
                false
            }
        }
    }

    /// Add an audio frame to the stream
    pub fn add_audio_frame(&self, frame: AudioFrame) -> bool {
        if !self.state.is_running() {
            return false;
        }

        // Initialize timing if not done yet
        {
            let mut start_time = self.start_time.lock().unwrap();
            if start_time.is_none() {
                let now = std::time::Instant::now();
                *start_time = Some(now);
                *self.last_stats_time.lock().unwrap() = Some(now);
            }
        }

        let frame_size = frame.data.len();

        // Try to send frame, if channel is full it will drop oldest frame
        match self.audio_channel.tx.try_send(frame) {
            Ok(_) => {
                self.bytes_sent
                    .fetch_add(frame_size as u64, Ordering::SeqCst);
                true
            }
            Err(e) => {
                warn!("Failed to send audio frame: {}", e);
                false
            }
        }
    }

    /// Get the current frame count
    pub fn frame_count(&self) -> u64 {
        self.state.get_frame_count()
    }

    /// Check if the source is running
    pub fn is_running(&self) -> bool {
        self.state.is_running()
    }

    /// Get a reference to the state
    pub fn state(&self) -> Arc<SourceState> {
        self.state.clone()
    }

    /// Get a clone of the video channel
    pub fn video_channel(&self) -> Arc<VideoChannel> {
        self.video_channel.clone()
    }

    /// Get a clone of the audio channel
    pub fn audio_channel(&self) -> Arc<AudioChannel> {
        self.audio_channel.clone()
    }
}

#[async_trait]
impl MediaSource for DummySource {
    fn video_channel(&self) -> &VideoChannel {
        &self.video_channel
    }

    fn audio_channel(&self) -> &AudioChannel {
        &self.audio_channel
    }

    async fn start(&mut self) -> Result<()> {
        self.state.set_running(true);
        Ok(())
    }

    async fn stop(&mut self) -> Result<()> {
        self.state.set_running(false);
        Ok(())
    }
}

#[async_trait]
impl ConnectionEvents for DummySource {
    async fn on_connect(&mut self) -> Result<()> {
        info!("DummySource connected");
        self.state.set_connected(true);
        Ok(())
    }

    async fn on_disconnect(&mut self) -> Result<()> {
        info!("DummySource disconnected");
        self.state.set_connected(false);
        Ok(())
    }

    async fn on_auth_success(&mut self, client_id: u64) -> Result<()> {
        info!("DummySource authenticated with client_id: {}", client_id);
        Ok(())
    }

    async fn on_auth_failure(&mut self, error: String) -> Result<()> {
        warn!("DummySource authentication failed: {}", error);
        Ok(())
    }

    async fn on_stream_ready(&mut self, stream_type: StreamType) -> Result<()> {
        info!("DummySource stream ready: {:?}", stream_type);
        Ok(())
    }

    async fn on_stream_error(&mut self, stream_type: StreamType, error: String) -> Result<()> {
        warn!("DummySource stream error for {:?}: {}", stream_type, error);
        Ok(())
    }
}

impl Clone for DummySource {
    fn clone(&self) -> Self {
        Self {
            state: self.state.clone(),
            video_channel: self.video_channel.clone(),
            audio_channel: self.audio_channel.clone(),
            start_time: Mutex::new(self.start_time.lock().unwrap().clone()),
            last_stats_time: Mutex::new(self.last_stats_time.lock().unwrap().clone()),
            bytes_sent: AtomicU64::new(self.bytes_sent.load(Ordering::SeqCst)),
        }
    }
}
