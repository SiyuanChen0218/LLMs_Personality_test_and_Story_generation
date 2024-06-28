## File structure
- `main.py`: The main script for story generation and evaluation using ChatGPT.
- `requirements.txt`: The requirements file for the project.
- `output/`: The directory containing the generated results (generated stories and evaluated endings) by ChatGPT.
- `src/`: The directory containing utility files for `main.py`

## Installation and Usage
0. Create a virtual environment (if needed):
```bash
conda create -n chatgpt-biases python=3.11
```
and activate it:
```bash
conda activate chatgpt-biases
```
1. Copy `.env.example` and rename it to `.env`. Follow instructions on [this page](https://platform.openai.com/docs/api-reference/authentication) to obtain your own OpenAI API key and on [this page](https://huggingface.co/docs/hub/security-tokens) for HuggingFace authentication token. You may also need to follow instructions on [this page](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf) to access Llama 2 models.
2. Install the requirements:
```bash
pip install -r requirements.txt
```
3. Change configurations in `src/config.py` as needed.
4. Run the script for story generation and evaluation:
```bash
python main.py
```

