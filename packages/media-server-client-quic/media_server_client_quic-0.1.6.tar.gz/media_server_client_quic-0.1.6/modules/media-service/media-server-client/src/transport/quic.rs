use crate::transport::{create_h264_message, MediaTransport, MediaTransportError, TransportType};
use async_trait::async_trait;
use dashmap::DashMap;
use media_server_client_common::connection_state::ConnectionState;
use media_server_quic_client::source::DummySource;
use media_server_quic_client::stream_client::ConnectionHandle;
use media_server_quic_client::stream_client::StreamClient;
use media_server_quic_client::AudioFrame;
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use tracing::{error, info};
/// QUIC transport implementation
pub struct QuicTransport {
    source: Arc<DummySource>,
    client_handle: DashMap<(), ConnectionHandle>,
}

impl std::fmt::Debug for QuicTransport {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("QuicTransport")
            .field("client_handle_count", &self.client_handle.len())
            .finish()
    }
}

impl QuicTransport {
    /// Create a new QUIC transport
    pub fn new() -> Self {
        let source = DummySource::new();
        Self {
            source: Arc::new(source),
            client_handle: DashMap::new(),
        }
    }

    /// Connect to a server
    pub async fn connect(
        &self,
        addr: SocketAddr,
        client_id: u64,
    ) -> Result<(), MediaTransportError> {
        info!("Connecting to QUIC server at {}", addr);

        // Create a new client with the source
        let mut client =
            StreamClient::new(Box::new((*self.source).clone()), client_id).map_err(|e| {
                error!("Failed to create QUIC client: {}", e);
                MediaTransportError::QuicError(format!("Failed to create client: {}", e))
            })?;

        // Connect to the server
        let handle = client.connect(addr).await.map_err(|e| {
            error!("Failed to connect to QUIC server: {}", e);
            MediaTransportError::ConnectionError(format!("Failed to connect: {}", e))
        })?;

        // Store the client handle
        self.client_handle.insert((), handle);

        info!("Successfully connected to QUIC server");
        Ok(())
    }

    /// Shutdown the transport
    pub async fn shutdown(&self) -> Result<(), MediaTransportError> {
        info!("Shutting down QUIC transport");

        // Close the connection
        if let Some((_, handle)) = self.client_handle.remove(&()) {
            handle.shutdown().await.map_err(|e| {
                error!("Failed to shutdown QUIC connection: {}", e);
                MediaTransportError::QuicError(format!("Failed to shutdown: {}", e))
            })?;
        }

        // Use state() to get a reference to the state
        let state = self.source.state();
        state.set_running(false);

        info!("QUIC transport shut down successfully");
        Ok(())
    }
}

impl Default for QuicTransport {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl MediaTransport for QuicTransport {
    fn add_video_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
        is_keyframe: bool,
        width: Option<u32>,
        height: Option<u32>,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<bool, MediaTransportError> {
        // Check if running
        if !self.source.is_running() {
            return Err(MediaTransportError::NotInitialized);
        }

        // Create H264 message
        let timestamp = timestamp.unwrap_or_else(|| self.source.frame_count());
        let metadata = metadata.unwrap_or_default();
        let msg = create_h264_message(data, timestamp, is_keyframe, width, height, metadata);

        // Since add_frame requires mutable reference, we can't directly call it
        // We'll use the underlying video channel instead
        if self.source.video_channel().tx.clone().try_send(msg).is_ok() {
            self.source.state().increment_frame_count();
            Ok(true)
        } else {
            Ok(false)
        }
    }

    fn add_audio_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
    ) -> Result<bool, MediaTransportError> {
        // Check if running
        if !self.source.is_running() {
            return Err(MediaTransportError::NotInitialized);
        }

        // Create audio frame
        let timestamp = timestamp.unwrap_or_else(|| self.source.frame_count() * 1000);
        let frame = AudioFrame { data, timestamp };

        // Since add_audio_frame requires mutable reference, we can't directly call it
        // We'll use the underlying audio channel instead
        if self
            .source
            .audio_channel()
            .tx
            .clone()
            .try_send(frame)
            .is_ok()
        {
            Ok(true)
        } else {
            Ok(false)
        }
    }

    fn is_running(&self) -> Result<bool, MediaTransportError> {
        Ok(self.source.is_running())
    }

    fn frame_count(&self) -> Result<u64, MediaTransportError> {
        Ok(self.source.frame_count())
    }

    fn transport_type(&self) -> TransportType {
        TransportType::Quic
    }

    async fn get_connection_state(&self) -> Result<ConnectionState, MediaTransportError> {
        if let Some(_handle) = self.client_handle.get(&()) {
            // Check if we have an active client
            if self.source.is_running() {
                Ok(ConnectionState::Connected)
            } else {
                Ok(ConnectionState::Disconnected)
            }
        } else {
            Ok(ConnectionState::Disconnected)
        }
    }

    async fn get_error(&self) -> Result<Option<String>, MediaTransportError> {
        if let Some(_handle) = self.client_handle.get(&()) {
            // For now, we don't have error tracking in the QUIC client
            // We could add it later if needed
            Ok(None)
        } else {
            Ok(None)
        }
    }
}
