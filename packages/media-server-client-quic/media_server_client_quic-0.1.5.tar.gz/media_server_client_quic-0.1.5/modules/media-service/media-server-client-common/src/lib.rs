pub type StreamId = u64;

#[derive(Debug)]
pub struct H264Message {
    pub data: Vec<u8>,
    pub timestamp: u64,
    pub frame_type: u32, // 0: Unknown, 1: I-Frame, 2: P-Frame, 3: B-Frame
    pub metadata: std::collections::HashMap<String, String>,
    pub width: Option<u32>,
    pub height: Option<u32>,
}
