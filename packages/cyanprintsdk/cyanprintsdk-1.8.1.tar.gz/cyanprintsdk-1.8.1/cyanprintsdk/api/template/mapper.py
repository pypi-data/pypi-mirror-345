from cyanprintsdk.api.core.core_mapper import AnswerMapper, QuestionMapper, CyanMapper
from cyanprintsdk.api.template.req import TemplateAnswerReq, TemplateValidateReq
from cyanprintsdk.api.template.res import TemplateRes, TemplateQnARes, TemplateFinalRes
from cyanprintsdk.domain.template.input import TemplateInput, TemplateValidateInput
from cyanprintsdk.domain.template.output import (
    TemplateOutput,
    is_qna,
    is_final,
    TemplateQnAOutput,
    TemplateFinalOutput,
)
from typing import cast


class TemplateInputMapper:
    @staticmethod
    def answer_to_domain(req: TemplateAnswerReq) -> TemplateInput:
        answers = {}
        for id, answer in req.answers.items():
            answers[id] = AnswerMapper.to_domain(answer)

        return TemplateInput(
            answers=answers,
            deterministic_state=req.deterministic_states,
        )

    @staticmethod
    def validate_to_domain(req: TemplateValidateReq) -> TemplateValidateInput:
        answers = {}
        for id, answer in req.answers.items():
            answers[id] = AnswerMapper.to_domain(answer)

        return TemplateValidateInput(
            deterministic_state=req.deterministic_states,
            answers=answers,
            validate=req.validate,
        )


class TemplateOutputMapper:
    @staticmethod
    def to_resp(output: TemplateOutput) -> TemplateRes:
        if is_qna(output):
            qna_output = cast(TemplateQnAOutput, output)
            return TemplateQnARes(
                type="questionnaire",
                deterministic_state=qna_output.deterministic_state,
                question=QuestionMapper.question_to_resp(qna_output.question),
            )
        elif is_final(output):
            final_output = cast(TemplateFinalOutput, output)
            return TemplateFinalRes(
                cyan=CyanMapper.cyan_to_resp(final_output.data), type="final"
            )
        else:
            raise ValueError(f"Invalid output type {output}")
