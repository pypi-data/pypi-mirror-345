# Video Editor Component for Streamlit

A Streamlit custom component to display a simple video editor interface.


## Installation

First install Streamlit (of course!) then pip-install this library:

```bash
pip install streamlit
pip install streamlit-video-editor
```


## Example

```python
# Streamlit Video Editor Component Example

import streamlit as st
from streamlit_video_editor import video_editor

# use full page width
st.set_page_config(page_title="Video Editor Example", layout="wide")

# load video file
video_file = st.file_uploader("Upload a video", type=["mp4", "mov"])

if video_file:
    # display video editor
    editor_response = video_editor(video_file.path)
    st.write("Editor output:", editor_response)
```


![Component Example](https://github.com/antunsz/streamlit-video-editor/raw/main/component-example.png)


## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/antunsz/streamlit-video-editor).

## Author

Carlos André Antunes ([@antunsz](https://github.com/antunsz))
