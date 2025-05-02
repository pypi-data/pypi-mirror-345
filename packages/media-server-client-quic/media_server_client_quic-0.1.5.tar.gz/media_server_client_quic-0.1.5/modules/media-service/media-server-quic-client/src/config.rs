use super::cert::SkipServerVerification;
use anyhow::Result;
use quinn::{ClientConfig, IdleTimeout, VarInt};
use std::sync::Arc;
use std::time::Duration;

pub fn configure_client() -> Result<ClientConfig> {
    let crypto = rustls::ClientConfig::builder()
        .with_safe_defaults()
        .with_custom_certificate_verifier(SkipServerVerification::new())
        .with_no_client_auth();

    let mut client_config = ClientConfig::new(Arc::new(crypto));
    let mut transport = quinn::TransportConfig::default();

    // Optimize for streaming media
    transport.initial_mtu(1200); // Standard MTU size
    transport.min_mtu(1200);
    transport.keep_alive_interval(Some(Duration::from_secs(5)));

    transport.max_concurrent_uni_streams(VarInt::from_u32(200)); // Match server config
    transport.max_concurrent_bidi_streams(VarInt::from_u32(200)); // Match server config

    transport.initial_rtt(Duration::from_millis(100)); // Typical initial RTT
    transport.max_idle_timeout(Some(IdleTimeout::from(VarInt::from_u32(30000)))); // 30 seconds
    transport.send_window(10_000_000); // 10MB window for high throughput
    transport.receive_window(VarInt::from_u32(10_000_000)); // 10MB window for high throughput
    transport.stream_receive_window(VarInt::from_u32(5_000_000)); // 5MB per stream
    transport.packet_threshold(50); // Allow up to 50 packets in flight

    client_config.transport_config(Arc::new(transport));

    Ok(client_config)
}
