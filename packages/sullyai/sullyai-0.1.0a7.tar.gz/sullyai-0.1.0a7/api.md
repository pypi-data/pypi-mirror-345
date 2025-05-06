# Shared Types

```python
from sullyai.types import HeadingSection, Section
```

# Notes

Types:

```python
from sullyai.types import DeleteResponse, NoteCreateResponse, NoteRetrieveResponse
```

Methods:

- <code title="post /v1/notes">client.notes.<a href="./src/sullyai/resources/notes.py">create</a>(\*\*<a href="src/sullyai/types/note_create_params.py">params</a>) -> <a href="./src/sullyai/types/note_create_response.py">NoteCreateResponse</a></code>
- <code title="get /v1/notes/{noteId}">client.notes.<a href="./src/sullyai/resources/notes.py">retrieve</a>(note_id) -> <a href="./src/sullyai/types/note_retrieve_response.py">NoteRetrieveResponse</a></code>
- <code title="delete /v1/notes/{noteId}">client.notes.<a href="./src/sullyai/resources/notes.py">delete</a>(note_id) -> <a href="./src/sullyai/types/delete_response.py">DeleteResponse</a></code>

# NoteStyles

Types:

```python
from sullyai.types import NoteStyleCreateResponse
```

Methods:

- <code title="post /v1/note-styles">client.note_styles.<a href="./src/sullyai/resources/note_styles.py">create</a>(\*\*<a href="src/sullyai/types/note_style_create_params.py">params</a>) -> <a href="./src/sullyai/types/note_style_create_response.py">NoteStyleCreateResponse</a></code>

# Audio

## Transcriptions

Types:

```python
from sullyai.types.audio import TranscriptionCreateResponse, TranscriptionRetrieveResponse
```

Methods:

- <code title="post /v1/audio/transcriptions">client.audio.transcriptions.<a href="./src/sullyai/resources/audio/transcriptions/transcriptions.py">create</a>(\*\*<a href="src/sullyai/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/sullyai/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>
- <code title="get /v1/audio/transcriptions/{transcriptionId}">client.audio.transcriptions.<a href="./src/sullyai/resources/audio/transcriptions/transcriptions.py">retrieve</a>(transcription_id) -> <a href="./src/sullyai/types/audio/transcription_retrieve_response.py">TranscriptionRetrieveResponse</a></code>
- <code title="delete /v1/audio/transcriptions/{transcriptionId}">client.audio.transcriptions.<a href="./src/sullyai/resources/audio/transcriptions/transcriptions.py">delete</a>(transcription_id) -> <a href="./src/sullyai/types/delete_response.py">DeleteResponse</a></code>

### Stream

Types:

```python
from sullyai.types.audio.transcriptions import StreamCreateTokenResponse
```

Methods:

- <code title="post /v1/audio/transcriptions/stream/token">client.audio.transcriptions.stream.<a href="./src/sullyai/resources/audio/transcriptions/stream.py">create_token</a>(\*\*<a href="src/sullyai/types/audio/transcriptions/stream_create_token_params.py">params</a>) -> <a href="./src/sullyai/types/audio/transcriptions/stream_create_token_response.py">StreamCreateTokenResponse</a></code>
