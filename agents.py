from adk.llm import LlmAgent
from adk import Agent
from jinja2 import Environment, FileSystemLoader
import os

# Setup Jinja2 environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# --- Core Logic Agents ---
def create_llm_agent(name: str, description: str, template_name: str, output_key: str):
    instruction_template = jinja_env.get_template(template_name)
    instruction = instruction_template.render() # Pass actual data here if needed at render time
    return LlmAgent(
        name=name,
        model="gemini-1.5-pro-preview-0514", # Using the specified model
        description=description,
        instructions=instruction, # Changed from 'instruction' to 'instructions'
        tools=[],
        output_key=output_key
    )

# Action Items
action_items_agent = create_llm_agent(
    name="ActionItemsAgent",
    description="Processes raw data to identify and extract action items.",
    template_name="action_items.j2",
    output_key="action_items"
)
validate_action_items_agent = create_llm_agent(
    name="ValidateActionItemsAgent",
    description="Validates the extracted action items based on schema and business rules.",
    template_name="validate_action_items.j2",
    output_key="validated_action_items"
)

# Collection Recommendations
collection_recommendations_agent = create_llm_agent(
    name="CollectionRecommendationsAgent",
    description="Generates collection recommendations from the input data.",
    template_name="collection_recommendations.j2",
    output_key="collection_recommendations"
)
validate_collection_recommendations_agent = create_llm_agent(
    name="ValidateCollectionRecommendationsAgent",
    description="Validates the generated collection recommendations.",
    template_name="validate_collection_recommendations.j2",
    output_key="validated_collection_recommendations"
)

# Risk Assessment
risk_assessment_agent = create_llm_agent(
    name="RiskAssessmentAgent",
    description="Performs risk assessment based on the input data.",
    template_name="risk_assessment.j2",
    output_key="risk_assessment"
)
validate_risk_assessment_agent = create_llm_agent(
    name="ValidateRiskAssessmentAgent",
    description="Validates the risk assessment results.",
    template_name="validate_risk_assessment.j2",
    output_key="validated_risk_assessment"
)

# Payment Prediction
payment_prediction_agent = create_llm_agent(
    name="PaymentPredictionAgent",
    description="Predicts payment likelihood or timing.",
    template_name="payment_prediction.j2",
    output_key="payment_prediction"
)
validate_payment_prediction_agent = create_llm_agent(
    name="ValidatePaymentPredictionAgent",
    description="Validates the payment predictions.",
    template_name="validate_payment_prediction.j2",
    output_key="validated_payment_prediction"
)

# Optimization Strategies
optimization_strategies_agent = create_llm_agent(
    name="OptimizationStrategiesAgent",
    description="Develops optimization strategies based on the input.",
    template_name="optimization_strategies.j2",
    output_key="optimization_strategies"
)
validate_optimization_strategies_agent = create_llm_agent(
    name="ValidateOptimizationStrategiesAgent",
    description="Validates the optimization strategies.",
    template_name="validate_optimization_strategies.j2",
    output_key="validated_optimization_strategies"
)

# --- Raw Data Store Agent ---
raw_data_store_agent = create_llm_agent(
    name="RawDataStoreAgent",
    description="Stores the original math model output data for reference throughout the workflow.",
    template_name="raw_data_store.j2",
    output_key="stored_raw_data"
)

# --- Consolidation and Formatting Agents ---
consolidate_response_agent = create_llm_agent(
    name="ConsolidateResponseAgent",
    description="Merges results from parallel validation steps into a single consolidated response.",
    template_name="consolidate_response.j2",
    output_key="consolidated_response"
)

# Create validation agent with raw data store as a sub-agent
validate_consolidated_agent = create_llm_agent(
    name="ValidateConsolidatedAgent",
    description="Performs final consistency and business rule checks on the consolidated response with reference to original data.",
    template_name="validate_consolidated_response.j2",
    sub_agents=[raw_data_store_agent],  # Use raw_data_store_agent as a sub-agent
    output_key="final_validated_response"
)

format_response_agent = create_llm_agent(
    name="FormatResponseAgent",
    description="Formats the final validated response into the desired output format (e.g., JSON, XML).",
    template_name="format_response.j2",
    output_key="formatted_response"
)

output_agent = create_llm_agent(
    name="OutputAgent",
    description="Handles the final output, e.g., sending to an API, message bus, or saving to a file.",
    template_name="output_agent.j2",
    output_key="final_output_status"
)
