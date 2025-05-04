use anyhow::Result;
use flume::Receiver;
use media_server_quic_protocol::common::AudioFrame;
use media_server_quic_protocol::common::StreamStats;
use media_server_quic_protocol::current_timestamp_micros;
use media_server_quic_protocol::packet_io::PacketIO;
use media_server_quic_protocol::ControlPacket;
use media_server_quic_protocol::MediaPacket;
use protobuf_types::media_streaming::H264Message;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;
use tokio::time::Instant;
use tracing::{debug, info};
const KEEP_ALIVE_INTERVAL: Duration = Duration::from_secs(1);
const STATS_INTERVAL: Duration = Duration::from_secs(5);

pub async fn handle_video_stream(
    mut send: quinn::SendStream,
    video_rx: Receiver<H264Message>,
    stats: Arc<Mutex<StreamStats>>,
    start_time: Instant,
) -> Result<()> {
    let mut packet_io = PacketIO::new();
    let mut frame_count = 0;

    while let Ok(frame) = video_rx.recv_async().await {
        let frame_size = frame.data.len();
        let packet = MediaPacket::Video(frame);

        match packet_io.write_packet(&mut send, &packet).await {
            Ok(size) => {
                frame_count += 1;
                let mut stats = stats.lock().await;
                stats.add_video_packet(size);
                stats.network.update_throughput(size as f64);

                if frame_count % 30 == 0 {
                    let elapsed = start_time.elapsed().as_secs_f64();
                    let fps = frame_count as f64 / elapsed;
                    debug!(
                        "Sent {} video frames ({:.2} FPS) - Size: {:.2}KB",
                        frame_count,
                        fps,
                        frame_size as f64 / 1024.0
                    );
                }
            }
            Err(e) => {
                debug!("Failed to send video frame: {}", e);
                break;
            }
        }
    }

    debug!("Video stream handler exiting");
    Ok(())
}

pub async fn handle_audio_stream(
    mut send: quinn::SendStream,
    audio_rx: Receiver<AudioFrame>,
    stats: Arc<Mutex<StreamStats>>,
    start_time: Instant,
) -> Result<()> {
    let mut packet_io = PacketIO::new();
    let mut frame_count = 0;

    while let Ok(frame) = audio_rx.recv_async().await {
        let frame_size = frame.data.len();
        let packet = MediaPacket::Audio(frame);

        match packet_io.write_packet(&mut send, &packet).await {
            Ok(size) => {
                frame_count += 1;
                let mut stats = stats.lock().await;
                stats.add_audio_packet(size);
                stats.network.update_throughput(size as f64);

                if frame_count % 50 == 0 {
                    let elapsed = start_time.elapsed().as_secs_f64();
                    let fps = frame_count as f64 / elapsed;
                    debug!(
                        "Sent {} audio frames ({:.2} FPS) - Size: {:.2}KB",
                        frame_count,
                        fps,
                        frame_size as f64 / 1024.0
                    );
                }
            }
            Err(e) => {
                debug!("Failed to send audio frame: {}", e);
                break;
            }
        }
    }

    debug!("Audio stream handler exiting");
    Ok(())
}

pub async fn handle_keep_alive(
    _client_id: u64,
    mut send: quinn::SendStream,
    mut recv: quinn::RecvStream,
    stats: Arc<Mutex<StreamStats>>,
) -> Result<()> {
    let mut packet_io = PacketIO::new();
    let mut sequence_number = 0;
    let mut interval = tokio::time::interval(KEEP_ALIVE_INTERVAL);

    loop {
        tokio::select! {
            _ = interval.tick() => {
                let timestamp = current_timestamp_micros();
                let ping = MediaPacket::Control(ControlPacket::Ping {
                    sequence_number,
                    timestamp,
                });

                match packet_io.write_packet(&mut send, &ping).await {
                    Ok(size) => {
                        debug!("Sent ping {} - size: {}B", sequence_number, size);
                        sequence_number += 1;
                    }
                    Err(e) => {
                        debug!("Failed to send ping: {}", e);
                        return Ok(());
                    }
                }
            }
            result = packet_io.read_packet(&mut recv) => {
                match result? {
                    Some(MediaPacket::Control(ControlPacket::Pong { sequence_number, timestamp, receive_timestamp })) => {
                        let now = current_timestamp_micros();
                        let rtt = Duration::from_micros(now - timestamp);
                        let transit = Duration::from_micros(receive_timestamp - timestamp);
                        let return_time = Duration::from_micros(now - receive_timestamp);

                        let mut stats = stats.lock().await;
                        stats.network.update_rtt(rtt);
                        stats.network.update_jitter(transit);
                        stats.network.update_packet_loss(false);

                        debug!(
                            "Received pong {} - RTT: {:?}, transit: {:?}, return: {:?}",
                            sequence_number, rtt, transit, return_time
                        );
                    }
                    Some(MediaPacket::Control(ControlPacket::StopStream)) => return Ok(()),
                    //None => return Ok(()), // Connection closed
                    _ => continue,
                }
            }
        }
    }
}

pub async fn monitor_stats(stats: Arc<Mutex<StreamStats>>, client_id: u64) -> Result<()> {
    let mut interval = tokio::time::interval(STATS_INTERVAL);

    loop {
        interval.tick().await;
        let stats = stats.lock().await;
        info!("Client {} stats:\n{}", client_id, stats.get_stats());
    }
}
