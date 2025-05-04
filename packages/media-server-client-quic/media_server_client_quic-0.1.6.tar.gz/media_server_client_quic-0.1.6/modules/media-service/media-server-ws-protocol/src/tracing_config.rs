// A helper module to initialize tracing with EnvFilter
use tracing_subscriber::EnvFilter;

pub fn init_tracing() {
    let env_filter =
        EnvFilter::new("info,sqlx=warn,hyper=warn,reqwest=warn,tower=warn,h2=warn,rustls=warn");

    let subscriber = tracing_subscriber::fmt()
        .with_env_filter(env_filter)
        .with_file(true)
        .with_line_number(true)
        .with_thread_ids(true)
        .with_target(true)
        .finish();

    // Try to set the global subscriber but don't panic if it fails
    let _ = tracing::subscriber::set_global_default(subscriber);
}
