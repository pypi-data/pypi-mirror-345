use crate::transport::{MediaTransport, MediaTransportError, TransportType};
use async_trait::async_trait;
use dashmap::DashMap;
use media_server_client_common::connection_state::ConnectionState;
use media_server_ws_client::client::WebSocketClient;
use media_server_ws_client::AudioFrame;
use media_server_ws_client::DummySource;
use media_server_ws_client::H264Message;
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use tracing::{error, info};

/// WebSocket transport implementation
pub struct WebSocketTransport {
    source: Arc<DummySource>,
    client: DashMap<(), Arc<tokio::sync::Mutex<WebSocketClient>>>,
}

impl std::fmt::Debug for WebSocketTransport {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("WebSocketTransport")
            .field("client_count", &self.client.len())
            .field("is_running", &self.source.is_running())
            .finish()
    }
}

impl WebSocketTransport {
    /// Create a new WebSocket transport
    pub fn new() -> Self {
        let source = DummySource::new();
        Self {
            source: Arc::new(source),
            client: DashMap::new(),
        }
    }

    /// Connect to a server
    pub async fn connect(
        &self,
        addr: SocketAddr,
        client_id: u64,
    ) -> Result<(), MediaTransportError> {
        info!("Connecting to WebSocket server at {}", addr);

        // Create client with source
        let client =
            WebSocketClient::new(Box::new((*self.source).clone()), client_id).map_err(|e| {
                error!("Failed to create WebSocket client: {}", e);
                MediaTransportError::WebSocketError(format!("Failed to create client: {}", e))
            })?;

        let client = Arc::new(tokio::sync::Mutex::new(client));
        let client_clone = client.clone();

        // Connect to the server using the cloned client
        let mut client_lock = client_clone.lock().await;
        client_lock.connect(addr).await.map_err(|e| {
            error!("Failed to connect to WebSocket server: {}", e);
            MediaTransportError::ConnectionError(format!("Failed to connect: {}", e))
        })?;
        drop(client_lock);

        // Store the client
        self.client.insert((), client);

        info!("Successfully connected to WebSocket server");
        Ok(())
    }

    /// Shutdown the transport
    pub async fn shutdown(&self) -> Result<(), MediaTransportError> {
        info!("Shutting down WebSocket transport");

        // Close the connection
        if let Some((_, client)) = self.client.remove(&()) {
            // We don't need to do anything with the client_lock, just acquire it to ensure
            // we have exclusive access during shutdown
            let _client_lock = client.lock().await;
        }

        // Set source as not running
        self.source.state().set_running(false);

        info!("WebSocket transport shut down successfully");
        Ok(())
    }
}

impl Default for WebSocketTransport {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl MediaTransport for WebSocketTransport {
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

        // Create a WebSocket-compatible H264Message
        let msg = H264Message {
            data,
            timestamp,
            frame_type: if is_keyframe { 1 } else { 2 }, // 1 for I-frame, 2 for P-frame
            metadata,
            width,
            height,
        };

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
        TransportType::WebSocket
    }

    async fn get_connection_state(&self) -> Result<ConnectionState, MediaTransportError> {
        if let Some(_client) = self.client.get(&()) {
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
        if let Some(_client) = self.client.get(&()) {
            // For now, we don't have error tracking in the WebSocket client
            // We could add it later if needed
            Ok(None)
        } else {
            Ok(None)
        }
    }
}
