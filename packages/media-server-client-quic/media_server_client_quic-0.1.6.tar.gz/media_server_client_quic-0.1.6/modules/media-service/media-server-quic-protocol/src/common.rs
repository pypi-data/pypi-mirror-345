use crate::types::AudioChannel;
use crate::types::VideoChannel;
use anyhow::Result;
use async_trait::async_trait;
use protobuf_types::media_streaming::H264Message;
use serde::{Deserialize, Serialize};
use std::time::Duration;

// Network settings
pub const STREAM_CHUNK_SIZE: usize = 1024 * 1024; // 1MB chunks
pub const MAX_CONCURRENT_STREAMS: u32 = 200; // Increased for 32 clients
pub const IDLE_TIMEOUT: Duration = Duration::from_secs(30);
pub const STATS_INTERVAL: Duration = Duration::from_secs(1);

// Media settings
pub const TARGET_FPS: u32 = 30;
pub const KEYFRAME_INTERVAL: u64 = TARGET_FPS as u64; // Keyframe every second
pub const TEST_CLIENT_COUNT: u32 = 8; // Number of test clients to create

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioFrame {
    pub data: Vec<u8>,
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ControlPacket {
    StartStream {
        client_id: u64,
        stream_type: StreamType,
    },
    StopStream {
        client_id: u64,
    },
    KeepAlive {
        client_id: u64,
    },
}

#[derive(Debug, Clone)]
pub enum MediaPacket {
    Video(H264Message),
    Audio(AudioFrame),
    Control(ControlPacket),
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum StreamType {
    Video,
    Audio,
    KeepAlive,
}

#[derive(Debug, Clone)]
pub struct NetworkStats {
    pub min_rtt: Duration,
    pub max_rtt: Duration,
    pub avg_rtt: Duration,
    rtt_samples: [Duration; 16],
    rtt_index: usize,
    rtt_count: usize,
    pub min_jitter: Duration,
    pub max_jitter: Duration,
    pub avg_jitter: Duration,
    jitter_samples: [Duration; 16],
    jitter_index: usize,
    jitter_count: usize,
    pub throughput: f64,
    pub packet_loss_rate: f64,
    pub total_packets: u64,
    pub lost_packets: u64,
    last_throughput_update: std::time::Instant,
    bytes_in_window: u64,
    has_rtt_data: bool,
    has_jitter_data: bool,
}

impl Default for NetworkStats {
    fn default() -> Self {
        Self::new()
    }
}

impl NetworkStats {
    pub fn new() -> Self {
        Self {
            min_rtt: Duration::ZERO,
            max_rtt: Duration::ZERO,
            avg_rtt: Duration::ZERO,
            rtt_samples: [Duration::ZERO; 16],
            rtt_index: 0,
            rtt_count: 0,
            min_jitter: Duration::ZERO,
            max_jitter: Duration::ZERO,
            avg_jitter: Duration::ZERO,
            jitter_samples: [Duration::ZERO; 16],
            jitter_index: 0,
            jitter_count: 0,
            throughput: 0.0,
            packet_loss_rate: 0.0,
            total_packets: 0,
            lost_packets: 0,
            last_throughput_update: std::time::Instant::now(),
            bytes_in_window: 0,
            has_rtt_data: false,
            has_jitter_data: false,
        }
    }

    pub fn update_rtt(&mut self, rtt: Duration) {
        if !self.has_rtt_data {
            self.min_rtt = rtt;
            self.max_rtt = rtt;
            self.avg_rtt = rtt;
            self.has_rtt_data = true;
        } else {
            self.min_rtt = self.min_rtt.min(rtt);
            self.max_rtt = self.max_rtt.max(rtt);
        }

        self.rtt_samples[self.rtt_index] = rtt;
        self.rtt_index = (self.rtt_index + 1) % self.rtt_samples.len();
        self.rtt_count = self.rtt_count.min(self.rtt_samples.len() - 1) + 1;

        // Calculate moving average
        let sum: Duration = self.rtt_samples.iter().take(self.rtt_count).sum();
        self.avg_rtt = sum / self.rtt_count as u32;
    }

    pub fn update_jitter(&mut self, jitter: Duration) {
        if !self.has_jitter_data {
            self.min_jitter = jitter;
            self.max_jitter = jitter;
            self.avg_jitter = jitter;
            self.has_jitter_data = true;
        } else {
            self.min_jitter = self.min_jitter.min(jitter);
            self.max_jitter = self.max_jitter.max(jitter);
        }

        self.jitter_samples[self.jitter_index] = jitter;
        self.jitter_index = (self.jitter_index + 1) % self.jitter_samples.len();
        self.jitter_count = self.jitter_count.min(self.jitter_samples.len() - 1) + 1;

        // Calculate moving average
        let sum: Duration = self.jitter_samples.iter().take(self.jitter_count).sum();
        self.avg_jitter = sum / self.jitter_count as u32;
    }

    pub fn update_packet_loss(&mut self, lost: bool) {
        self.total_packets += 1;
        if lost {
            self.lost_packets += 1;
        }
        self.packet_loss_rate = self.lost_packets as f64 / self.total_packets as f64;
    }

    pub fn update_throughput(&mut self, bytes: f64) {
        let now = std::time::Instant::now();
        let elapsed = now.duration_since(self.last_throughput_update);

        if elapsed >= Duration::from_secs(1) {
            // Convert to Mbps
            self.throughput =
                (self.bytes_in_window as f64 * 8.0) / (elapsed.as_secs_f64() * 1_000_000.0);
            self.bytes_in_window = bytes as u64;
            self.last_throughput_update = now;
        } else {
            self.bytes_in_window += bytes as u64;
        }
    }

    pub fn get_stats(&self) -> String {
        format!(
            "Network Stats:\n  RTT (min/avg/max): {:.2?}/{:.2?}/{:.2?}\n  Jitter (min/avg/max): {:.2?}/{:.2?}/{:.2?}\n  Throughput: {:.2} Mbps\n  Packet Loss: {:.2}%",
            self.min_rtt,
            self.avg_rtt,
            self.max_rtt,
            self.min_jitter,
            self.avg_jitter,
            self.max_jitter,
            self.throughput,
            self.packet_loss_rate * 100.0
        )
    }
}

#[derive(Debug, Clone)]
pub struct StreamStats {
    pub video_packets: u64,
    pub audio_packets: u64,
    pub video_bytes: u64,
    pub audio_bytes: u64,
    pub start_time: std::time::Instant,
    pub network: NetworkStats,
}

impl Default for StreamStats {
    fn default() -> Self {
        Self::new()
    }
}

impl StreamStats {
    pub fn new() -> Self {
        Self {
            video_packets: 0,
            audio_packets: 0,
            video_bytes: 0,
            audio_bytes: 0,
            start_time: std::time::Instant::now(),
            network: NetworkStats::new(),
        }
    }

    pub fn add_video_packet(&mut self, size: usize) {
        self.video_packets += 1;
        self.video_bytes += size as u64;
    }

    pub fn add_audio_packet(&mut self, size: usize) {
        self.audio_packets += 1;
        self.audio_bytes += size as u64;
    }

    fn calculate_stats(&self) -> (f64, f64, f64, f64) {
        let elapsed = self.start_time.elapsed().as_secs_f64();
        let video_mbps = (self.video_bytes as f64 * 8.0) / (elapsed * 1_000_000.0);
        let audio_mbps = (self.audio_bytes as f64 * 8.0) / (elapsed * 1_000_000.0);
        let video_fps = self.video_packets as f64 / elapsed;
        let audio_fps = self.audio_packets as f64 / elapsed;
        (video_mbps, audio_mbps, video_fps, audio_fps)
    }

    pub fn get_stats(&self) -> String {
        let (video_mbps, audio_mbps, video_fps, audio_fps) = self.calculate_stats();
        format!(
            "Stream Stats:\n  Video: {:.2} Mbps @ {:.2} FPS\n  Audio: {:.2} Mbps @ {:.2} FPS\n{}",
            video_mbps,
            video_fps,
            audio_mbps,
            audio_fps,
            self.network.get_stats()
        )
    }
}

#[async_trait]
pub trait ConnectionEvents: Send + Sync {
    /// Called when the client successfully connects to the server
    async fn on_connect(&mut self) -> Result<()> {
        Ok(())
    }

    /// Called when the client disconnects from the server
    async fn on_disconnect(&mut self) -> Result<()> {
        Ok(())
    }

    /// Called when the client successfully authenticates
    async fn on_auth_success(&mut self, _client_id: u64) -> Result<()> {
        Ok(())
    }

    /// Called when authentication fails
    async fn on_auth_failure(&mut self, _error: String) -> Result<()> {
        Ok(())
    }

    /// Called when a stream is successfully established
    async fn on_stream_ready(&mut self, _stream_type: StreamType) -> Result<()> {
        Ok(())
    }

    /// Called when a stream encounters an error
    async fn on_stream_error(&mut self, _stream_type: StreamType, _error: String) -> Result<()> {
        Ok(())
    }
}

#[async_trait]
pub trait MediaSource: ConnectionEvents {
    /// Get the video channel
    fn video_channel(&self) -> &VideoChannel;

    /// Get the audio channel
    fn audio_channel(&self) -> &AudioChannel;

    /// Start the media source
    async fn start(&mut self) -> Result<()>;

    /// Stop the media source
    async fn stop(&mut self) -> Result<()>;
}

#[async_trait]
pub trait MediaSink: Send + Sync {
    async fn handle_video(&mut self, frame: H264Message, stream_id: u64) -> Result<()>;
    async fn handle_audio(&mut self, frame: AudioFrame, stream_id: u64) -> Result<()>;
    async fn on_auth(
        &mut self,
        auth: String,
        serial: String,
        sign: Vec<u8>,
        stream_id: u64,
    ) -> Result<bool>;
    async fn on_client_disconnect(&mut self, stream_id: u64) -> Result<()>;
}
