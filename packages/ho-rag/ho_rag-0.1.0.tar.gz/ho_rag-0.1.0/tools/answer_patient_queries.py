from server import mcp
from utils.llm_call import make_llm_request

@mcp.tool()
async def answer_doctor_queries(patient_name:str, query:str) -> str:
    """
        Answers a medical query for a specific patient using a Retrieval-Augmented Generation (RAG) system powered by the OpenAI Chat Completions API.

        This function takes in the name of a patient and a natural language query related to that patient. 
        It then interacts with an OpenAI language model integrated with an indexer and data source 
        (commonly known as a Retrieval-Augmented Generation setup). The indexer retrieves relevant 
        context-specific medical data or notes about the patient, which are combined with the query to 
        generate a precise and context-aware response from the LLM.

        Parameters:
        -----------
        patient_name : str
            The name of the patient for whom the query is being made. This is used to identify and retrieve 
            relevant patient-specific information from the external data source.
        
        query : str
            A natural language question or statement about the patient. This could involve medical history, 
            treatment details, medications, lab reports, or any other patient-related information.

        Returns:
        --------
        str
            The AI-generated response to the query, informed by both the retrieved patient-specific data 
            and the language model's reasoning.

        Example:
        --------
        >>> answer_doctor_queries("John Doe", "What were the symptoms of John Doe?")
        'John Doe has back pain.'
    """
    return await make_llm_request(patient_name, query)