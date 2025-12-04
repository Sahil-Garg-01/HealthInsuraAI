# Health Insurance Claim Processing System

An AI-powered **ReAct agent** for automated health insurance claim adjudication.

## ReAct Pattern

The agent follows the **Think → Act → Observe** loop:

```
┌─────────────────────────────────────────────────────────┐
│                      START                               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   THINK NODE                             │
│  • Analyze current state                                 │
│  • Reason about next action                              │
│  • Output: thought, action, action_input                 │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    ACT NODE                              │
│  • Execute chosen action (ingest/preprocess/extract/     │
│    analyze/decide/output/finish)                         │
│  • Call appropriate processor                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  OBSERVE NODE                            │
│  • Process action result                                 │
│  • Update state with observation                         │
│  • Check completion condition                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
                 ┌────────────┐
                 │ Complete?  │───Yes──▶ END
                 └─────┬──────┘
                       │No
                       │
                       └──────────────▶ THINK (loop)
```

## Architecture

```
healthinsuranceclaim/
├── main.py                     # Entry point
├── config/
│   └── settings.py             # Centralized configuration
└── src/
    ├── types.py                # Shared type definitions
    ├── agent/
    │   └── react_agent.py      # ReAct agent (think/act/observe nodes)
    ├── processors/
    │   ├── ingestion.py        # File intake
    │   ├── preprocessing.py    # Document prep (stamps, signatures)
    │   ├── extraction.py       # OCR, tables, translation
    │   ├── intelligence.py     # NER, classification, structuring
    │   ├── decision.py         # LLM-based decision
    │   └── output.py           # Report generation
    └── utils/
        └── http_client.py      # HTTP utilities
```

## Available Actions

| Action | Description |
|--------|-------------|
| `ingest` | Ingest uploaded files |
| `preprocess` | Split docs, detect stamps/signatures |
| `extract` | OCR text, extract tables, translate |
| `analyze` | NER, classify, structure claim JSON |
| `decide` | Make approve/query/reject decision |
| `output` | Generate reports, store to DB |
| `finish` | Complete processing |

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

## Usage

```bash
python main.py
```