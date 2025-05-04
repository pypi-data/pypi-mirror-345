use media_server_client::transport::{TransportType, UnifiedTransport};
use media_server_client::ConnectionState;
use std::env;
use std::net::SocketAddr;
use tokio::runtime::Runtime;
use tracing::{error, info};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .with_thread_ids(true)
        .with_file(true)
        .with_line_number(true)
        .init();

    info!("Media Server Client CLI");

    // Parse command-line arguments
    let args: Vec<String> = env::args().collect();
    let transport_type = if args.len() > 1 && args[1] == "quic" {
        TransportType::Quic
    } else {
        TransportType::WebSocket
    };

    let addr: SocketAddr = match args.get(2) {
        Some(addr_str) => addr_str.parse()?,
        None => "127.0.0.1:8080".parse()?,
    };

    info!("Using transport: {:?}", transport_type);
    info!("Connecting to: {}", addr);

    // Create transport
    let transport = UnifiedTransport::new(transport_type);

    // Connect to server
    match transport.connect(addr, 0).await {
        Ok(_) => info!("Connection successful!"),
        Err(e) => error!("Connection failed: {}", e),
    }

    // Check connection state
    if let Ok(state) = transport.get_connection_state().await {
        info!("Connection state: {:?}", state);
    }

    // Check for errors
    if let Ok(Some(error)) = transport.get_error().await {
        error!("Connection error: {}", error);
    }

    // Keep alive for a moment
    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;

    // Shutdown
    if let Err(e) = transport.shutdown().await {
        error!("Error during shutdown: {}", e);
    }

    Ok(())
}
