

from deepeval.models import DeepEvalBaseLLM
from ollama import Client
from ollama import ChatResponse
from deepeval import evaluate



class customLM(DeepEvalBaseLLM):
    def __init__(self, url="http://localhost:11434",model="llama3:8b"):
        self.model = Client(host=url)
        self.model_name = model

    def load_model(self, *args, **kwargs) -> Client:
        return self.model
    
    def generate(self, prompt: str) -> str:
        client = self.load_model()
        completion:ChatResponse = client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Your helpful AI for Evaluation"},
                {"role": "user", "content": prompt}
            ],
            # format="json"
        )
        return completion['message']["content"]
    
    async def a_generate(self, prompt: str) -> str:
        # Use asyncio.to_thread to run the blocking generate method in a separate thread
        return self.generate(prompt=prompt)

    def get_model_name(self):
        return self.model_name

from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase
# from bayesrag.llmEvaluator import customLM

def deepEvalutor(user_query: str,generated_response:str,context: list[str]):
        # Evaluate the output using Contextual Relevancy Metric
    metric = ContextualRelevancyMetric(
        threshold=0.7,
        model=customLM(),
        include_reason=True
    )
    
    test_case = LLMTestCase(
        input=user_query,
        actual_output=generated_response,
        retrieval_context=context 
    )
    evaluation = metric.measure(test_case)
    
    result=evaluate([test_case], [metric])
    score,reason=result.test_results[0].metrics_data[0].score,result.test_results[0].metrics_data[0].reason

    evaluation_results = {
        "score": score,
        "reason": reason
    }

    return evaluation_results


if __name__=="__main__": 
    
    c = customLM()
    print(c.generate("Hey"))
    
    