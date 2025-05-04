use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use futures_util::{
    SinkExt, StreamExt,
};
use tokio::io::{AsyncRead, AsyncWrite};
use tokio::sync::Mutex;
use tokio::task::JoinHandle;
use media_server_ws_protocol::config::PING_INTERVAL;
use media_server_ws_protocol::config::CONNECTION_TIMEOUT;
use tokio_tungstenite::{connect_async, tungstenite::Message, WebSocketStream};
use tracing::{debug, error, info};
use media_server_ws_protocol::{ControlPacket, MediaPacket, MediaSource, StreamStats, StreamType};
use media_server_ws_protocol::packet_io::PacketIO;
use media_server_ws_protocol::current_timestamp_micros;
use crate::handlers::monitor_stats;
use media_server_client_common::connection_state::{ConnectionState, ConnectionStateTracker};
pub struct WebSocketClient {
    client_id: u64,
    media_source: Option<Box<dyn MediaSource>>,
    stats: Arc<Mutex<StreamStats>>,
    state: ConnectionStateTracker,
}

pub struct ConnectionHandle {
    task: JoinHandle<Result<()>>,
    state: ConnectionStateTracker,
}

impl ConnectionHandle {
    pub async fn shutdown(self) -> Result<()> {
        self.state.shutdown().await;
        self.task.await?
    }

    pub async fn get_state(&self) -> ConnectionState {
        self.state.get_state().await
    }

    pub async fn get_error(&self) -> Option<String> {
        self.state.get_error().await
    }

    pub async fn wait(&mut self) -> Result<Result<()>> {
        let task = std::mem::replace(&mut self.task, tokio::task::spawn(async { Ok(()) }));
        Ok(task.await?)
    }
}

impl WebSocketClient {
    pub fn new(media_source: Box<dyn MediaSource>, client_id: u64) -> Result<Self> {
        Ok(Self {
            client_id,
            media_source: Some(media_source),
            stats: Arc::new(Mutex::new(StreamStats::new())),
            state: ConnectionStateTracker::new(),
        })
    }

    /// Perform the hello handshake with the server
    async fn perform_hello_handshake<S>(
        ws_stream: &mut WebSocketStream<S>,
        packet_io: &mut PacketIO,
        _source: &mut Box<dyn MediaSource>,
        client_id: u64,
    ) -> Result<(String, u64)>
    where
        S: AsyncRead + AsyncWrite + Unpin,
    {
        // Send client hello
        let client_hello = MediaPacket::Control(ControlPacket::Hello {
            version: 1,
            nonce: None,
            capabilities: vec!["h264".to_string(), "opus".to_string(), "keep-alive".to_string()],
            client_id: Some(client_id),
        });

        info!("Sending client hello");
        let hello_msg = packet_io.encode_packet(&client_hello)?;
        ws_stream.send(hello_msg).await?;

        // Wait for server hello
        if let Some(msg) = ws_stream.next().await {
            let msg = msg?;
            if let Some(packet) = packet_io.decode_packet(&msg)? {
                if let MediaPacket::Control(ControlPacket::Hello {
                    version,
                    nonce,
                    capabilities,
                    client_id,
                }) = packet
                {
                    info!("Received server hello - version: {}, nonce: {:?}, capabilities: {:?}, client_id: {:?}", 
                        version, nonce, capabilities, client_id);

                    if version != 1 {
                        return Err(anyhow::anyhow!("Unsupported protocol version: {}", version));
                    }

                    Ok((nonce.unwrap_or_default(), client_id.unwrap_or_default()))
                } else {
                    Err(anyhow::anyhow!("Invalid server hello message"))
                }
            } else {
                Err(anyhow::anyhow!("Invalid message format"))
            }
        } else {
            Err(anyhow::anyhow!("No response from server"))
        }
    }

    /// Perform authentication with the server
    async fn perform_auth<S>(
        ws_stream: &mut WebSocketStream<S>,
        packet_io: &mut PacketIO,
        nonce: &str,
        client_id: u64,
    ) -> Result<()>
    where
        S: AsyncRead + AsyncWrite + Unpin,
    {
        // Send auth
        let auth = MediaPacket::Control(ControlPacket::Auth {
            auth: "test-auth".to_string(),
            serial: "test-serial".to_string(),
            sign: nonce.as_bytes().to_vec(),
            stream_id: client_id,
        });

        info!("Sending auth request");
        let auth_msg = packet_io.encode_packet(&auth)?;
        ws_stream.send(auth_msg).await?;

        // Wait for auth response
        if let Some(msg) = ws_stream.next().await {
            let msg = msg?;
            if let Some(packet) = packet_io.decode_packet(&msg)? {
                if let MediaPacket::Control(ControlPacket::AuthResponse { success, message }) =
                    packet
                {
                    if success {
                        info!("Auth successful");
                        Ok(())
                    } else {
                        Err(anyhow::anyhow!(
                            "Auth failed: {}",
                            message.unwrap_or_default()
                        ))
                    }
                } else {
                    Err(anyhow::anyhow!("Invalid auth response"))
                }
            } else {
                Err(anyhow::anyhow!("Invalid message format"))
            }
        } else {
            Err(anyhow::anyhow!("No response from server"))
        }
    }

