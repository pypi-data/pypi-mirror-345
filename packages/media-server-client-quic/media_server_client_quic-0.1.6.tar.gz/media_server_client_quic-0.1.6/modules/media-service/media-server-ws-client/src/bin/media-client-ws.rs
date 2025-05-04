use anyhow::Result;
use media_server_ws_client::client::WebSocketClient;
use media_server_ws_client::H264Message;
use media_server_ws_protocol::source::DummySource;
use media_server_ws_protocol::tracing_config;
use media_server_ws_protocol::TARGET_FPS;
use std::net::SocketAddr;
use std::time::Duration;
use tokio::sync::mpsc;
use tracing::{error, info};
// estimate h264 frame size

const VIDEO_FRAME_SIZE: usize = 19200;

async fn generate_dummy_frames(
    source: &DummySource,
    shutdown_rx: mpsc::Receiver<()>,
) -> Result<()> {
    // Create a tick interval based on target FPS
    let mut interval = tokio::time::interval(Duration::from_secs_f64(1.0 / TARGET_FPS as f64));
    let mut shutdown_rx = shutdown_rx;

    // Prepare dummy data (simulate H264 frame)
    let mut dummy_data = vec![0u8; VIDEO_FRAME_SIZE];
    // Add NAL unit start code and header
    dummy_data[0..4].copy_from_slice(&[0, 0, 0, 1]);
    dummy_data[4] = 0x67; // SPS (keyframe marker)

    // Frame counter
    let mut frame_count = 0;

    // Generate frames until interrupted
    loop {
        tokio::select! {
            _ = interval.tick() => {
                // Create a frame
                let is_keyframe = frame_count % TARGET_FPS as u64 == 0;
                if is_keyframe {
                    dummy_data[4] = 0x67; // SPS (keyframe)
                } else {
                    dummy_data[4] = 0x41; // Regular frame
                }

                let frame = H264Message {
                    data: dummy_data.clone(),
                    timestamp: frame_count,
                    frame_type: if is_keyframe { 1 } else { 2 },
                    metadata: Default::default(),
                    width: Some(1920),
                    height: Some(1080),
                };

                // Add the frame to the source
                source.add_frame(frame, is_keyframe);

                frame_count += 1;
                if frame_count % TARGET_FPS as u64 == 0 {
                    info!("Generated {} frames", frame_count);
                }
            }

            _ = shutdown_rx.recv() => {
                info!("Shutting down frame generator");
                break;
            }
        }
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_config::init_tracing();

    info!("Starting WebSocket client test");

    // Get address from command line or use default
    let addr: SocketAddr = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:25502".to_string())
        .parse()?;

    // Create source and client
    let source = DummySource::new();
    let source_clone = source.clone();
    let mut client = WebSocketClient::new(Box::new(source))?;

    // Create channel for shutdown signal
    let (shutdown_tx, shutdown_rx) = mpsc::channel(1);

    // Connect to server
    info!("Connecting to server at {}", addr);
    let mut handle = client.connect(addr).await?;
    info!("Connected to server");

    // Generate dummy frames task
    let frames_task = tokio::spawn(async move {
        if let Err(e) = generate_dummy_frames(&source_clone, shutdown_rx).await {
            error!("Error generating frames: {}", e);
        }
    });

    // Wait for Ctrl+C or connection error
    tokio::select! {
        _ = tokio::signal::ctrl_c() => {
            info!("Received Ctrl+C, shutting down...");
        }
        result = handle.wait() => {
            match result {
                Ok(Ok(_)) => info!("Connection completed normally"),
                Ok(Err(e)) => info!("Connection error: {}", e),
                Err(e) => info!("Task error: {}", e),
            }
        }
    }

    // Signal frame generation task to stop
    let _ = shutdown_tx.send(()).await;

    // Cancel frame generation task
    frames_task.abort();

    // Shutdown
    info!("Shutting down client...");
    handle.shutdown().await?;

    info!("Client shutdown complete");
    Ok(())
}
