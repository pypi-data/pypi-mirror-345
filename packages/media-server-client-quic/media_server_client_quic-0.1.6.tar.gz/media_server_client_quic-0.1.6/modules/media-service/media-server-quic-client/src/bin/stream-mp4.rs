use anyhow::Result;
use media_server_quic_client::source::DummySource;
use media_server_quic_client::stream_client::ConnectionHandle;
use media_server_quic_client::stream_client::StreamClient;
use media_server_quic_client::AudioFrame;
use media_server_quic_client::H264Message;
use media_server_quic_protocol::common::TARGET_FPS;
use std::{
    net::SocketAddr,
    path::PathBuf,
    process::{Command, Stdio},
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc,
    },
    time::Duration,
};
use tokio::{
    fs,
    io::{AsyncReadExt, BufReader},
    signal::ctrl_c,
    sync::{mpsc, Notify},
    time::interval,
};
use tracing::trace;
use tracing::{error, info};
use tracing_subscriber::FmtSubscriber;
// Constants
const DEFAULT_MEDIA_URL: &str =
    "https://www.dropbox.com/scl/fi/8b7hpxpv71lgj3ik6f2e4/Seg-Vid-Made-With-Clipchamp.mp4?rlkey=lxwrmcxhif0y0h6xoucehd132&st=lx38jn76&dl=1";
const CACHE_DIR: &str = "/tmp/media_cache";
const INITIAL_DELAY: Duration = Duration::from_millis(500);
const MAX_FRAME_SIZE: usize = 1024 * 1024; // 1MB
const MIN_FRAME_SIZE: usize = 100; // Adjust as needed
const MIN_DUMMY_FRAME_SIZE: usize = 1920 * 1080 * 3 / 2; // For dummy frames
const SWITCH_THRESHOLD: u64 = 9; // First 100 frames are dummy

/// Searches for the 4-byte start code [0,0,0,1] in `buf` starting at `start`.
fn find_start_code(buf: &[u8], start: usize) -> Option<usize> {
    buf[start..]
        .windows(4)
        .position(|w| w == &[0, 0, 0, 1])
        .map(|pos| pos + start)
}

/// HybridSource first sends dummy frames then switches over to FFmpeg output.
#[derive(Clone)]
struct HybridSource {
    frame_count: Arc<AtomicU64>,
    running: Arc<AtomicU64>,
    video_tx: Option<mpsc::Sender<H264Message>>,
    audio_tx: Option<mpsc::Sender<AudioFrame>>,
    file_path: String,
}

impl HybridSource {
    fn new(file_path: String) -> Self {
        Self {
            frame_count: Arc::new(AtomicU64::new(0)),
            running: Arc::new(AtomicU64::new(0)),
            video_tx: None,
            audio_tx: None,
            file_path,
        }
    }

    fn is_running(&self) -> bool {
        self.running.load(Ordering::Relaxed) != 0
    }

    fn set_running(&self, running: bool) {
        self.running
            .store(if running { 1 } else { 0 }, Ordering::Relaxed);
    }

    /// Dummy frame generation: produce a fixed-size dummy frame.
    async fn generate_dummy_frames(&self) -> Result<()> {
        let mut interval = interval(Duration::from_secs_f64(1.0 / TARGET_FPS as f64));
        // Prepare a dummy frame buffer (YUV420 size for 1920x1080)
        let mut dummy_frame = vec![0u8; MIN_DUMMY_FRAME_SIZE];
        // Set a start code and a NAL unit type.
        dummy_frame[0..4].copy_from_slice(&[0, 0, 0, 1]);
        dummy_frame[4] = 0x67; // SPS (keyframe marker)
                               // (For non-keyframes you might set dummy_frame[4] to 0x41)
        info!(
            "Starting dummy frame generation (first {} frames)",
            SWITCH_THRESHOLD
        );
        while self.frame_count.load(Ordering::Relaxed) < SWITCH_THRESHOLD {
            interval.tick().await;
            let count = self.frame_count.fetch_add(1, Ordering::Relaxed);
            let frame = H264Message {
                data: dummy_frame.clone(),
                timestamp: count,
                frame_type: 1, // every frame is key (dummy)
                metadata: Default::default(),
                width: Some(1920),
                height: Some(1080),
            };
            if let Some(tx) = &self.video_tx {
                tx.send(frame).await?;
            }
            info!("Dummy: Sent frame {}", count);
        }
        Ok(())
    }

