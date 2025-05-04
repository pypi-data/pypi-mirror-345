use anyhow::Result;
use media_server_ws_protocol::StreamStats;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;
use tracing::info;

pub async fn monitor_stats(stats: Arc<Mutex<StreamStats>>, client_id: u64) -> Result<()> {
    let mut interval = tokio::time::interval(Duration::from_secs(5));

    loop {
        interval.tick().await;
        let stats = stats.lock().await;
        info!("Client {} stats:\n{}", client_id, stats.get_stats());
    }
}
