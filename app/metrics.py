"""
LLM evaluation metrics module.

Provides core evaluation metrics for assessing LLM response quality.
Uses RAGAS when available, with fallback implementations for basic scenarios.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    name: str
    value: float
    success: bool
    error: Optional[str] = None


class MetricsEvaluator:
    """
    Evaluates LLM responses against golden dataset using various metrics.
    """
    
    def __init__(self, use_ragas: bool = True, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the metrics evaluator.
        
        Args:
            use_ragas: Whether to try using RAGAS library if available
            model_name: Model name to use for evaluation
        """
        self.use_ragas = use_ragas
        self.model_name = model_name
        self.ragas_available = False
        
        # Try to import RAGAS
        if self.use_ragas:
            try:
                from ragas.metrics import (
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                )
                self.ragas_available = True
                self.faithfulness_metric = faithfulness
                self.answer_relevancy_metric = answer_relevancy
                self.context_precision_metric = context_precision
                self.context_recall_metric = context_recall
                logger.info("RAGAS library loaded successfully")
            except ImportError:
                logger.warning(
                    "RAGAS not installed. Using fallback evaluation metrics. "
                    "Install with: pip install ragas"
                )
    
    def evaluate_sample(
        self,
        question: str,
        context: str,
        ground_truth: str,
        model_answer: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, MetricResult]:
        """
        Evaluate a single QA pair against multiple metrics.
        
        Args:
            question: The question asked
            context: The retrieved context
            ground_truth: The expected answer
            model_answer: The model's answer
            metadata: Optional metadata about the sample
            
        Returns:
            Dictionary mapping metric names to MetricResult objects
        """
        results = {}
        
        # Faithfulness: Does the answer follow from the context?
        results["faithfulness"] = self._evaluate_faithfulness(
            context, model_answer
        )
        
        # Answer Relevancy: Is the answer relevant to the question?
        results["answer_relevancy"] = self._evaluate_answer_relevancy(
            question, model_answer
        )
        
        # Context Precision: Is the context relevant to the question?
        results["context_precision"] = self._evaluate_context_precision(
            question, context
        )
        
        # Semantic Similarity: How similar is the answer to ground truth?
        results["semantic_similarity"] = self._evaluate_semantic_similarity(
            ground_truth, model_answer
        )
        
        return results
    
    def _evaluate_faithfulness(
        self,
        context: str,
        answer: str
    ) -> MetricResult:
        """
        Evaluate faithfulness: does the answer follow from the context?
        
        Fallback: Simple heuristic based on keyword overlap
        RAGAS: Uses LLM-based evaluation
        """
        metric_name = "faithfulness"
        
        try:
            if self.ragas_available:
                # TODO: Implement RAGAS faithfulness evaluation
                # This requires proper RAGAS setup with LLM backend
                score = self._fallback_faithfulness(context, answer)
            else:
                score = self._fallback_faithfulness(context, answer)
            
            return MetricResult(name=metric_name, value=score, success=True)
        
        except Exception as e:
            logger.warning(f"Failed to compute {metric_name}: {e}")
            return MetricResult(
                name=metric_name,
                value=0.0,
                success=False,
                error=str(e)
            )
    
    def _fallback_faithfulness(self, context: str, answer: str) -> float:
        """
        Fallback faithfulness evaluation using keyword overlap.
        
        Returns a score between 0 and 1 based on how much of the answer
        appears to be grounded in the context.
        """
        if not context or not answer:
            return 0.0
        
        context_words = set(context.lower().split())
        answer_words = answer.lower().split()
        
        if not answer_words:
            return 0.0
        
        # Count how many answer words appear in context
        grounded_words = sum(1 for word in answer_words if word in context_words)
        
        # Simple heuristic: proportion of answer words found in context
        # Cap at 0.95 since we're being conservative
        score = min(grounded_words / len(answer_words), 0.95)
        
        return score
    
    def _evaluate_answer_relevancy(
        self,
        question: str,
        answer: str
    ) -> MetricResult:
        """
        Evaluate answer relevancy: is the answer relevant to the question?
        
        Fallback: Based on keyword overlap between question and answer
        """
        metric_name = "answer_relevancy"
        
        try:
            if self.ragas_available:
                # TODO: Implement RAGAS answer_relevancy evaluation
                score = self._fallback_answer_relevancy(question, answer)
            else:
                score = self._fallback_answer_relevancy(question, answer)
            
            return MetricResult(name=metric_name, value=score, success=True)
        
        except Exception as e:
            logger.warning(f"Failed to compute {metric_name}: {e}")
            return MetricResult(
                name=metric_name,
                value=0.0,
                success=False,
                error=str(e)
            )
    
    def _fallback_answer_relevancy(self, question: str, answer: str) -> float:
        """
        Fallback answer relevancy using keyword overlap.
        
        Returns a score between 0 and 1 based on shared keywords
        between question and answer.
        """
        if not question or not answer:
            return 0.0
        
        # Remove common stop words for better matching
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "is", "was"}
        
        question_words = set(
            w.lower() for w in question.split() if w.lower() not in stop_words
        )
        answer_words = set(
            w.lower() for w in answer.split() if w.lower() not in stop_words
        )
        
        if not question_words:
            return 0.5  # No meaningful words in question
        
        # Jaccard similarity
        overlap = len(question_words & answer_words)
        union = len(question_words | answer_words)
        
        score = overlap / union if union > 0 else 0.0
        
        return score
    
    def _evaluate_context_precision(
        self,
        question: str,
        context: str
    ) -> MetricResult:
        """
        Evaluate context precision: is the context relevant to the question?
        
        Fallback: Based on keyword overlap
        """
        metric_name = "context_precision"
        
        try:
            if self.ragas_available:
                # TODO: Implement RAGAS context_precision evaluation
                score = self._fallback_context_precision(question, context)
            else:
                score = self._fallback_context_precision(question, context)
            
            return MetricResult(name=metric_name, value=score, success=True)
        
        except Exception as e:
            logger.warning(f"Failed to compute {metric_name}: {e}")
            return MetricResult(
                name=metric_name,
                value=0.0,
                success=False,
                error=str(e)
            )
    
    def _fallback_context_precision(self, question: str, context: str) -> float:
        """
        Fallback context precision evaluation.
        
        Similar to answer relevancy but for context.
        """
        return self._fallback_answer_relevancy(question, context)
    
    def _evaluate_semantic_similarity(
        self,
        ground_truth: str,
        model_answer: str
    ) -> MetricResult:
        """
        Evaluate semantic similarity between ground truth and model answer.
        
        Fallback: Based on token overlap and string similarity
        """
        metric_name = "semantic_similarity"
        
        try:
            score = self._fallback_semantic_similarity(ground_truth, model_answer)
            return MetricResult(name=metric_name, value=score, success=True)
        
        except Exception as e:
            logger.warning(f"Failed to compute {metric_name}: {e}")
            return MetricResult(
                name=metric_name,
                value=0.0,
                success=False,
                error=str(e)
            )
    
    def _fallback_semantic_similarity(
        self,
        ground_truth: str,
        model_answer: str
    ) -> float:
        """
        Fallback semantic similarity using Jaccard similarity on tokens.
        """
        if not ground_truth or not model_answer:
            return 0.0
        
        truth_tokens = set(ground_truth.lower().split())
        answer_tokens = set(model_answer.lower().split())
        
        overlap = len(truth_tokens & answer_tokens)
        union = len(truth_tokens | answer_tokens)
        
        score = overlap / union if union > 0 else 0.0
        
        return score
    
    def evaluate_batch(
        self,
        samples: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, float]]]:
        """
        Evaluate a batch of samples from the golden dataset.
        
        Args:
            samples: List of evaluation records from golden dataset
            
        Returns:
            Tuple of (detailed_results, aggregate_metrics)
        """
        detailed_results = []
        all_metrics = {}
        
        for i, sample in enumerate(samples):
            logger.info(f"Evaluating sample {i + 1}/{len(samples)}")
            
            try:
                question = sample.get("question", "")
                context = sample.get("retrieved_context", "")
                ground_truth = sample.get("ground_truth", "")
                model_answer = sample.get("model_answer", "")
                metadata = sample.get("metadata", {})
                
                # Evaluate sample
                metric_results = self.evaluate_sample(
                    question=question,
                    context=context,
                    ground_truth=ground_truth,
                    model_answer=model_answer,
                    metadata=metadata
                )
                
                # Store results
                sample_result = {
                    "sample_id": i,
                    "question": question,
                    "metadata": metadata,
                    "metrics": {
                        name: {
                            "value": result.value,
                            "success": result.success,
                            "error": result.error
                        }
                        for name, result in metric_results.items()
                    }
                }
                detailed_results.append(sample_result)
                
                # Accumulate metrics
                for metric_name, result in metric_results.items():
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    if result.success:
                        all_metrics[metric_name].append(result.value)
            
            except Exception as e:
                logger.error(f"Error evaluating sample {i}: {e}")
                continue
        
        # Aggregate metrics
        aggregated = {}
        for metric_name, scores in all_metrics.items():
            if scores:
                aggregated[metric_name] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "count": len(scores)
                }
        
        return detailed_results, aggregated