    /// FFmpeg-based frame generation (reads from ffmpeg's output)
    async fn generate_ffmpeg_frames(&self) -> Result<()> {
        // Build ffmpeg command arguments.
        let ffmpeg_args = [
            "-re",
            "-i",
            &self.file_path,
            "-c:v",
            "h264",
            "-f",
            "h264",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-vf",
            "scale=1920:1080",
            "-r",
            &TARGET_FPS.to_string(),
            "-g",
            "1", // force every frame to be a keyframe
            "-pix_fmt",
            "yuv420p",
            "-profile:v",
            "baseline",
            "-level",
            "4.1",
            "-x264-params",
            "keyint=1:min-keyint=1",
            "-bsf:v",
            "h264_mp4toannexb",
            "-fflags",
            "nobuffer",
            "-flush_packets",
            "1",
            "-",
        ];
        info!("Starting FFmpeg process with args: {:?}", ffmpeg_args);

        let mut cmd = Command::new("ffmpeg");
        cmd.args(&ffmpeg_args)
            .stdout(Stdio::piped())
            .stderr(Stdio::null());

        let mut process = tokio::process::Command::from(cmd)
            .kill_on_drop(true)
            .spawn()?;
        let stdout = process
            .stdout
            .take()
            .expect("Failed to capture ffmpeg stdout");

        let mut reader = BufReader::new(stdout);
        let mut accum_buf: Vec<u8> = Vec::with_capacity(MAX_FRAME_SIZE);
        let mut tick = interval(Duration::from_secs_f64(1.0 / TARGET_FPS as f64));
        let start_time = std::time::Instant::now();
        let mut last_stats_time = start_time;
        let mut bytes_sent = 0u64;

        info!("Switched to FFmpeg frame generation");
        loop {
            let mut buf = vec![0u8; MAX_FRAME_SIZE];
            let n = reader.read(&mut buf).await?;
            trace!("FFmpeg: Read {} bytes", n);
            if n == 0 {
                trace!("FFmpeg: EOF reached");
                break;
            }
            accum_buf.extend_from_slice(&buf[..n]);
            trace!("FFmpeg: Accumulator length: {} bytes", accum_buf.len());

            // Process accumulated data for complete frames.
            while let Some(first_sc) = find_start_code(&accum_buf, 0) {
                if let Some(second_sc) = find_start_code(&accum_buf, first_sc + 4) {
                    let frame_data = accum_buf[first_sc..second_sc].to_vec();
                    let len = frame_data.len();
                    trace!("FFmpeg: Extracted frame of {} bytes", len);
                    accum_buf = accum_buf[second_sc..].to_vec();
                    if len < MIN_FRAME_SIZE {
                        trace!("FFmpeg: Frame too small ({} bytes), skipping", len);
                        continue;
                    }
                    let count = self.frame_count.fetch_add(1, Ordering::Relaxed);
                    let frame = H264Message {
                        data: frame_data,
                        timestamp: count,
                        frame_type: 1,
                        metadata: Default::default(),
                        width: Some(1920),
                        height: Some(1080),
                    };
                    info!(
                        "FFmpeg: Sending frame {} - Size: {:.2}KB",
                        count,
                        len as f64 / 1024.0
                    );
                    if let Some(tx) = &self.video_tx {
                        tx.send(frame).await?;
                    }
                    bytes_sent += len as u64;
                    let now = std::time::Instant::now();
                    if now.duration_since(last_stats_time).as_secs() >= 5 {
                        let elapsed = now.duration_since(start_time).as_secs_f64();
                        let actual_fps = self.frame_count.load(Ordering::Relaxed) as f64 / elapsed;
                        let mbps = (bytes_sent as f64 * 8.0) / (elapsed * 1_000_000.0);
                        info!(
                            "FFmpeg stats - Frames: {}, Avg FPS: {:.2}, Bitrate: {:.2} Mbps",
                            self.frame_count.load(Ordering::Relaxed),
                            actual_fps,
                            mbps
                        );
                        last_stats_time = now;
                    }
                    tick.tick().await;
                } else {
                    info!(
                        "FFmpeg: No second start code found; waiting for more data. Accumulated: {} bytes",
                        accum_buf.len()
                    );
                    break;
                }
            }
        }
        Ok(())
    }

