use crate::transport::{MediaTransport, TransportType, UnifiedTransport};
use media_server_client_common::connection_state::ConnectionState;

use pyo3::prelude::*;
use std::collections::HashMap;
use std::net::SocketAddr;
use tokio::runtime::Runtime;
use tracing::{debug, error};

/// Initialize logging with debug level
fn init_logging() {
    use tracing_subscriber::{fmt, EnvFilter};
    let _ = fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("media_streaming=info,info")),
        )
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_file(true)
        .with_line_number(true)
        .with_target(false)
        .try_init();
}

/// Python class for media streaming
#[pyclass]
struct MediaStreamingClient {
    runtime: Option<Runtime>,
    transport: Option<UnifiedTransport>,
    transport_type: TransportType,
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq)]
pub enum PyConnectionState {
    Connected,
    Disconnected,
    Connecting,
    Error,
    Authenticated,
    Streaming,
    ShuttingDown,
}

#[pymethods]
impl MediaStreamingClient {
    /// Create a new streaming client
    #[new]
    fn new(transport_type: &str) -> Self {
        init_logging();

        debug!(
            "Creating new media streaming client with transport type: {}",
            transport_type
        );

        // Determine transport type
        let transport_type = match transport_type.to_lowercase().as_str() {
            // "quic" => TransportType::Quic,
            _ => {
                debug!("Using WebSocket transport (default)");
                TransportType::WebSocket
            }
        };

        Self {
            runtime: None,
            transport: None,
            transport_type,
        }
    }

