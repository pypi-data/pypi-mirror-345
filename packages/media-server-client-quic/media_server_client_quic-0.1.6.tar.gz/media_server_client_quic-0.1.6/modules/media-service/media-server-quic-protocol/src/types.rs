use crate::common::AudioFrame;
use flume::{bounded, Receiver, Sender};
use protobuf_types::media_streaming::H264Message;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
// Channel sizes (in number of frames)
const VIDEO_CHANNEL_SIZE: usize = 4; // Only keep last ~133ms of video (at 30fps)
const AUDIO_CHANNEL_SIZE: usize = 8; // Only keep last ~160ms of audio (at 50Hz)

pub struct VideoChannel {
    pub tx: Sender<H264Message>,
    pub rx: Receiver<H264Message>,
}

impl VideoChannel {
    pub fn new() -> Self {
        let (tx, rx) = bounded(VIDEO_CHANNEL_SIZE);
        Self { tx, rx }
    }

    pub fn clone_sender(&self) -> Sender<H264Message> {
        self.tx.clone()
    }

    pub fn subscribe(&self) -> Receiver<H264Message> {
        self.rx.clone()
    }
}

impl Default for VideoChannel {
    fn default() -> Self {
        Self::new()
    }
}

pub struct AudioChannel {
    pub tx: Sender<AudioFrame>,
    pub rx: Receiver<AudioFrame>,
}

impl AudioChannel {
    pub fn new() -> Self {
        let (tx, rx) = bounded(AUDIO_CHANNEL_SIZE);
        Self { tx, rx }
    }

    pub fn clone_sender(&self) -> Sender<AudioFrame> {
        self.tx.clone()
    }

    pub fn subscribe(&self) -> Receiver<AudioFrame> {
        self.rx.clone()
    }
}

impl Default for AudioChannel {
    fn default() -> Self {
        Self::new()
    }
}

pub struct SourceState {
    frame_count: AtomicU64,
    running: AtomicBool,
    connected: AtomicBool,
}

impl SourceState {
    pub fn new() -> Self {
        Self {
            frame_count: AtomicU64::new(0),
            running: AtomicBool::new(false),
            connected: AtomicBool::new(false),
        }
    }

    pub fn increment_frame_count(&self) -> u64 {
        self.frame_count.fetch_add(1, Ordering::SeqCst)
    }

    pub fn get_frame_count(&self) -> u64 {
        self.frame_count.load(Ordering::SeqCst)
    }

    pub fn set_running(&self, running: bool) {
        self.running.store(running, Ordering::SeqCst)
    }

    pub fn is_running(&self) -> bool {
        self.running.load(Ordering::SeqCst)
    }

    pub fn set_connected(&self, connected: bool) {
        self.connected.store(connected, Ordering::SeqCst)
    }

    pub fn is_connected(&self) -> bool {
        self.connected.load(Ordering::SeqCst)
    }
}

impl Default for SourceState {
    fn default() -> Self {
        Self::new()
    }
}
