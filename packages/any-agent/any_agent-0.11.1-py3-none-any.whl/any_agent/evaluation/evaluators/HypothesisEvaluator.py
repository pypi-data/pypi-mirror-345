from collections.abc import Sequence

from any_agent.evaluation.evaluators.LLMEvaluator import LLMEvaluator
from any_agent.evaluation.evaluators.schemas import EvaluationResult
from any_agent.evaluation.test_case import CheckpointCriteria, GroundTruthAnswer


class HypothesisEvaluator(LLMEvaluator):
    """Evaluates the final answer against ground truth."""

    def evaluate(
        self,
        hypothesis_final_answer: str,
        ground_truth_answer_dict: Sequence[GroundTruthAnswer],
        ground_truth_checkpoints: Sequence[CheckpointCriteria],
    ) -> list[EvaluationResult]:
        """Verify if the final answer meets all specified criteria."""
        results = []

        for criterion in ground_truth_checkpoints:
            evaluation = self.llm_evaluate_with_criterion(
                criteria=criterion.criteria,
                points=criterion.points,
                ground_truth_output=ground_truth_answer_dict,
                hypothesis_final_answer=hypothesis_final_answer,
            )

            results.append(evaluation)

        return results
