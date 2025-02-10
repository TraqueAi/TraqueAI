# from datasets import Dataset
# from ragas.metrics import context_precision, answer_relevancy
# from ragas import evaluate

# def evaluate_response(user_query, llm_response, context):
#     data_samples = {
#         'question': [user_query],
#         'answer': [llm_response],
#         'contexts': [[context]],
#     }
#     dataset = Dataset.from_dict(data_samples)
#     # if ground_truth:
#     #     data_samples['ground_truth'] = [ground_truth]

#     # metrics = [context_precision] if ground_truth else [answer_relevancy]
#     metrics = [answer_relevancy]
#     score = evaluate(dataset, metrics=metrics)
#     return score.to_pandas()


from deepeval.metrics import ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase
from bayesrag.llmEvaluator import customLM

from deepeval import evaluate

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