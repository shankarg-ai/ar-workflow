import asyncio
import json
import os
from adk.workflows import Parallel, Sequential
from adk.agent_runtime import AgentRuntime # Corrected import

from agents import (
    action_items_agent,
    validate_action_items_agent,
    collection_recommendations_agent,
    validate_collection_recommendations_agent,
    risk_assessment_agent,
    validate_risk_assessment_agent,
    payment_prediction_agent,
    validate_payment_prediction_agent,
    optimization_strategies_agent,
    validate_optimization_strategies_agent,
    raw_data_store_agent,
    consolidate_response_agent,
    validate_consolidated_agent,
    format_response_agent,
    output_agent
)

# Define the parallel execution block
parallel_workflow = Parallel(
    name="ParallelProcessing",
    description="Executes core logic and validation for different domains in parallel.",
    branches=[
        Sequential(
            name="ActionItemsBranch",
            description="Processes and validates action items.",
            agents=[
                action_items_agent,
                validate_action_items_agent
            ]
        ),
        Sequential(
            name="CollectionRecommendationsBranch",
            description="Processes and validates collection recommendations.",
            agents=[
                collection_recommendations_agent,
                validate_collection_recommendations_agent
            ]
        ),
        Sequential(
            name="RiskAssessmentBranch",
            description="Processes and validates risk assessment.",
            agents=[
                risk_assessment_agent,
                validate_risk_assessment_agent
            ]
        ),
        Sequential(
            name="PaymentPredictionBranch",
            description="Processes and validates payment predictions.",
            agents=[
                payment_prediction_agent,
                validate_payment_prediction_agent
            ]
        ),
        Sequential(
            name="OptimizationStrategiesBranch",
            description="Processes and validates optimization strategies.",
            agents=[
                optimization_strategies_agent,
                validate_optimization_strategies_agent
            ]
        ),
    ]
)

# Define the main sequential workflow with raw data store
main_workflow = Sequential(
    name="MainWorkflow",
    description="Orchestrates the entire AP AR workflow with raw data preservation.",
    agents=[
        # First store the raw data for later reference
        raw_data_store_agent,
        # Then process through parallel workflow
        parallel_workflow,
        # Consolidate the results from parallel processing
        consolidate_response_agent,
        # Validate with access to both consolidated response and original data
        # (raw_data_store_agent is already a sub-agent of validate_consolidated_agent)
        validate_consolidated_agent,
        # Format the validated response
        format_response_agent,
        # Handle final output
        output_agent,
    ]
)

async def run_workflow(input_data_path: str):
    """Loads input data and runs the main ADK workflow."""
    try:
        with open(input_data_path, 'r') as f:
            raw_graph_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_data_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_data_path}")
        return

    runtime = AgentRuntime()
    print("Starting ADK workflow...")
    
    # The input to the first agent in the main_workflow will be raw_graph_data
    # ADK LlmAgent expects inputs as a dictionary.
    # The 'run' method of the first agent in 'parallel_workflow' will receive this.
    # We need to ensure the LlmAgents are designed to pick up 'raw_graph_data' or a specific key from it.
    # For now, let's assume the first agents in each parallel branch can handle the entire raw_graph_data.
    initial_inputs = {"raw_data": raw_graph_data} 

    try:
        result = await runtime.run_agent(agent=main_workflow, inputs=initial_inputs)
        print("Workflow completed.")
        print("Final Result:", result)
        
        # You might want to save the final formatted output to a file
        if result and 'formatted_response' in result:
            output_file_path = os.path.join(os.path.dirname(input_data_path), 'workflow_output.json')
            with open(output_file_path, 'w') as outfile:
                json.dump(result['formatted_response'], outfile, indent=4)
            print(f"Formatted output saved to {output_file_path}")
        elif result and 'final_output_status' in result:
             print(f"Output agent status: {result['final_output_status']}")
        else:
            print("No specific 'formatted_response' or 'final_output_status' key in result.")

    except Exception as e:
        print(f"An error occurred during workflow execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Path to the input JSON file (output from the math model)
    input_json_path = os.path.join('output', 'ar_results.json')
    
    # Ensure the script is run from the root of 'AP AR Workflow development' directory
    # or adjust path accordingly.
    current_dir = os.getcwd()
    if not current_dir.endswith('AP AR Workflow development'):
        print(f"Warning: Script is being run from {current_dir}.")
        print("Please ensure 'output/ar_results.json' and 'templates' directory are accessible.")
        # Potentially adjust input_json_path if needed, e.g. by joining with a base path

    asyncio.run(run_workflow(input_json_path))
