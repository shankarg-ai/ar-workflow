# AP AR Workflow with Google ADK

This project implements the AP AR workflow described in the provided diagram using Google's Agent Development Kit (ADK).
It processes raw data (assumed to be the output of a math model optimization, like `output/ar_results.json`) through a series of agents executed in parallel and sequentially.


![Receivables](https://github.com/shankarg-ai/ar-workflow/blob/main/workflow.png)


## Project Structure

```
d:\Download\AP AR Workflow development/
├── output/
│   ├── ar_results.json  (Input: Output from math model optimization)
│   └── workflow_output.json (Output: Final formatted output of this ADK workflow)
├── templates/             (Jinja2 templates for LLM Agent instructions)
│   ├── action_items.j2
│   ├── validate_action_items.j2
│   ├── ... (other templates for each agent)
├── agents.py              (Definitions of all ADK LlmAgent instances)
├── main.py                (Main script to define and run the ADK workflow)
├── requirements.txt       (Python dependencies)
└── README.md              (This file)
```

## Setup

1.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note:* The ADK library (`google/adk-python`) might need to be installed directly from GitHub if it's not available on PyPI or as part of `google-cloud-aiplatform`. The `requirements.txt` includes a comment about this. You might need:
    ```bash
    pip install git+https://github.com/google/adk-python.git
    ```
    Ensure you have Git installed if you use this method.

3.  **Set up Google Cloud Authentication (if using cloud-based Gemini models):**
    If your `LlmAgent` instances are configured to use Google Cloud-hosted models (like those on Vertex AI), you'll need to authenticate. This typically involves:
    *   Installing the Google Cloud CLI: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
    *   Logging in: `gcloud auth application-default login`
    *   Setting your project: `gcloud config set project YOUR_PROJECT_ID`
    The example uses `gemini-2.5-pro-preview-03-25`. You may need to ensure this model is available to you and your environment is configured for it (e.g., API keys, correct SDK versions).

4.  **Prepare Input Data:**
    Ensure your input file `output/ar_results.json` exists and contains the data in the expected JSON format from your math model.

5.  **Populate Jinja Templates (Crucial Next Step):**
    The `.j2` files in the `templates/` directory are currently EMPTY. You **MUST** populate these with the specific instructions for each `LlmAgent` to perform its task. The quality of your workflow depends heavily on these prompts.
    For example, `templates/action_items.j2` should contain the prompt for the LLM to extract action items from the input data.

## Running the Workflow

Once setup is complete and templates are populated:

```bash
python main.py
```

The script will:
1.  Load data from `output/ar_results.json`.
2.  Execute the defined ADK workflow.
3.  Print the final result to the console.
4.  Save the formatted output (if the `FormatResponseAgent` produces a `formatted_response` key in its output) to `output/workflow_output.json`.

## How it Works

*   **`agents.py`**: Defines each step of your workflow (e.g., `ActionItemsAgent`, `ValidateActionItemsAgent`) as an `LlmAgent`. Each agent is configured with:
    *   A name and description.
    *   The Gemini model to use (`gemini-2.5-pro-preview-03-25`).
    *   Instructions loaded from a corresponding `.j2` template file in the `templates/` directory.
    *   An `output_key` which determines how its result is named in the workflow's state.
*   **`main.py`**: 
    *   Constructs the overall workflow using ADK's `Parallel` and `Sequential` workflow agents, following the logic from your diagram.
    *   The `Parallel` agent runs five branches concurrently: Action Items, Collection Recommendations, Risk Assessment, Payment Prediction, and Optimization Strategies. Each branch is a `Sequential` workflow containing a core logic agent and its validation agent.
    *   After the parallel tasks complete, their outputs are fed into a sequence of agents: `ConsolidateResponseAgent`, `ValidateConsolidatedAgent`, `FormatResponseAgent`, and `OutputAgent`.
    *   The `AgentRuntime().run_agent(...)` method executes the workflow.
*   **`templates/`**: Contains Jinja2 templates. Each LLM agent will use one of these templates to generate its prompt. **You need to write these prompts.**

## Important Notes

*   **ADK Version & Imports:** The ADK library is relatively new and its API might evolve. The imports and class names (`LlmAgent`, `AgentRuntime`, `Sequential`, `Parallel`) are based on common usage patterns. Ensure they match the version of ADK you are using. Specifically, `AgentRuntime` was imported from `adk.agent_runtime` which seems to be a common location.
*   **LLM Model:** The code uses `gemini-2.5-pro-preview-03-25`. Ensure this model ID is correct and accessible in your environment. You might need to adjust it based on availability or your specific Google Cloud setup.
*   **Error Handling & Input/Output Keys:** The current `main.py` has basic error handling and makes assumptions about output keys (e.g., `formatted_response`). You'll likely need to refine this based on the actual outputs of your LLM agents and how you want data to flow between them.
*   **Jinja Template Content:** The success of this workflow entirely depends on the quality of the instructions you provide in the `.j2` template files. These prompts will guide the LLM for each specific task.
