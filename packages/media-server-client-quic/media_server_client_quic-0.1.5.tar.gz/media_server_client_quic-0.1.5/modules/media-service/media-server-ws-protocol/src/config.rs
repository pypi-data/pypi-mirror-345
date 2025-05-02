use std::time::Duration;

// WebSocket configuration constants
pub const CONNECTION_TIMEOUT: Duration = Duration::from_secs(10);
pub const PING_INTERVAL: Duration = Duration::from_secs(1);
pub const MAX_MESSAGE_SIZE: usize = 8 * 1024 * 1024; // Reduced to 8MB