    /// Connect to a media server
    fn connect(&mut self, host: String, port: u16, client_id: u64) -> PyResult<()> {
        debug!(
            "Connecting to {}:{} with transport {:?}",
            host, port, self.transport_type
        );

        // Create the runtime if it doesn't exist
        if self.runtime.is_none() {
            self.runtime = Some(Runtime::new().map_err(|e| {
                error!("Failed to create runtime: {}", e);
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "Failed to create runtime: {}",
                    e
                ))
            })?);
        }

        let runtime = self.runtime.as_ref().unwrap();

        // Create transport
        let transport = UnifiedTransport::new(self.transport_type);

        // Connect to server
        let addr = format!("{}:{}", host, port)
            .parse::<SocketAddr>()
            .map_err(|e| {
                error!("Invalid address: {}", e);
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid address: {}", e))
            })?;

        // Connect using the runtime
        runtime.block_on(async {
            transport.connect(addr, client_id).await.map_err(|e| {
                error!("Failed to connect: {}", e);
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to connect: {}", e))
            })
        })?;

        // Save the transport
        self.transport = Some(transport);

        debug!("Successfully connected to media server");
        Ok(())
    }

    /// Send a video frame
    #[pyo3(signature = (data, timestamp=None, is_keyframe=None, width=None, height=None, metadata=None))]
    fn send_video_frame(
        &self,
        _py: Python<'_>,
        data: &'_ [u8],
        timestamp: Option<u64>,
        is_keyframe: Option<bool>,
        width: Option<u32>,
        height: Option<u32>,
        metadata: Option<HashMap<String, String>>,
    ) -> PyResult<bool> {
        if let Some(transport) = &self.transport {
            // Convert PyBytes to Vec<u8>
            let data = data.to_vec();
            let is_keyframe = is_keyframe.unwrap_or(false);

            let result =
                transport.add_video_frame(data, timestamp, is_keyframe, width, height, metadata);

            match result {
                Ok(result) => Ok(result),
                Err(e) => {
                    error!("Failed to send video frame: {}", e);
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Failed to send video frame: {}",
                        e
                    )))
                }
            }
        } else {
            error!("Transport not connected");
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Not connected to a server",
            ))
        }
    }

    /// Alias for send_video_frame
    #[pyo3(signature = (data, timestamp=None, is_keyframe=None, width=None, height=None, metadata=None))]
    fn add_frame(
        &self,
        py: Python<'_>,
        data: &'_ [u8],
        timestamp: Option<u64>,
        is_keyframe: Option<bool>,
        width: Option<u32>,
        height: Option<u32>,
        metadata: Option<HashMap<String, String>>,
    ) -> PyResult<bool> {
        self.send_video_frame(py, data, timestamp, is_keyframe, width, height, metadata)
    }

    /// Alias for send_video_frame with different parameter order (for backward compatibility)
    #[pyo3(signature = (data, timestamp=None, is_keyframe=None, metadata=None, width=None, height=None))]
    fn h264_frame(
        &self,
        py: Python<'_>,
        data: &'_ [u8],
        timestamp: Option<u64>,
        is_keyframe: Option<bool>,
        metadata: Option<HashMap<String, String>>,
        width: Option<u32>,
        height: Option<u32>,
    ) -> PyResult<bool> {
        self.send_video_frame(py, data, timestamp, is_keyframe, width, height, metadata)
    }

    /// Send an audio frame
    #[pyo3(signature = (data, timestamp=None))]
    fn send_audio_frame(&self, data: &[u8], timestamp: Option<u64>) -> PyResult<bool> {
        if let Some(transport) = &self.transport {
            let data = data.to_vec();
            let result = transport.add_audio_frame(data, timestamp);

            match result {
                Ok(result) => Ok(result),
                Err(e) => {
                    error!("Failed to send audio frame: {}", e);
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Failed to send audio frame: {}",
                        e
                    )))
                }
            }
        } else {
            error!("Transport not connected");
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Not connected to a server",
            ))
        }
    }

    /// Alias for send_audio_frame
    #[pyo3(signature = (data, timestamp=None))]
    fn add_audio_frame(&self, data: &[u8], timestamp: Option<u64>) -> PyResult<bool> {
        self.send_audio_frame(data, timestamp)
    }

    /// Disconnect from the server
    fn disconnect(&mut self) -> PyResult<()> {
        if let Some(transport) = &self.transport {
            if let Some(runtime) = &self.runtime {
                debug!("Disconnecting from server");
                runtime.block_on(async {
                    transport.shutdown().await.map_err(|e| {
                        error!("Failed to disconnect: {}", e);
                        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                            "Failed to disconnect: {}",
                            e
                        ))
                    })
                })?;
                debug!("Successfully disconnected from server");
            }
            self.transport = None;
        }
        Ok(())
    }

    /// Check if the transport is running
    fn is_running(&self) -> PyResult<bool> {
        if let Some(transport) = &self.transport {
            match transport.is_running() {
                Ok(running) => Ok(running),
                Err(e) => {
                    error!("Failed to check if transport is running: {}", e);
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Failed to check if transport is running: {}",
                        e
                    )))
                }
            }
        } else {
            Ok(false)
        }
    }

    /// Get the frame count
    fn get_frame_count(&self) -> PyResult<u64> {
        if let Some(transport) = &self.transport {
            match transport.frame_count() {
                Ok(count) => Ok(count),
                Err(e) => {
                    error!("Failed to get frame count: {}", e);
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Failed to get frame count: {}",
                        e
                    )))
                }
            }
        } else {
            Ok(0)
        }
    }

    /// Alias for get_frame_count
    fn frame_count(&self) -> PyResult<u64> {
        self.get_frame_count()
    }

    /// Get the transport type as a string
    fn get_transport_type(&self) -> String {
        match self.transport_type {
            TransportType::Quic => "quic".to_string(),
            TransportType::WebSocket => "websocket".to_string(),
        }
    }

    /// Get the current connection state
    fn get_connection_state(&self) -> PyResult<PyConnectionState> {
        if let Some(transport) = &self.transport {
            if let Some(runtime) = &self.runtime {
                let state = runtime.block_on(async {
                    transport.get_connection_state().await.map_err(|e| {
                        error!("Failed to get connection state: {}", e);
                        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                            "Failed to get connection state: {}",
                            e
                        ))
                    })
                })?;
                Ok(match state {
                    ConnectionState::Connected => PyConnectionState::Connected,
                    ConnectionState::Disconnected => PyConnectionState::Disconnected,
                    ConnectionState::Connecting => PyConnectionState::Connecting,
                    ConnectionState::Error => PyConnectionState::Error,
                    ConnectionState::Authenticated => PyConnectionState::Authenticated,
                    ConnectionState::Streaming => PyConnectionState::Streaming,
                    ConnectionState::ShuttingDown => PyConnectionState::ShuttingDown,
                })
            } else {
                Ok(PyConnectionState::Disconnected)
            }
        } else {
            Ok(PyConnectionState::Disconnected)
        }
    }

    /// Get the current error message if any
    fn get_error(&self) -> PyResult<Option<String>> {
        if let Some(transport) = &self.transport {
            if let Some(runtime) = &self.runtime {
                runtime.block_on(async {
                    transport.get_error().await.map_err(|e| {
                        error!("Failed to get error: {}", e);
                        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                            "Failed to get error: {}",
                            e
                        ))
                    })
                })
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }
}

/// Python module initialization
#[pymodule]
pub fn media_server_client(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<MediaStreamingClient>()?;
    m.add_class::<PyConnectionState>()?;
    Ok(())
}