    /// Setup a stream with the server
    async fn setup_stream<S>(
        ws_stream: &mut WebSocketStream<S>,
        packet_io: &mut PacketIO,
        stream_type: StreamType,
    ) -> Result<()>
    where
        S: AsyncRead + AsyncWrite + Unpin,
    {
        // Send stream setup message
        let start = MediaPacket::Control(ControlPacket::StartStream { stream_type });
        let start_msg = packet_io.encode_packet(&start)?;
        ws_stream.send(start_msg).await?;

        // Wait for ack
        if let Some(msg) = ws_stream.next().await {
            let msg = msg?;
            if let Some(packet) = packet_io.decode_packet(&msg)? {
                if let MediaPacket::Control(ControlPacket::StartStream {
                    stream_type: ack_type,
                }) = packet
                {
                    if ack_type == stream_type {
                        info!("Stream setup successful for {:?}", stream_type);
                        Ok(())
                    } else {
                        Err(anyhow::anyhow!("Stream type mismatch"))
                    }
                } else {
                    Err(anyhow::anyhow!("Invalid stream ack"))
                }
            } else {
                Err(anyhow::anyhow!("Invalid message format"))
            }
        } else {
            Err(anyhow::anyhow!("No response from server"))
        }
    }

    pub async fn connect(&mut self, server_addr: SocketAddr) -> Result<ConnectionHandle> {
        info!("Starting connection to WebSocket server at {}", server_addr);

        // Take ownership of the media source
        let mut source = self
            .media_source
            .take()
            .ok_or_else(|| anyhow::anyhow!("No media source available"))?;

        // Start the media source immediately
        source.start().await?;
        source.on_connect().await?;

        // Clone necessary components for the connection task
        let stats = self.stats.clone();
        let state = self.state.clone();
        let client_id = self.client_id;

        // Set initial state
        state.set_state(ConnectionState::Connecting).await;

        // Spawn the connection handling task
        let task = tokio::spawn(async move {
            let result: Result<()> = async {
                // Connect to the WebSocket server
                let url = format!("ws://{}:{}", server_addr.ip(), server_addr.port());

                info!("Connecting to WebSocket at {}", url);
                let (mut ws_stream, _) =
                    tokio::time::timeout(CONNECTION_TIMEOUT, connect_async(url)).await??;
                state.set_state(ConnectionState::Connected).await;

                // Initialize packet IO
                let mut packet_io = PacketIO::new();

                // Perform hello handshake first
                let (nonce, client_id) =
                    Self::perform_hello_handshake(&mut ws_stream, &mut packet_io, &mut source, client_id)
                        .await?;

                // Perform auth
                Self::perform_auth(&mut ws_stream, &mut packet_io, &nonce, client_id).await?;
                source.on_auth_success(client_id).await?;
                state.set_state(ConnectionState::Authenticated).await;

                // Setup streams
                Self::setup_stream(&mut ws_stream, &mut packet_io, StreamType::Video).await?;
                source.on_stream_ready(StreamType::Video).await?;

                Self::setup_stream(&mut ws_stream, &mut packet_io, StreamType::Audio).await?;
                source.on_stream_ready(StreamType::Audio).await?;

                Self::setup_stream(&mut ws_stream, &mut packet_io, StreamType::KeepAlive).await?;
                source.on_stream_ready(StreamType::KeepAlive).await?;

                state.set_state(ConnectionState::Streaming).await;

                // Split the WebSocket stream
                let (mut ws_sender, mut ws_receiver) = ws_stream.split();

                // Get channels for streaming
                let video_rx = source.video_channel().subscribe();
                let audio_rx = source.audio_channel().subscribe();

                let _start = std::time::Instant::now();
                let mut ping_interval = tokio::time::interval(PING_INTERVAL);
                let mut sequence_number = 0;
                let mut shutdown_rx = state.subscribe_shutdown();

                // Spawn a separate task to monitor stats
                let stats_clone = stats.clone();
                let stats_task = tokio::spawn(async move {
                    if let Err(e) = monitor_stats(stats_clone, client_id).await {
                        error!("Stats monitor error: {}", e);
                    }
                });

                // Main event loop
                loop {
                    tokio::select! {
                        // Handle incoming WebSocket messages
                        Some(msg) = ws_receiver.next() => {
                            match msg {
                                Ok(msg) => {
                                    if let Ok(Some(packet)) = packet_io.decode_packet(&msg) {
                                        match packet {
                                            MediaPacket::Control(ControlPacket::Pong { sequence_number, timestamp, receive_timestamp }) => {
                                                let now = current_timestamp_micros();
                                                let rtt = Duration::from_micros(now - timestamp);
                                                let transit = Duration::from_micros(receive_timestamp - timestamp);

                                                // Update network stats
                                                let mut stats_lock = stats.lock().await;
                                                stats_lock.network.update_rtt(rtt);
                                                stats_lock.network.update_jitter_from_transit(transit);
                                                stats_lock.network.update_packet_loss(false);

                                                debug!(
                                                    "Received pong {} - RTT: {:?}, transit: {:?}",
                                                    sequence_number, rtt, transit
                                                );
                                            },
                                            // Handle other control packets as needed
                                            _ => {}
                                        }
                                    } else if let Message::Close(_) = msg {
                                        info!("Received close frame from server");
                                        break;
                                    }
                                },
                                Err(e) => {
                                    error!("Error receiving WebSocket message: {}", e);
                                    state.set_error(e.to_string()).await;
                                    break;
                                }
                            }
                        },

                        // Send video frames
                        Ok(frame) = video_rx.recv_async() => {
                            let frame_size = frame.data.len();
                            let packet = MediaPacket::Video(frame);
                            
                            if let Ok(message) = packet_io.encode_packet(&packet) {
                                if let Err(e) = ws_sender.send(message).await {
                                    error!("Failed to send video frame: {}", e);
                                    state.set_error(e.to_string()).await;
                                    break;
                                }
                                
                                // Update stats
                                let mut stats_lock = stats.lock().await;
                                stats_lock.add_video_packet(frame_size);
                                stats_lock.network.update_throughput(frame_size as f64);
                                drop(stats_lock);
                                
                                debug!("Sent video frame: {} bytes", frame_size);
                            }
                        },

                        // Send audio frames
                        Ok(frame) = audio_rx.recv_async() => {
                            let frame_size = frame.data.len();
                            let packet = MediaPacket::Audio(frame);
                            
                            if let Ok(message) = packet_io.encode_packet(&packet) {
                                if let Err(e) = ws_sender.send(message).await {
                                    error!("Failed to send audio frame: {}", e);
                                    state.set_error(e.to_string()).await;
                                    break;
                                }
                                
                                // Update stats
                                let mut stats_lock = stats.lock().await;
                                stats_lock.add_audio_packet(frame_size);
                                stats_lock.network.update_throughput(frame_size as f64);
                                drop(stats_lock);
                                
                                debug!("Sent audio frame: {} bytes", frame_size);
                            }
                        },

                        // Send keep-alive ping
                        _ = ping_interval.tick() => {
                            let timestamp = current_timestamp_micros();
                            let ping = MediaPacket::Control(ControlPacket::Ping {
                                sequence_number,
                                timestamp,
                            });

                            if let Ok(message) = packet_io.encode_packet(&ping) {
                                if let Err(e) = ws_sender.send(message).await {
                                    error!("Failed to send ping: {}", e);
                                    state.set_error(e.to_string()).await;
                                    break;
                                }
                                
                                debug!("Sent ping {} to server", sequence_number);
                                sequence_number += 1;
                            }
                        },

                        // Handle shutdown signal
                        _ = shutdown_rx.recv() => {
                            info!("Received shutdown signal");
                            break;
                        }
                    }
                }

                // Abort stats monitoring task
                stats_task.abort();

                // Send stop stream message
                let stop = MediaPacket::Control(ControlPacket::StopStream);
                if let Ok(message) = packet_io.encode_packet(&stop) {
                    let _ = ws_sender.send(message).await; // Ignore errors during shutdown
                }

                source.on_disconnect().await?;
                state.set_state(ConnectionState::Disconnected).await;
                Ok(())
            }
            .await;

            match result {
                Ok(_) => {
                    info!("Connection closed gracefully");
                    Ok(())
                }
                Err(e) => {
                    error!("Connection failed: {}", e);
                    state.set_error(e.to_string()).await;
                    source
                        .on_stream_error(StreamType::Video, e.to_string())
                        .await?;
                    source.on_disconnect().await?;
                    Err(e)
                }
            }
        });

        Ok(ConnectionHandle {
            task,
            state: self.state.clone(),
        })
    }

    pub async fn shutdown(&self) {
        self.state.shutdown().await;
    }
}

impl Clone for WebSocketClient {
    fn clone(&self) -> Self {
        Self {
            client_id: self.client_id,
            media_source: None,
            stats: self.stats.clone(),
            state: self.state.clone(),
        }
    }
}

// Helper type for monitoring tasks
pub struct NamedTask<T = Result<(), anyhow::Error>> {
    pub name: &'static str,
    pub task: JoinHandle<T>,
}

impl<T> NamedTask<T> {
    pub fn new(name: &'static str, task: JoinHandle<T>) -> Self {
        Self { name, task }
    }
}
