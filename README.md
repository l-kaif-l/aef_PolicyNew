# 🌾 NF Transcript Toolkit

A Streamlit application for qualitative research analysis that extracts insights from transcripts and performs thematic coding using Azure OpenAI.

## Features

### 🧠 Insights Extraction
- Automatically extract key insights from interview transcripts
- Generate concise bullet points highlighting perceptions, experiences, barriers, and enablers
- Extract relevant verbatim quotes from the text
- Process multiple files simultaneously
- Persistent results across sessions

### 🏷️ Codebook Coding (KII)
- Thematic coding based on predefined taxonomy
- Segments transcripts intelligently for better analysis
- Classifies content into themes and subcodes
- Extracts insights and supporting quotes for each segment
- Customizable segment size for analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- Azure OpenAI API access
- Streamlit account (for deployment)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nf-transcript-toolkit.git
cd nf-transcript-toolkit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Azure OpenAI credentials in Streamlit secrets:

Create a `.streamlit/secrets.toml` file:
```toml
AZURE_OPENAI_API_KEY = "your-api-key-here"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-10-21"
DEPLOYMENT = "gpt-4o"
```

## Usage

### Running Locally

```bash
streamlit run app.py
```

### Insights Extraction

1. Navigate to the **Insights Extraction** tab
2. Upload one or more transcript files (.docx or .txt)
3. Click **Generate Insights**
4. Review the extracted insights and quotes
5. Download reports as needed

### Codebook Coding

1. Navigate to the **Codebook Coding (KII)** tab
2. Adjust the segment size slider (800-3000 characters)
3. Upload transcript files
4. Click **Run Coding**
5. Review the thematic coding results
6. Download coded reports

## Taxonomy Structure

The KII coding uses a predefined taxonomy covering:

- **Respondent Background (BCK)**: Role, Experience
- **Introduction and Spread of NF (SPR)**: Introduction channels, Response, Early adopters
- **Adoption Patterns (ADO)**: Numbers, Types, Dropout reasons
- **NF Practices and Inputs (PRC)**: Biological inputs, Input access, Crop types
- **Challenges and Barriers (CHL)**: Labor, Yield, Market, Social, Health/Food changes
- **Support Systems (SUP)**: CSA support, Government support, Suggestions
- **Benefits of NF (BEN)**: Cost reduction, Soil health, Human health, Income stability
- **Ecosystem and Policy (ECO)**: Market policy, Ecosystem changes, Institutional links
- **Future Direction and Continuity (FUT)**: Exposure visits, Training needs, Infrastructure

## File Support

- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

## Features

- **Chunking**: Intelligent text segmentation with overlap for context preservation
- **Deduplication**: Automatic removal of duplicate insights and quotes
- **Retry Logic**: Built-in retry mechanism for API calls with exponential backoff
- **Session Persistence**: Results are saved in session state and persist across tab switches
- **Progress Tracking**: Real-time progress indicators during processing

## Dependencies

```
streamlit
python-docx
openai
tenacity
```

## Configuration

### Azure OpenAI Settings

The application requires the following secrets (configured in Streamlit):

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-10-21)
- `DEPLOYMENT`: Model deployment name (default: gpt-4o)

### Processing Parameters

**Insights Extraction:**
- Chunk size: 6000 characters
- Chunk overlap: 400 characters
- Target insights: 10-20 per file
- Target quotes: 5-12 per file

**Codebook Coding:**
- Segment size: Adjustable (800-3000 characters)
- One theme per segment
- Multiple subcodes allowed per theme

## Output Format

### Insights Report
```
INSIGHTS REPORT — filename.docx

INSIGHTS (Top 10–20):
- Insight 1
- Insight 2
...

QUOTES (5–12 strongest):
- "Quote 1"
- "Quote 2"
...
```

### Coded Report
```
=== KII CODED REPORT — filename.docx ===

[Segment 1]
Theme: Theme Name
Subcodes: Subcode1, Subcode2
Insight: Brief insight statement
Quote: "Verbatim quote from text"

[Segment 2]
...
```

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Add secrets in the Streamlit Cloud dashboard
4. Deploy the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Built with Azure OpenAI and Streamlit for qualitative research analysis in agricultural and development contexts.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.
