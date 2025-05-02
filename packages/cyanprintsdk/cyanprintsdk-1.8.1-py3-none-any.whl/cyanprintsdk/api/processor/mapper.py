from cyanprintsdk.api.core.core_mapper import CyanMapper
from cyanprintsdk.api.processor.req import ProcessorReq
from cyanprintsdk.api.processor.res import ProcessorRes
from cyanprintsdk.domain.processor.input import ProcessorInput
from cyanprintsdk.domain.processor.output import ProcessorOutput


class ProcessorMapper:
    @staticmethod
    def to_domain(req: ProcessorReq) -> ProcessorInput:
        globs = [CyanMapper.glob_req_to_domain(x) for x in req.globs]
        return ProcessorInput(
            read_directory=req.read_dir,
            write_directory=req.write_dir,
            config=req.config,
            globs=globs,
        )

    @staticmethod
    def to_res(res: ProcessorOutput) -> ProcessorRes:
        return ProcessorRes(output_dir=res.directory)
