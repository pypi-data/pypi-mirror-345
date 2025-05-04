use std::sync::Arc;
use tokio::sync::broadcast;
use tokio::sync::Mutex;
use tracing::debug;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ConnectionState {
    Disconnected,
    Connecting,
    Connected,
    Authenticated,
    Streaming,
    Error,
    ShuttingDown,
}

impl Default for ConnectionState {
    fn default() -> Self {
        Self::Disconnected
    }
}

pub struct ConnectionStateTracker {
    state: Arc<Mutex<ConnectionState>>,
    error: Arc<Mutex<Option<String>>>,
    shutdown: broadcast::Sender<()>,
}

impl ConnectionStateTracker {
    pub fn new() -> Self {
        let (shutdown, _) = broadcast::channel(1);
        Self {
            state: Arc::new(Mutex::new(ConnectionState::Disconnected)),
            error: Arc::new(Mutex::new(None)),
            shutdown,
        }
    }

    pub async fn set_state(&self, new_state: ConnectionState) {
        let mut state = self.state.lock().await;
        let old_state = *state;
        *state = new_state;
        drop(state);

        debug!(
            "Connection state changed: {:?} -> {:?}",
            old_state, new_state
        );
    }

    pub async fn get_state(&self) -> ConnectionState {
        *self.state.lock().await
    }

    pub async fn set_error(&self, error: String) {
        let mut error_state = self.error.lock().await;
        *error_state = Some(error);
        self.set_state(ConnectionState::Error).await;
    }

    pub async fn get_error(&self) -> Option<String> {
        self.error.lock().await.clone()
    }

    pub fn shutdown_sender(&self) -> broadcast::Sender<()> {
        self.shutdown.clone()
    }

    pub fn subscribe_shutdown(&self) -> broadcast::Receiver<()> {
        self.shutdown.subscribe()
    }

    pub async fn shutdown(&self) {
        self.set_state(ConnectionState::ShuttingDown).await;
        let _ = self.shutdown.send(());
    }
}

impl Clone for ConnectionStateTracker {
    fn clone(&self) -> Self {
        Self {
            state: self.state.clone(),
            error: self.error.clone(),
            shutdown: self.shutdown.clone(),
        }
    }
}
