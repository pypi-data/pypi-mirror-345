import pprint

from aiohttp import web  # type: ignore
from pydantic import ValidationError  # type: ignore

from cyanprintsdk.api.plugin.fn import LambdaPluginFn, LambdaPlugin
from cyanprintsdk.api.plugin.mapper import PluginMapper
from cyanprintsdk.api.plugin.req import PluginReq
from cyanprintsdk.api.plugin.res import PluginRes
from cyanprintsdk.api.processor.fn import LambdaProcessorFn, LambdaProcessor
from cyanprintsdk.api.processor.mapper import ProcessorMapper
from cyanprintsdk.api.processor.req import ProcessorReq
from cyanprintsdk.api.processor.res import ProcessorRes
from cyanprintsdk.api.template.fn import LambdaTemplate, LambdaTemplateFn
from cyanprintsdk.api.template.mapper import TemplateInputMapper, TemplateOutputMapper
from cyanprintsdk.api.template.req import TemplateAnswerReq, TemplateValidateReq
from cyanprintsdk.api.template.res import TemplateRes, TemplateValidRes
from cyanprintsdk.domain.core.cyan_script import (
    ICyanPlugin,
    ICyanProcessor,
    ICyanTemplate,
)

from cyanprintsdk.domain.plugin.input import PluginInput
from cyanprintsdk.domain.plugin.output import PluginOutput
from cyanprintsdk.domain.plugin.service import PluginService
from cyanprintsdk.domain.processor.input import ProcessorInput
from cyanprintsdk.domain.processor.output import ProcessorOutput
from cyanprintsdk.domain.processor.service import ProcessorService
from cyanprintsdk.domain.template.input import TemplateInput, TemplateValidateInput
from cyanprintsdk.domain.template.output import TemplateOutput
from cyanprintsdk.domain.template.service import TemplateService


async def health_check(request):
    return web.json_response(
        {
            "Message": "OK",
            "Status": "OK",
        }
    )


def start_plugin_with_fn(f: LambdaPluginFn):
    start_plugin(LambdaPlugin(f))


def start_plugin(plugin: ICyanPlugin):
    app = web.Application()

    plugin_service = PluginService(plugin)

    async def plug(request):
        try:
            json = await request.json()
            req = PluginReq(**json)
            pprint.pprint(req)
        except ValidationError as e:
            print(e)
            return web.json_response({"error": str(e)}, status=400)

        # translate to domain
        i: PluginInput = PluginMapper.to_domain(req)
        o: PluginOutput = await plugin_service.plug(i)
        res: PluginRes = PluginMapper.to_res(o)

        return web.json_response(res.model_dump(by_alias=True))

    app.add_routes(
        [
            web.get("/", health_check),
            web.post("/api/plug", plug),
        ]
    )

    web.run_app(app, port=5552)


def start_processor_with_fn(f: LambdaProcessorFn):
    start_processor(LambdaProcessor(f))


def start_processor(processor: ICyanProcessor):
    app = web.Application()

    proc_service = ProcessorService(processor)

    async def process(request):
        try:
            json = await request.json()
            req = ProcessorReq(**json)
            pprint.pprint(req)
        except ValidationError as e:
            print(e)
            return web.json_response({"error": str(e)}, status=400)

        # translate to domain
        i: ProcessorInput = ProcessorMapper.to_domain(req)
        o: ProcessorOutput = await proc_service.process(i)
        res: ProcessorRes = ProcessorMapper.to_res(o)

        return web.json_response(res.model_dump(by_alias=True))

    app.add_routes(
        [
            web.get("/", health_check),
            web.post("/api/process", process),
        ]
    )

    web.run_app(app, port=5551)


def start_template_with_fn(f: LambdaTemplateFn):
    start_template(LambdaTemplate(f))


def start_template(template: ICyanTemplate):
    app = web.Application()

    template_service = TemplateService(template)

    async def template_answer(request):
        try:
            json = await request.json()
            print(json)
            req = TemplateAnswerReq(**json)
            pprint.pprint(req)
        except ValidationError as e:
            print(e)
            return web.json_response({"error": str(e)}, status=400)

        # translate to domain
        i: TemplateInput = TemplateInputMapper.answer_to_domain(req)
        o: TemplateOutput = await template_service.template(i)
        res: TemplateRes = TemplateOutputMapper.to_resp(o)

        res_model = res.model_dump(by_alias=True)

        return web.json_response(res_model)

    async def template_validate(request):
        try:
            json = await request.json()
            req = TemplateValidateReq(**json)
            pprint.pprint(req)
        except ValidationError as e:
            print(e)
            return web.json_response({"error": str(e)}, status=400)

        # translate to domain
        i: TemplateValidateInput = TemplateInputMapper.validate_to_domain(req)
        o: str | None = await template_service.validate(i)
        if o == "":
            o = None
        res: TemplateValidRes = TemplateValidRes(valid=o)

        res_model = res.model_dump(by_alias=True)

        return web.json_response(res_model)

    app.add_routes(
        [
            web.get("/", health_check),
            web.post("/api/template/init", template_answer),
            web.post("/api/template/validate", template_validate),
        ]
    )

    web.run_app(app, port=5550)
