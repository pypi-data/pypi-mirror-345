from typing import cast
from cyanprintsdk.api.core.answer_req import (
    AnswerReq,
    BoolAnswerReq,
    StringAnswerReq,
    StringArrayAnswerReq,
    is_bool_answer_req,
    is_string_answer_req,
    is_string_array_answer_req,
)
from cyanprintsdk.api.core.answer_res import (
    AnswerRes,
    BoolAnswerRes,
    StringAnswerRes,
    StringArrayAnswerRes,
)
from cyanprintsdk.api.core.cyan_req import (
    CyanPluginReq,
    CyanGlobReq,
    CyanProcessorReq,
    CyanReq,
)
from cyanprintsdk.api.core.cyan_res import (
    CyanRes,
    CyanProcessorRes,
    CyanPluginRes,
    CyanGlobRes,
)
from cyanprintsdk.api.core.question_res import (
    QuestionRes,
    ConfirmQuestionRes,
    CheckboxQuestionRes,
    SelectQuestionRes,
    DateQuestionRes,
    PasswordQuestionRes,
    TextQuestionRes,
)
from cyanprintsdk.domain.core.answer import (
    Answer,
    is_string_array_answer,
    is_bool_answer,
    is_string_answer,
    BoolAnswer,
    StringAnswer,
    StringArrayAnswer,
)
from cyanprintsdk.domain.core.cyan import (
    CyanPlugin,
    CyanGlob,
    GlobType,
    CyanProcessor,
    Cyan,
)
from cyanprintsdk.domain.core.question import (
    Question,
    ConfirmQ,
    CheckboxQ,
    SelectQ,
    DateQ,
    PasswordQ,
    TextQ,
)


class CyanMapper:
    @staticmethod
    def plugin_req_to_domain(req: CyanPluginReq) -> CyanPlugin:
        return CyanPlugin(name=req.name, config=req.config)

    @staticmethod
    def glob_req_to_domain(req: CyanGlobReq) -> CyanGlob:
        if req.type == "template":
            glob_type = GlobType.Template
        elif req.type == "copy":
            glob_type = GlobType.Copy
        else:
            raise ValueError(f"Invalid req.type: {req.type}")

        return CyanGlob(
            root=req.root, glob=req.glob, exclude=req.exclude, type=glob_type
        )

    @staticmethod
    def processor_req_to_domain(req: CyanProcessorReq) -> CyanProcessor:
        files = [CyanMapper.glob_req_to_domain(x) for x in req.files]
        return CyanProcessor(name=req.name, config=req.config, files=files)

    @staticmethod
    def cyan_req_to_domain(req: CyanReq) -> Cyan:
        processors = [CyanMapper.processor_req_to_domain(x) for x in req.processors]
        plugins = [CyanMapper.plugin_req_to_domain(x) for x in req.plugins]
        return Cyan(processors=processors, plugins=plugins)

    @staticmethod
    def cyan_to_resp(data: Cyan) -> CyanRes:
        processors = [CyanMapper.processor_to_resp(x) for x in data.processors]
        plugins = [CyanMapper.plugin_to_resp(x) for x in data.plugins]
        return CyanRes(processors=processors, plugins=plugins)

    @staticmethod
    def processor_to_resp(data: CyanProcessor) -> CyanProcessorRes:
        files = [CyanMapper.glob_to_resp(x) for x in data.files]
        return CyanProcessorRes(name=data.name, config=data.config, files=files)

    @staticmethod
    def plugin_to_resp(data: CyanPlugin) -> CyanPluginRes:
        return CyanPluginRes(name=data.name, config=data.config)

    @staticmethod
    def glob_type_to_resp(t: GlobType) -> str:
        if t == GlobType.Template:
            return "template"
        elif t == GlobType.Copy:
            return "copy"
        else:
            raise ValueError(f"Invalid GlobType: {t}")

    @staticmethod
    def glob_to_resp(data: CyanGlob) -> CyanGlobRes:
        return CyanGlobRes(
            root=data.root,
            glob=data.glob,
            exclude=data.exclude,
            type=CyanMapper.glob_type_to_resp(data.type),
        )


class QuestionMapper:
    @staticmethod
    def question_to_resp(q: Question) -> QuestionRes:
        if isinstance(q, SelectQ):
            return QuestionMapper.select_to_resp(q)
        elif isinstance(q, TextQ):
            return QuestionMapper.text_to_resp(q)
        elif isinstance(q, PasswordQ):
            return QuestionMapper.password_to_resp(q)
        elif isinstance(q, DateQ):
            return QuestionMapper.date_to_resp(q)
        elif isinstance(q, ConfirmQ):
            return QuestionMapper.confirm_to_resp(q)
        elif isinstance(q, CheckboxQ):
            return QuestionMapper.checkbox_to_resp(q)
        else:
            raise ValueError(f"Invalid question type: {q}")

    @staticmethod
    def confirm_to_resp(q: ConfirmQ) -> ConfirmQuestionRes:
        return ConfirmQuestionRes(
            default=q.default,
            message=q.message,
            id=q.id,
            error_message=q.error_message,
            desc=q.desc,
            type="confirm",
        )

    @staticmethod
    def checkbox_to_resp(q: CheckboxQ) -> CheckboxQuestionRes:
        return CheckboxQuestionRes(
            message=q.message, id=q.id, desc=q.desc, options=q.options, type="checkbox"
        )

    @staticmethod
    def select_to_resp(q: SelectQ) -> SelectQuestionRes:
        return SelectQuestionRes(
            message=q.message, id=q.id, desc=q.desc, options=q.options, type="select"
        )

    @staticmethod
    def text_to_resp(q: TextQ) -> TextQuestionRes:
        return TextQuestionRes(
            message=q.message,
            id=q.id,
            desc=q.desc,
            default=q.default,
            initial=q.initial,
            type="text",
        )

    @staticmethod
    def password_to_resp(q: PasswordQ) -> PasswordQuestionRes:
        return PasswordQuestionRes(
            message=q.message,
            id=q.id,
            desc=q.desc,
            confirmation=q.confirmation,
            type="password",
        )

    @staticmethod
    def date_to_resp(q: DateQ) -> DateQuestionRes:
        return DateQuestionRes(
            message=q.message,
            id=q.id,
            desc=q.desc,
            default=q.default.isoformat() if q.default else None,
            maxDate=q.max_date.isoformat() if q.max_date else None,
            minDate=q.min_date.isoformat() if q.min_date else None,
            type="date",
        )


class AnswerMapper:
    @staticmethod
    def to_domain(req: AnswerReq) -> Answer:
        if is_bool_answer_req(req):
            bool_answer = cast(BoolAnswerReq, req)
            return BoolAnswer(answer=bool_answer.answer)
        elif is_string_answer_req(req):
            string_answer = cast(StringAnswerReq, req)
            return StringAnswer(answer=string_answer.answer)
        elif is_string_array_answer_req(req):
            string_array_answer = cast(StringArrayAnswerReq, req)
            return StringArrayAnswer(answer=string_array_answer.answer)
        else:
            raise ValueError(f"Invalid answer request type: {req}")

    @staticmethod
    def to_resp(answer: Answer) -> AnswerRes:
        if is_bool_answer(answer):
            return BoolAnswerRes(answer=answer.answer)
        elif is_string_answer(answer):
            return StringAnswerRes(answer=answer.answer)
        elif is_string_array_answer(answer):
            return StringArrayAnswerRes(answer=answer.answer)
        else:
            raise ValueError(f"Invalid answer type: {answer}")
