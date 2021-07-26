mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
[theme]\n\
base="dark"\n\
backgroundColor="#191a1a"\n\
secondaryBackgroundColor="#2c2b2b"\n\
\n\

" > ~/.streamlit/config.toml