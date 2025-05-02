use crate::MediaPacket;
use anyhow::{anyhow, Result};
use bytes::BytesMut;
use dashmap::DashMap;
use once_cell::sync::Lazy;
use std::hash::{Hash, Hasher};
use std::sync::atomic::{AtomicUsize, Ordering};
use tokio_tungstenite::tungstenite::Message;
use tracing::{debug, error};
const INITIAL_BUFFER_SIZE: usize = 16 * 1024; // Start with 16KB
const MAX_BUFFER_SIZE: usize = 8 * 1024 * 1024; // Max 8MB
const BUFFER_SHRINK_THRESHOLD: usize = 4 * 1024 * 1024; // Shrink if over 4MB
const MAX_POOL_SIZE: usize = 32; // Limit per thread

// Thread-local buffer pool
static BUFFER_POOL: Lazy<DashMap<usize, Vec<BytesMut>>> = Lazy::new(DashMap::new);
static POOL_SIZE: AtomicUsize = AtomicUsize::new(0);

#[inline]
fn get_thread_id() -> usize {
    let mut s = std::collections::hash_map::DefaultHasher::new();
    std::thread::current().id().hash(&mut s);
    s.finish() as usize
}

fn get_buffer(required_size: usize) -> BytesMut {
    let thread_id = get_thread_id();

    // Try to get a buffer from the pool that's close to our size
    if let Some(mut pool) = BUFFER_POOL.get_mut(&thread_id) {
        for i in (0..pool.len()).rev() {
            let buf = &pool[i];
            // Use a buffer if it's within 2x of what we need
            if buf.capacity() >= required_size && buf.capacity() <= required_size * 2 {
                let buf = pool.swap_remove(i);
                POOL_SIZE.fetch_sub(1, Ordering::Relaxed);
                debug!("Reused buffer of size {}", buf.capacity());
                return buf;
            }
        }
    }

    // Create new buffer with optimal size
    let size = required_size.clamp(INITIAL_BUFFER_SIZE, MAX_BUFFER_SIZE);
    debug!("Created new buffer of size {}", size);
    BytesMut::with_capacity(size)
}

fn return_buffer(mut buf: BytesMut) {
    if POOL_SIZE.load(Ordering::Relaxed) >= MAX_POOL_SIZE {
        return;
    }

    let cap = buf.capacity();
    // Only keep reasonably sized buffers
    if !(INITIAL_BUFFER_SIZE..=MAX_BUFFER_SIZE).contains(&cap) {
        return;
    }

    buf.clear();
    // For oversized buffers, create a new one with smaller capacity
    if cap > BUFFER_SHRINK_THRESHOLD {
        let mut new_buf = BytesMut::with_capacity(BUFFER_SHRINK_THRESHOLD);
        new_buf.extend_from_slice(&buf);
        buf = new_buf;
    }

    let thread_id = get_thread_id();
    BUFFER_POOL.entry(thread_id).or_default().push(buf);
    POOL_SIZE.fetch_add(1, Ordering::Relaxed);
}

pub struct PacketIO {
    buffer: BytesMut,       // Reusable buffer for encoding operations
    write_buffer: BytesMut, // Buffer for encoding operations
    last_packet_size: usize,
}

impl Default for PacketIO {
    fn default() -> Self {
        Self::new()
    }
}

impl PacketIO {
    pub fn new() -> Self {
        Self {
            buffer: get_buffer(INITIAL_BUFFER_SIZE),
            write_buffer: get_buffer(INITIAL_BUFFER_SIZE),
            last_packet_size: 0,
        }
    }

    /// Converts MediaPacket to WebSocket Message
    pub fn encode_packet(&mut self, packet: &MediaPacket) -> Result<Message> {
        // Serialize to a Vec<u8> first (unfortunately we need this intermediate step)
        let data = bitcode::serialize(packet)
            .map_err(|e| anyhow!("Bitcode serialization error: {}", e))?;

        self.last_packet_size = data.len();

        // If our buffer is too small for future use, resize it
        if self.write_buffer.capacity() < data.len() {
            let new_capacity = (data.len() * 3) / 2; // Grow by 50%
            let mut new_buf = get_buffer(new_capacity);
            std::mem::swap(&mut self.write_buffer, &mut new_buf);
            return_buffer(new_buf);
        }

        // Return as binary message
        Ok(Message::Binary(data))
    }

    /// Decodes WebSocket Message to MediaPacket
    pub fn decode_packet(&mut self, message: &Message) -> Result<Option<MediaPacket>> {
        match message {
            Message::Binary(data) => {
                self.last_packet_size = data.len();

                // If we frequently get large packets, ensure our read buffer is large enough
                if self.buffer.capacity() < data.len() && data.len() < MAX_BUFFER_SIZE {
                    let new_capacity = (data.len() * 3) / 2; // Grow by 50%
                    let mut new_buf = get_buffer(new_capacity);
                    std::mem::swap(&mut self.buffer, &mut new_buf);
                    return_buffer(new_buf);
                    debug!("Increased read buffer size to {}", new_capacity);
                }

                // Decode directly from the binary data
                let packet = bitcode::deserialize(data)
                    .map_err(|e| anyhow!("Bitcode deserialization error: {}", e))?;

                Ok(Some(packet))
            }
            Message::Close(_) => Ok(None),
            _ => {
                error!("Unexpected message type");
                Ok(None)
            }
        }
    }

    #[inline]
    pub fn last_packet_size(&self) -> usize {
        self.last_packet_size
    }
}

impl Drop for PacketIO {
    fn drop(&mut self) {
        return_buffer(std::mem::replace(&mut self.buffer, BytesMut::new()));
        return_buffer(std::mem::replace(&mut self.write_buffer, BytesMut::new()));
    }
}
