use crate::common::AudioFrame;
use crate::common::StreamType;
use crate::current_timestamp_micros;
use crate::packet::MediaPacket as NativeMediaPacket;
use crate::ControlPacket;
use anyhow::{anyhow, Result};
use prost::Message;
use protobuf_types::media_streaming::{
    data_message, AudioMessage, AuthMessage, AuthResponse, DataMessage, HelloMessage, InitMessage,
    MessageType, PingMessage, PongMessage,
};
use tracing::debug;

impl From<NativeMediaPacket> for DataMessage {
    fn from(packet: NativeMediaPacket) -> Self {
        let (msg_type, timestamp, payload) = match packet {
            NativeMediaPacket::Video(h264) => (
                MessageType::H264,
                h264.timestamp,
                data_message::Payload::H264(h264),
            ),
            NativeMediaPacket::Audio(audio) => (
                MessageType::Audio,
                audio.timestamp,
                data_message::Payload::Audio(AudioMessage {
                    data: audio.data.to_vec(),
                    timestamp: audio.timestamp,
                    metadata: Default::default(),
                }),
            ),
            NativeMediaPacket::Control(ctrl) => {
                let now = current_timestamp_micros();
                match ctrl {
                    ControlPacket::Hello {
                        version,
                        nonce,
                        capabilities,
                        client_id,
                    } => (
                        MessageType::Hello,
                        now,
                        data_message::Payload::Hello(HelloMessage {
                            version,
                            nonce,
                            capabilities,
                            client_id: client_id.map(|id| id.to_string()),
                        }),
                    ),
                    ControlPacket::StartStream { stream_type } => (
                        MessageType::Init,
                        now,
                        data_message::Payload::Init(InitMessage {
                            stream_type: format!("{:?}", stream_type),
                        }),
                    ),
                    ControlPacket::StopStream | ControlPacket::KeepAlive => (
                        MessageType::Unknown,
                        now,
                        data_message::Payload::Hello(HelloMessage::default()),
                    ),
                    ControlPacket::Ping {
                        sequence_number,
                        timestamp,
                    } => (
                        MessageType::Ping,
                        timestamp,
                        data_message::Payload::Ping(PingMessage {
                            sequence_number,
                            timestamp,
                        }),
                    ),
                    ControlPacket::Pong {
                        sequence_number,
                        timestamp,
                        receive_timestamp,
                    } => (
                        MessageType::Pong,
                        timestamp,
                        data_message::Payload::Pong(PongMessage {
                            sequence_number,
                            timestamp,
                            receive_timestamp,
                        }),
                    ),
                    ControlPacket::Auth {
                        auth,
                        serial,
                        sign,
                        stream_id,
                    } => (
                        MessageType::Auth,
                        now,
                        data_message::Payload::Auth(AuthMessage {
                            auth,
                            serial,
                            sign,
                            stream_id,
                        }),
                    ),
                    ControlPacket::AuthResponse { success, message } => (
                        MessageType::AuthResponse,
                        now,
                        data_message::Payload::AuthResponse(AuthResponse { success, message }),
                    ),
                }
            }
        };

        DataMessage {
            r#type: msg_type as i32,
            timestamp,
            payload: Some(payload),
        }
    }
}

impl TryFrom<DataMessage> for NativeMediaPacket {
    type Error = anyhow::Error;

