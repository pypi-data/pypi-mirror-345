use media_server_client_common::connection_state::ConnectionState;
use media_server_quic_client::H264Message;
use std::collections::HashMap;
use std::fmt::Debug;
use std::net::SocketAddr;
use thiserror::Error;
pub mod quic;
pub mod websocket;

/// Common error type for media transport
#[derive(Error, Debug)]
pub enum MediaTransportError {
    #[error("Connection error: {0}")]
    ConnectionError(String),
    #[error("Runtime error: {0}")]
    RuntimeError(String),
    #[error("Transport not initialized")]
    NotInitialized,
    #[error("Transport already shut down")]
    AlreadyShutDown,
    #[error("Websocket error: {0}")]
    WebSocketError(String),
    #[error("QUIC error: {0}")]
    QuicError(String),
}

/// Transport type enum
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransportType {
    WebSocket,
    Quic,
}

/// Unified interface for media transport
#[async_trait::async_trait]
pub trait MediaTransport: Send + Sync + Debug {
    /// Send H264 frame
    fn add_video_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
        is_keyframe: bool,
        width: Option<u32>,
        height: Option<u32>,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<bool, MediaTransportError>;

    /// Send audio frame
    fn add_audio_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
    ) -> Result<bool, MediaTransportError>;

    /// Check if the transport is running
    fn is_running(&self) -> Result<bool, MediaTransportError>;

    /// Get the current frame count
    fn frame_count(&self) -> Result<u64, MediaTransportError>;

    /// Get the transport type
    fn transport_type(&self) -> TransportType;

    /// Get the current connection state
    async fn get_connection_state(&self) -> Result<ConnectionState, MediaTransportError>;

    /// Get the current error message if any
    async fn get_error(&self) -> Result<Option<String>, MediaTransportError>;
}

/// Unified transport that can be either QUIC or WebSocket
#[derive(Debug)]
pub enum UnifiedTransport {
    Quic(quic::QuicTransport),
    WebSocket(websocket::WebSocketTransport),
}

impl UnifiedTransport {
    /// Create a new unified transport with the specified type
    pub fn new(transport_type: TransportType) -> Self {
        match transport_type {
            TransportType::Quic => UnifiedTransport::Quic(quic::QuicTransport::new()),
            TransportType::WebSocket => {
                UnifiedTransport::WebSocket(websocket::WebSocketTransport::new())
            }
        }
    }

    /// Connect to a server
    pub async fn connect(
        &self,
        addr: SocketAddr,
        client_id: u64,
    ) -> Result<(), MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.connect(addr, client_id).await,
            UnifiedTransport::WebSocket(transport) => transport.connect(addr, client_id).await,
        }
    }

    /// Shutdown the transport
    pub async fn shutdown(&self) -> Result<(), MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.shutdown().await,
            UnifiedTransport::WebSocket(transport) => transport.shutdown().await,
        }
    }
}

#[async_trait::async_trait]
impl MediaTransport for UnifiedTransport {
    fn add_video_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
        is_keyframe: bool,
        width: Option<u32>,
        height: Option<u32>,
        metadata: Option<HashMap<String, String>>,
    ) -> Result<bool, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => {
                transport.add_video_frame(data, timestamp, is_keyframe, width, height, metadata)
            }
            UnifiedTransport::WebSocket(transport) => {
                transport.add_video_frame(data, timestamp, is_keyframe, width, height, metadata)
            }
        }
    }

    fn add_audio_frame(
        &self,
        data: Vec<u8>,
        timestamp: Option<u64>,
    ) -> Result<bool, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.add_audio_frame(data, timestamp),
            UnifiedTransport::WebSocket(transport) => transport.add_audio_frame(data, timestamp),
        }
    }

    fn is_running(&self) -> Result<bool, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.is_running(),
            UnifiedTransport::WebSocket(transport) => transport.is_running(),
        }
    }

    fn frame_count(&self) -> Result<u64, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.frame_count(),
            UnifiedTransport::WebSocket(transport) => transport.frame_count(),
        }
    }

    fn transport_type(&self) -> TransportType {
        match self {
            UnifiedTransport::Quic(_) => TransportType::Quic,
            UnifiedTransport::WebSocket(_) => TransportType::WebSocket,
        }
    }

    async fn get_connection_state(&self) -> Result<ConnectionState, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.get_connection_state().await,
            UnifiedTransport::WebSocket(transport) => transport.get_connection_state().await,
        }
    }

    async fn get_error(&self) -> Result<Option<String>, MediaTransportError> {
        match self {
            UnifiedTransport::Quic(transport) => transport.get_error().await,
            UnifiedTransport::WebSocket(transport) => transport.get_error().await,
        }
    }
}

/// Create an H264 message from raw data
pub fn create_h264_message(
    data: Vec<u8>,
    timestamp: u64,
    is_keyframe: bool,
    width: Option<u32>,
    height: Option<u32>,
    metadata: HashMap<String, String>,
) -> H264Message {
    H264Message {
        data,
        timestamp,
        frame_type: if is_keyframe { 1 } else { 2 },
        metadata,
        width,
        height,
    }
}
