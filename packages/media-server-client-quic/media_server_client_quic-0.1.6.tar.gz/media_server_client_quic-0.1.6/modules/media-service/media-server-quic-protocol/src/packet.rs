use anyhow::Result;
use protobuf_types::media_streaming::H264Message;

use serde::{Deserialize, Serialize};

use crate::common::AudioFrame;
pub const PROTOCOL_VERSION: u32 = 1;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capabilities {
    pub video_codecs: Vec<String>,
    pub audio_codecs: Vec<String>,
}

impl Default for Capabilities {
    fn default() -> Self {
        Self {
            video_codecs: vec!["h264".to_string()],
            audio_codecs: vec!["opus".to_string()],
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HelloMessage {
    pub version: u32,
    pub capabilities: Capabilities,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub nonce: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub client_id: Option<u64>,
}

impl HelloMessage {
    pub fn new_client() -> Self {
        Self {
            version: PROTOCOL_VERSION,
            capabilities: Capabilities::default(),
            nonce: None,
            client_id: None,
        }
    }

    pub fn new_server(nonce: String, client_id: u64) -> Self {
        Self {
            version: PROTOCOL_VERSION,
            capabilities: Capabilities::default(),
            nonce: Some(nonce),
            client_id: Some(client_id),
        }
    }

    pub fn verify_version(&self) -> bool {
        self.version == PROTOCOL_VERSION
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProtocolMessage {
    Hello(HelloMessage),
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum ControlPacket {
    StartStream {
        stream_type: crate::common::StreamType,
    },
    StopStream,
    Ping {
        sequence_number: u64,
        timestamp: u64,
    },
    Pong {
        sequence_number: u64,
        timestamp: u64,
        receive_timestamp: u64,
    },
    KeepAlive,
    Hello {
        version: u32,
        nonce: Option<String>,
        capabilities: Vec<String>,
        client_id: Option<u64>,
    },
    Auth {
        auth: String,
        serial: String,
        sign: Vec<u8>,
        stream_id: u64,
    },
    AuthResponse {
        success: bool,
        message: Option<String>,
    },
}

#[derive(Debug, Clone)]
pub enum MediaPacket {
    Video(H264Message),
    Audio(AudioFrame),
    Control(ControlPacket),
}

impl MediaPacket {
    // Owned conversion - consumes self
    pub fn into_bytes(self) -> Result<Vec<u8>> {
        super::proto_conversion::pb::encode_packet(self)
    }

    // Reference-based conversion - borrows self
    pub fn to_bytes(&self) -> Result<Vec<u8>> {
        super::proto_conversion::pb::encode_packet(self.clone())
    }

    // Owned conversion with existing buffer - consumes self
    pub fn into_bytes_into(self, buf: &mut Vec<u8>) -> Result<()> {
        super::proto_conversion::pb::encode_packet_into(self, buf)
    }

    // Reference-based conversion with existing buffer - borrows self
    pub fn to_bytes_into(&self, buf: &mut Vec<u8>) -> Result<()> {
        super::proto_conversion::pb::encode_packet_into(self.clone(), buf)
    }

    pub fn from_bytes(data: &[u8]) -> Result<Self> {
        super::proto_conversion::pb::decode_packet(data)
    }
}