    fn try_from(value: DataMessage) -> Result<Self> {
        debug!("Converting message type: {}", value.r#type);

        let msg_type = MessageType::try_from(value.r#type)
            .map_err(|_| anyhow!("Invalid message type: {}", value.r#type))?;

        let payload = value.payload.ok_or_else(|| anyhow!("Missing payload"))?;

        match msg_type {
            MessageType::H264 => {
                debug!("Converting H264 message");
                if let data_message::Payload::H264(h264) = payload {
                    Ok(NativeMediaPacket::Video(h264))
                } else {
                    Err(anyhow!("Invalid payload type for H264 message"))
                }
            }
            MessageType::Audio => {
                debug!("Converting Audio message");
                if let data_message::Payload::Audio(audio) = payload {
                    Ok(NativeMediaPacket::Audio(AudioFrame {
                        timestamp: audio.timestamp,
                        data: audio.data,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Audio message"))
                }
            }
            MessageType::Init => {
                debug!("Converting Init message");
                if let data_message::Payload::Init(init) = payload {
                    let stream_type = match init.stream_type.as_str() {
                        "Video" => StreamType::Video,
                        "Audio" => StreamType::Audio,
                        "KeepAlive" => StreamType::KeepAlive,
                        _ => StreamType::Video, // Default to video for backward compatibility
                    };
                    Ok(NativeMediaPacket::Control(ControlPacket::StartStream {
                        stream_type,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Init message"))
                }
            }
            MessageType::Ping => {
                debug!("Converting Ping message");
                if let data_message::Payload::Ping(ping) = payload {
                    Ok(NativeMediaPacket::Control(ControlPacket::Ping {
                        sequence_number: ping.sequence_number,
                        timestamp: ping.timestamp,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Ping message"))
                }
            }
            MessageType::Pong => {
                debug!("Converting Pong message");
                if let data_message::Payload::Pong(pong) = payload {
                    Ok(NativeMediaPacket::Control(ControlPacket::Pong {
                        sequence_number: pong.sequence_number,
                        timestamp: pong.timestamp,
                        receive_timestamp: pong.receive_timestamp,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Pong message"))
                }
            }
            MessageType::Hello => {
                debug!("Converting Hello message");
                if let data_message::Payload::Hello(hello) = payload {
                    Ok(NativeMediaPacket::Control(ControlPacket::Hello {
                        version: hello.version,
                        nonce: hello.nonce,
                        capabilities: hello.capabilities,
                        client_id: hello.client_id.and_then(|id| id.parse::<u64>().ok()),
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Hello message"))
                }
            }
            MessageType::Auth => {
                debug!("Converting Auth message");
                if let data_message::Payload::Auth(auth) = payload {
                    Ok(NativeMediaPacket::Control(ControlPacket::Auth {
                        auth: auth.auth,
                        serial: auth.serial,
                        sign: auth.sign,
                        stream_id: auth.stream_id,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for Auth message"))
                }
            }
            MessageType::AuthResponse => {
                debug!("Converting AuthResponse message");
                if let data_message::Payload::AuthResponse(auth_response) = payload {
                    Ok(NativeMediaPacket::Control(ControlPacket::AuthResponse {
                        success: auth_response.success,
                        message: auth_response.message,
                    }))
                } else {
                    Err(anyhow!("Invalid payload type for AuthResponse message"))
                }
            }
            MessageType::Unknown => {
                debug!("Received Unknown/Empty message type, treating as keepalive");
                Ok(NativeMediaPacket::Control(ControlPacket::KeepAlive))
            }
        }
    }
}

pub fn encode_packet(packet: NativeMediaPacket) -> Result<Vec<u8>> {
    let proto_msg = DataMessage::from(packet);
    let len = proto_msg.encoded_len();
    let mut buf = Vec::with_capacity(len);
    proto_msg.encode(&mut buf)?;
    Ok(buf)
}

pub fn encode_packet_into(packet: NativeMediaPacket, buf: &mut Vec<u8>) -> Result<()> {
    let proto_msg = DataMessage::from(packet);
    let len = proto_msg.encoded_len();
    buf.reserve(len);
    proto_msg.encode(buf)?;
    Ok(())
}

pub fn decode_packet(data: &[u8]) -> Result<NativeMediaPacket> {
    debug!("Decoding packet of {} bytes", data.len());
    let proto_msg = DataMessage::decode(data)?;
    debug!("Decoded protobuf message type: {}", proto_msg.r#type);
    NativeMediaPacket::try_from(proto_msg)
}
