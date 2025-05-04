use anyhow::Result;
use media_server_quic_client::source::DummySource;
use media_server_quic_client::stream_client::StreamClient;
use media_server_quic_protocol::common::AudioFrame;
use media_server_quic_protocol::common::TARGET_FPS;
use protobuf_types::media_streaming::H264Message;
use std::{net::SocketAddr, time::Duration};
use tokio::{
    signal::ctrl_c,
    time::{interval, timeout},
};
use tracing::{info, warn, Level};
use tracing_subscriber::FmtSubscriber;

const VIDEO_FRAME_SIZE: usize = 1920 * 1080 * 3 / 2; // YUV420 format (1.5 bytes per pixel)
const AUDIO_FRAME_SIZE: usize = 960 * 2 * 2; // 960 samples * 2 channels * 2 bytes per sample (16-bit)

/// Create a dummy video frame
fn create_video_frame(frame_count: u64, is_keyframe: bool) -> H264Message {
    // Create a dummy NAL unit header for H264
    let mut frame_data = vec![0u8; VIDEO_FRAME_SIZE];
    // Add NAL unit start code
    frame_data[0..4].copy_from_slice(&[0, 0, 0, 1]);
    // Add SPS NAL unit type for keyframes (0x67) or regular frame NAL unit type (0x41)
    frame_data[4] = if is_keyframe { 0x67 } else { 0x41 };
    frame_data[5] = 0x41;

    H264Message {
        data: frame_data,
        timestamp: frame_count,
        frame_type: if is_keyframe { 1 } else { 2 },
        metadata: Default::default(),
        width: Some(1920),
        height: Some(1080),
    }
}

/// Create a dummy audio frame
fn create_audio_frame(frame_count: u64) -> AudioFrame {
    AudioFrame {
        data: vec![0u8; AUDIO_FRAME_SIZE],
        timestamp: frame_count * 1000,
    }
}

async fn run_client(server_addr: SocketAddr) -> Result<()> {
    info!("Starting dummy streaming client");

    // Create source and get its channels
    let source = DummySource::new();
    let state = source.state();
    let video_channel = source.video_channel();
    let audio_channel = source.audio_channel();

    // Create client
    let mut client = StreamClient::new(Box::new(source), 0)?;

    // Setup frame generation intervals
    let mut video_interval = interval(Duration::from_secs_f64(1.0 / TARGET_FPS as f64));
    let mut audio_interval = interval(Duration::from_secs_f64(1.0 / 50.0)); // 50Hz audio

    // Start the connection
    let mut handle = client.connect(server_addr).await?;

    info!("Connected to server ---");

    // Frame generation task
    let frame_task = tokio::spawn({
        let state = state.clone();
        async move {
            let mut frame_count = 0u64;
            loop {
                if !state.is_running() {
                    info!("State no longer running, stopping frame generation");
                    break;
                }

                tokio::select! {
                    _ = video_interval.tick() => {
                        let is_keyframe = frame_count % TARGET_FPS as u64 == 0;
                        let frame = create_video_frame(frame_count, is_keyframe);
                        // Only try to send if we're connected
                        if state.is_connected() && video_channel.tx.try_send(frame).is_ok() {
                            frame_count += 1;
                        }
                    }
                    _ = audio_interval.tick() => {
                        let frame = create_audio_frame(frame_count);
                        // Only try to send if we're connected
                        if state.is_connected() {
                            let _ = audio_channel.tx.try_send(frame);
                        }
                    }
                }
            }
            info!("Frame generation task stopped");
        }
    });

    // Wait for either Ctrl+C or connection termination with a timeout
    let shutdown_result = tokio::select! {
        _ = ctrl_c() => {
            info!("Received Ctrl+C, shutting down...");
            Ok(())
        }
        result = handle.wait() => {
            match result? {
                Ok(()) => {
                    info!("Connection closed gracefully");
                    Ok(())
                }
                Err(e) => {
                    info!("Connection error: {}", e);
                    Ok(())
                }
            }
        }
    };

    // Shutdown everything with timeout protection
    info!("Setting running state to false");
    state.set_running(false);

    info!("Shutting down connection handle");
    if let Err(_) = timeout(Duration::from_secs(5), handle.shutdown()).await {
        warn!("Connection handle shutdown timed out");
    }

    info!("Aborting frame generation task");
    frame_task.abort();
    if let Err(_) = timeout(Duration::from_secs(2), frame_task).await {
        warn!("Frame task shutdown timed out");
    }

    info!("Client shutdown complete");
    shutdown_result
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .with_target(false)
        .with_thread_ids(true)
        .with_file(true)
        .with_line_number(true)
        .init();

    let addr = "127.0.0.1:25502".parse()?;
    run_client(addr).await?;

    info!("Finalizing");
    Ok(())
}
