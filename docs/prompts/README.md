# LLM Command Prompts

This directory contains the prompts used by the `refine` and `format-meeting` commands of metalscribe.

## Global Language Architecture

Language is a **global parameter** that flows through the entire pipeline:

1. **Transcription**: Set via `--lang pt` in the `run` command
2. **Mapping**: `pt` → `pt-BR` (Whisper code → BCP 47 code)
3. **Metadata**: Saved as `prompt_language: pt-BR` in the markdown file
4. **LLM**: `refine` and `format-meeting` commands automatically read from the file

```
Whisper Code      →    Prompt Code
pt                →    pt-BR (Brazilian Portuguese)
en                →    en-US (American English)
es                →    es-ES (Spanish)
```

## Language Structure

Prompts are organized by language code (BCP 47):

```
prompts/
├── README.md           # This file
├── pt-BR/              # Brazilian Portuguese (current default)
│   ├── refine.md
│   └── format-meeting.md
├── en-US/              # American English (to be implemented)
│   ├── refine.md
│   └── format-meeting.md
└── es-ES/              # Spanish (to be implemented)
    ├── refine.md
    └── format-meeting.md
```

## Default Language

The default language is `pt` (Portuguese), which maps to `pt-BR`. It can be changed via:

1. **CLI Flag**: `metalscribe run -i audio.mp3 --lang en`
2. **Environment Variable**: `METALSCRIBE_DEFAULT_LANGUAGE=en`

## Adding a New Language

1. Create a new folder with the BCP 47 code (e.g., `en-US/`)
2. Copy the files from `pt-BR/` as a base
3. Translate while maintaining the markdown structure
4. Add the mapping in `src/metalscribe/config.py`:
   ```python
   LANGUAGE_MAPPING = {
       "pt": "pt-BR",
       "en": "en-US",  # Add here
   }
   SUPPORTED_PROMPT_LANGUAGES = ["pt-BR", "en-US"]  # Add here
   ```
5. Test with: `metalscribe run -i audio.mp3 --lang en`

### Translation Guidelines

- **Preserve markdown structure** (sections, examples, formatting)
- **Adapt examples** to the target language context
- **Keep technical terms** in English when appropriate
- **Test with real transcriptions** in the target language

## Available Prompts

### refine.md

Prompt for correcting ASR (Automatic Speech Recognition) errors:
- Corrects swapped homophones
- Restores punctuation
- Removes common hallucinations
- Preserves the speaker's informal style

### format-meeting.md

Prompt for formatting meeting transcriptions:
- Generates executive summary
- Identifies participants
- Extracts discussed topics
- Lists action items
- Organizes full transcription

## Supported Languages

| Whisper | Prompt | Language | Status |
|---------|--------|--------|--------|
| `pt` | `pt-BR` | Brazilian Portuguese | ✅ Available |
| `en` | `en-US` | American English | 🚧 Planned |
| `es` | `es-ES` | Spanish | 🚧 Planned |

---

**Note**: Current prompts are optimized for Brazilian Portuguese. Contributions for other languages are welcome!
