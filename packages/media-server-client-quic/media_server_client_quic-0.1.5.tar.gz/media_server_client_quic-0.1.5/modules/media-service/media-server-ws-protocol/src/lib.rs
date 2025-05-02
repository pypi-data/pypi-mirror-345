use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tracing::debug;

pub mod config;
pub mod packet_io;
pub mod source;
pub mod tracing_config;

// Network settings
pub const STREAM_CHUNK_SIZE: usize = 256 * 1024; // Reduced from 1MB to 256KB chunks
pub const MAX_CONCURRENT_STREAMS: u32 = 200; // Increased for 32 clients
pub const IDLE_TIMEOUT: Duration = Duration::from_secs(30);
pub const STATS_INTERVAL: Duration = Duration::from_secs(1);

// Media settings
pub const TARGET_FPS: u32 = 30;
pub const KEYFRAME_INTERVAL: u64 = TARGET_FPS as u64; // Keyframe every second
pub const TEST_CLIENT_COUNT: u32 = 8; // Number of test clients to create

// H264 Message structure (similar to the protobuf version but with serde)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct H264Message {
    pub data: Vec<u8>,
    pub timestamp: u64,
    pub frame_type: u32, // 0: Unknown, 1: I-Frame, 2: P-Frame, 3: B-Frame
    pub metadata: std::collections::HashMap<String, String>,
    pub width: Option<u32>,
    pub height: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioFrame {
    pub data: Vec<u8>,
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ControlPacket {
    StartStream {
        stream_type: StreamType,
    },
    StopStream,
    Ping {
        sequence_number: u64,
        timestamp: u64,
    },
    Pong {
        sequence_number: u64,
        timestamp: u64,
        receive_timestamp: u64,
    },
    KeepAlive {
        client_id: Option<u64>,
    },
    Hello {
        version: u32,
        nonce: Option<String>,
        capabilities: Vec<String>,
        client_id: Option<u64>,
    },
    Auth {
        auth: String,
        serial: String,
        sign: Vec<u8>,
        stream_id: u64,
    },
    AuthResponse {
        success: bool,
        message: Option<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
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
    pub last_transit_time: Option<Duration>,
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
            last_transit_time: None,
        }
    }

    #[inline]
    pub fn update_rtt(&mut self, rtt: Duration) {
        if !self.has_rtt_data {
            self.min_rtt = rtt;
            self.max_rtt = rtt;
            self.avg_rtt = rtt;
            self.has_rtt_data = true;
        } else {
            // Fast updates for min/max using min/max directly
            self.min_rtt = self.min_rtt.min(rtt);
            self.max_rtt = self.max_rtt.max(rtt);
        }

        // Use a faster exponential moving average instead of storing all samples
        // This weights recent RTT values more heavily while maintaining smoothing
        // EMA = previous_avg * 0.875 + new_value * 0.125 (effectively an 8-sample window)
        let prev_micros = self.avg_rtt.as_micros() as u64;
        let new_micros = rtt.as_micros() as u64;
        let ema_micros = (prev_micros * 7 + new_micros) >> 3; // Divide by 8 using shift

        self.avg_rtt = Duration::from_micros(ema_micros);

        // Also maintain traditional sample tracking for compatibility
        self.rtt_samples[self.rtt_index] = rtt;
        self.rtt_index = (self.rtt_index + 1) % self.rtt_samples.len();
        self.rtt_count = self.rtt_count.min(self.rtt_samples.len() - 1) + 1;
    }

    #[inline]
    pub fn update_jitter(&mut self, jitter: Duration) {
        if !self.has_jitter_data {
            self.min_jitter = jitter;
            self.max_jitter = jitter;
            self.avg_jitter = jitter;
            self.has_jitter_data = true;
        } else {
            // Fast updates for min/max
            self.min_jitter = self.min_jitter.min(jitter);
            self.max_jitter = self.max_jitter.max(jitter);
        }

        // Use exponential moving average for faster updates
        let prev_micros = self.avg_jitter.as_micros() as u64;
        let new_micros = jitter.as_micros() as u64;
        let ema_micros = (prev_micros * 7 + new_micros) >> 3; // Divide by 8 using shift

        self.avg_jitter = Duration::from_micros(ema_micros);

        // Also maintain traditional sample tracking for compatibility
        self.jitter_samples[self.jitter_index] = jitter;
        self.jitter_index = (self.jitter_index + 1) % self.jitter_samples.len();
        self.jitter_count = self.jitter_count.min(self.jitter_samples.len() - 1) + 1;
    }

    pub fn update_jitter_from_transit(&mut self, transit_time: Duration) {
        if let Some(last_transit) = self.last_transit_time {
            // Calculate jitter using RFC 3550 formula
            let new_jitter = calculate_rfc3550_jitter(transit_time, last_transit, self.avg_jitter);
            debug!(
                "Jitter calculation: transit={:?}, last_transit={:?}, last_jitter={:?}, new_jitter={:?}",
                transit_time, last_transit, self.avg_jitter, new_jitter
            );
            self.update_jitter(new_jitter);
        } else {
            // First packet, no jitter yet
            debug!(
                "First packet transit time: {:?}, initializing jitter",
                transit_time
            );
            self.update_jitter(Duration::ZERO);
        }

        // Update the last transit time for next calculation
        self.last_transit_time = Some(transit_time);
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

    pub fn update_packets_sent(&mut self, size: usize) {
        // Update both video and network stats
        self.add_video_packet(size);
        self.network.update_throughput(size as f64);
    }

    pub fn update_keep_alive(&mut self) {
        // Just update the network stats with a small packet
        self.network.update_throughput(64.0); // Assume 64 bytes for keep-alive
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

// Channel definitions for video and audio
pub struct VideoChannel {
    pub tx: flume::Sender<H264Message>,
    pub rx: flume::Receiver<H264Message>,
}

impl VideoChannel {
    pub fn new() -> Self {
        let (tx, rx) = flume::bounded(4); // Only keep last ~133ms of video (at 30fps)
        Self { tx, rx }
    }

    pub fn clone_sender(&self) -> flume::Sender<H264Message> {
        self.tx.clone()
    }

    pub fn subscribe(&self) -> flume::Receiver<H264Message> {
        self.rx.clone()
    }
}

impl Default for VideoChannel {
    fn default() -> Self {
        Self::new()
    }
}

pub struct AudioChannel {
    pub tx: flume::Sender<AudioFrame>,
    pub rx: flume::Receiver<AudioFrame>,
}

impl AudioChannel {
    pub fn new() -> Self {
        let (tx, rx) = flume::bounded(8); // Only keep last ~160ms of audio (at 50Hz)
        Self { tx, rx }
    }

    pub fn clone_sender(&self) -> flume::Sender<AudioFrame> {
        self.tx.clone()
    }

    pub fn subscribe(&self) -> flume::Receiver<AudioFrame> {
        self.rx.clone()
    }
}

impl Default for AudioChannel {
    fn default() -> Self {
        Self::new()
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

// Helper function to get current timestamp in microseconds
pub fn current_timestamp_micros() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_micros() as u64
}

/// Calculate network jitter according to RFC 3550 section 6.4.1
#[inline]
pub fn calculate_rfc3550_jitter(
    transit_time: Duration,
    last_transit: Duration,
    last_jitter: Duration,
) -> Duration {
    // Calculate absolute difference in transit times
    let transit_delta = if transit_time > last_transit {
        transit_time - last_transit
    } else {
        last_transit - transit_time
    };

    // Apply the RFC 3550 jitter formula: J(i) = J(i-1) + (|D(i-1,i)| - J(i-1))/16
    // Use fast integer arithmetic
    let jitter_micros = last_jitter.as_micros() as i64;
    let delta_micros = transit_delta.as_micros() as i64;

    // Calculate (|D(i-1,i)| - J(i-1))/16 with faster integer arithmetic
    let adjustment = (delta_micros - jitter_micros) >> 4; // Divide by 16 using bit shift
    let new_jitter = jitter_micros + adjustment;

    // Ensure we never return zero jitter unless it's the first packet
    if new_jitter <= 0 {
        Duration::from_micros(1)
    } else {
        Duration::from_micros(new_jitter as u64)
    }
}
