use crate::ControlPacket;
use crate::MediaPacket;
use anyhow::Result;
use bytes::{BufMut, BytesMut};
use dashmap::DashMap;
use once_cell::sync::Lazy;
use quinn;
use std::hash::{Hash, Hasher};
use std::sync::atomic::{AtomicUsize, Ordering};
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
    read_buffer: BytesMut,
    write_buffer: BytesMut,
    len_buffer: [u8; 4],
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
            read_buffer: get_buffer(INITIAL_BUFFER_SIZE),
            write_buffer: get_buffer(INITIAL_BUFFER_SIZE),
            len_buffer: [0u8; 4],
            last_packet_size: 0,
        }
    }

    #[inline]
    pub async fn read_packet(
        &mut self,
        recv: &mut quinn::RecvStream,
    ) -> Result<Option<MediaPacket>> {
        // Read length prefix
        match recv.read_exact(&mut self.len_buffer).await {
            Ok(_) => (),
            Err(e)
                if e.to_string().contains("connection closed")
                    || e.to_string().contains("0 bytes") =>
            {
                return Ok(None);
            }
            Err(_) => {
                //error!("Failed to read packet length: {}", e);
                return Ok(None);
            }
        }

        let packet_len = u32::from_be_bytes(self.len_buffer) as usize;
        if packet_len == 0 {
            return Ok(Some(MediaPacket::Control(ControlPacket::KeepAlive)));
        }

        // Ensure buffer capacity
        if self.read_buffer.capacity() < packet_len {
            let mut new_buf = get_buffer(packet_len);
            std::mem::swap(&mut self.read_buffer, &mut new_buf);
            return_buffer(new_buf);
        }
        self.read_buffer.clear();
        self.read_buffer.resize(packet_len, 0);

        // Read packet data
        if let Err(e) = recv.read_exact(&mut self.read_buffer).await {
            error!("Failed to read packet data: {}", e);
            return Ok(None);
        }

        // Decode packet
        match MediaPacket::from_bytes(&self.read_buffer) {
            Ok(packet) => Ok(Some(packet)),
            Err(e) if e.to_string().contains("End of stream") => Ok(None),
            Err(_e) => {
                debug!("Failed to decode packet");
                Ok(Some(MediaPacket::Control(ControlPacket::KeepAlive)))
            }
        }
    }

    #[inline]
    pub async fn write_packet(
        &mut self,
        send: &mut quinn::SendStream,
        packet: &MediaPacket,
    ) -> Result<usize> {
        // Pre-encode to temporary buffer to know exact size
        let mut vec_buffer = Vec::with_capacity(self.write_buffer.capacity());
        packet.to_bytes_into(&mut vec_buffer)?;
        let data_len = vec_buffer.len();

        // Prepare final buffer with exact size
        let total_len = data_len + 4;
        if self.write_buffer.capacity() < total_len {
            let mut new_buf = get_buffer(total_len);
            std::mem::swap(&mut self.write_buffer, &mut new_buf);
            return_buffer(new_buf);
        }
        self.write_buffer.clear();

        // Write length prefix and data
        self.write_buffer
            .put_slice(&(data_len as u32).to_be_bytes());
        self.write_buffer.put_slice(&vec_buffer);

        // Single write operation
        send.write_all(&self.write_buffer[..total_len]).await?;

        self.last_packet_size = total_len;
        Ok(total_len)
    }

    #[inline]
    pub fn last_packet_size(&self) -> usize {
        self.last_packet_size
    }
}

impl Drop for PacketIO {
    fn drop(&mut self) {
        return_buffer(std::mem::replace(&mut self.read_buffer, BytesMut::new()));
        return_buffer(std::mem::replace(&mut self.write_buffer, BytesMut::new()));
    }
}