    /// Hybrid generate_frames: first send dummy frames then switch to FFmpeg.
    async fn generate_frames(&self) -> Result<()> {
        // First, generate 100 dummy frames.
        self.generate_dummy_frames().await?;
        // Then, switch over to FFmpeg frames.
        self.generate_ffmpeg_frames().await?;
        Ok(())
    }
}

// #[async_trait]
// impl MediaSource for HybridSource {
//     async fn start(&mut self) -> Result<(VideoChannel, AudioChannel)> {
//         let video_channel = VideoChannel::new();
//         let audio_channel = AudioChannel::new();

//         self.video_tx = Some(video_channel.clone_sender());
//         self.running.store(1, Ordering::Relaxed);

//         let source = self.clone();
//         tokio::spawn(async move {
//             if let Err(e) = source.generate_frames().await {
//                 error!("Error in HybridSource: {}", e);
//             }
//         });

//         Ok((video_channel, audio_channel))
//     }

//     async fn stop(&mut self) -> Result<()> {
//         self.running.store(0, Ordering::Relaxed);
//         self.video_tx = None;
//         self.audio_tx = None;
//         Ok(())
//     }
// }

async fn get_cached_or_download(url: &str) -> Result<PathBuf> {
    let cache_dir = PathBuf::from(CACHE_DIR);
    fs::create_dir_all(&cache_dir).await?;
    let file_name = url.split('/').last().unwrap_or("video.mp4");
    let cache_path = cache_dir.join(file_name);
    if cache_path.exists() {
        info!("Using cached file: {}", cache_path.display());
        return Ok(cache_path);
    }
    info!("Downloading MP4 file from {} to cache", url);
    let response = reqwest::get(url).await?;
    let bytes = response.bytes().await?;
    fs::write(&cache_path, bytes).await?;
    info!("Downloaded and cached file: {}", cache_path.display());
    Ok(cache_path)
}

async fn run_client(server_addr: SocketAddr, file_path: String) -> Result<ConnectionHandle> {
    info!("Starting MP4 streaming client");
    let mut client = StreamClient::new(Box::new(DummySource::new()), 0)?;
    client.connect(server_addr).await
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging.
    FmtSubscriber::builder()
        .with_max_level(tracing::Level::DEBUG)
        .with_target(false)
        .with_thread_ids(true)
        .with_file(true)
        .with_line_number(true)
        .with_thread_names(true)
        .with_level(true)
        .with_ansi(true)
        .with_timer(tracing_subscriber::fmt::time::time())
        .compact()
        .try_init()
        .map_err(|e| anyhow::anyhow!("Failed to initialize logging: {}", e))?;

    let server_addr: SocketAddr = "127.0.0.1:25502".parse()?;
    let args: Vec<String> = std::env::args()
        .filter(|arg| !arg.starts_with("--"))
        .collect();

    let file_path = args
        .get(1)
        .map(|s| s.to_string())
        .or_else(|| std::env::var("MEDIA_URL").ok())
        .unwrap_or_else(|| DEFAULT_MEDIA_URL.to_string());

    info!("Using media source: {}", file_path);

    let file_path = if file_path.starts_with("http") {
        get_cached_or_download(&file_path)
            .await?
            .to_string_lossy()
            .to_string()
    } else {
        file_path
    };

    let shutdown_notify = Arc::new(Notify::new());
    let shutdown_clone = shutdown_notify.clone();
    tokio::spawn(async move {
        if ctrl_c().await.is_ok() {
            info!("Received Ctrl+C, shutting down gracefully...");
            shutdown_clone.notify_waiters();
        }
    });

    tokio::select! {
        res = run_client(server_addr, file_path) => {
            if let Err(e) = res {
                error!("Error running client: {}", e);
            }
        }
        _ = shutdown_notify.notified() => {
            info!("Shutdown signal received, exiting main loop.");
        }
    }

    info!("Exiting gracefully. If your terminal appears broken, type `reset` or `stty sane`.");
    Ok(())
}
