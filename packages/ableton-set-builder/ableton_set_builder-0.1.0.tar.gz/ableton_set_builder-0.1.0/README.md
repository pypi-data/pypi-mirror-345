# AbletonSetBuilder - Build Ableton sets using Python
This package helps building Ableton Live sets.

To start with this package, initialize the class with an existing Ableton Live set, to be used as a template:
```python
from ableton_set_builder import AbletonSetBuilder, ColorsDir

builder = AbletonSetBuilder('path/to/template.als') # parses both compressed and uncompressed .als sets
```

The following functions are available:
```python
builder.create_audio_track("Track Name", "salmon")
builder.add_scene("101", "scene 101")

xml = builder.to_xml() # compile set to XML
builder.build_als('path/to/output') # compile set to compressed ALS
```
