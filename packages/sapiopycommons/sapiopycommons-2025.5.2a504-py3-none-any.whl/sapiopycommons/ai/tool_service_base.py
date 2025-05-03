from __future__ import annotations

import json
import traceback
from abc import abstractmethod, ABC
from typing import Any, Iterable, Sequence

from grpc import ServicerContext
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition

from sapiopycommons.ai.api.fielddefinitions.proto.fields_pb2 import FieldValueMapPbo, FieldValuePbo
from sapiopycommons.ai.api.fielddefinitions.proto.velox_field_def_pb2 import VeloxFieldDefPbo, FieldTypePbo, \
    SelectionPropertiesPbo, IntegerPropertiesPbo, DoublePropertiesPbo, BooleanPropertiesPbo
from sapiopycommons.ai.api.plan.tool.proto.entry_pb2 import StepOutputBatchPbo, StepItemContainerPbo, DataTypePbo, \
    StepBinaryContainerPbo, StepCsvContainerPbo, StepCsvHeaderRowPbo, StepCsvRowPbo, StepImageContainerPbo, \
    StepJsonContainerPbo, StepTextContainerPbo, StepInputBatchPbo
from sapiopycommons.ai.api.plan.tool.proto.tool_pb2 import ToolDetailsRequestPbo, ToolDetailsResponsePbo, \
    ToolDetailsPbo, ProcessStepRequestPbo, ProcessStepResponsePbo, ToolOutputDetailsPbo, ToolIoConfigBasePbo, \
    ToolInputDetailsPbo
from sapiopycommons.ai.api.plan.tool.proto.tool_pb2_grpc import ToolServiceServicer
from sapiopycommons.ai.api.session.proto.sapio_conn_info_pb2 import SapioUserSecretTypePbo, SapioConnectionInfoPbo
from sapiopycommons.ai.protobuf_utils import ProtobufUtils
from sapiopycommons.general.aliases import FieldMap, FieldValue


class SapioToolResult(ABC):
    """
    A class representing a result from a Sapio tool. Instantiate one of the subclasses to create a result object.
    """

    @abstractmethod
    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        """
        Convert this SapioToolResult object to a StepOutputBatchPbo or list of FieldValueMapPbo proto objects.
        """
        pass


class BinaryResult(SapioToolResult):
    """
    A class representing binary results from a Sapio tool.
    """
    binary_data: list[bytes]

    def __init__(self, binary_data: list[bytes]):
        """
        :param binary_data: The binary data as a list of bytes.
        """
        self.binary_data = binary_data

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                dataType=DataTypePbo.BINARY,
                binary_container=StepBinaryContainerPbo(items=self.binary_data)
            )
        )


class CsvResult(SapioToolResult):
    """
    A class representing CSV results from a Sapio tool.
    """
    csv_data: list[dict[str, Any]]

    def __init__(self, csv_data: list[dict[str, Any]]):
        """
        :param csv_data: The list of CSV data results, provided as a list of dictionaries of column name to value.
        """
        self.csv_data = csv_data

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                dataType=DataTypePbo.CSV,
                csv_container=StepCsvContainerPbo(
                    header=StepCsvHeaderRowPbo(cells=self.csv_data[0].keys()),
                    items=[StepCsvRowPbo(cells=[str(x) for x in row.values()]) for row in self.csv_data]
                )
            ) if self.csv_data else None
        )


class FieldMapResult(SapioToolResult):
    """
    A class representing field map results from a Sapio tool.
    """
    field_maps: list[FieldMap]

    def __init__(self, field_maps: list[FieldMap]):
        """
        :param field_maps: A list of field maps, where each map is a dictionary of field names to values. Each entry
            will create a new data record in the system, so long as the tool definition specifies an output data type
            name.
        """
        self.field_maps = field_maps

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        new_records: list[FieldValueMapPbo] = []
        for field_map in self.field_maps:
            fields: dict[str, FieldValuePbo] = {}
            for field, value in field_map.items():
                field_value = FieldValuePbo()
                if isinstance(value, str):
                    field_value.string_value = value
                elif isinstance(value, int):
                    field_value.int_value = value
                elif isinstance(value, float):
                    field_value.double_value = value
                elif isinstance(value, bool):
                    field_value.bool_value = value
                fields[field] = field_value
            new_records.append(FieldValueMapPbo(fields=fields))
        return new_records


class ImageResult(SapioToolResult):
    """
    A class representing image results from a Sapio tool.
    """
    image_format: str
    image_data: list[bytes]

    def __init__(self, image_format: str, image_data: list[bytes]):
        """
        :param image_format: The format of the image (e.g., PNG, JPEG).
        :param image_data: The image data as a list of bytes. Each entry in the list represents a separate image.
        """
        self.image_format = image_format
        self.image_data = image_data

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                dataType=DataTypePbo.IMAGE,
                image_container=StepImageContainerPbo(
                    image_format=self.image_format,
                    items=self.image_data)
            )
        )


class JsonResult(SapioToolResult):
    """
    A class representing JSON results from a Sapio tool.
    """
    json_data: list[Any]

    def __init__(self, json_data: list[Any]):
        """
        :param json_data: The list of JSON data results. Each entry in the list represents a separate JSON object.
            These entries must be able to be serialized to JSON using json.dumps().
        """
        self.json_data = json_data

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                dataType=DataTypePbo.JSON,
                json_container=StepJsonContainerPbo(items=[json.dumps(x) for x in self.json_data])
            )
        )


class TextResult(SapioToolResult):
    """
    A class representing text results from a Sapio tool.
    """
    text_data: list[str]

    def __init__(self, text_data: list[str]):
        """
        :param text_data: The text data as a list of strings.
        """
        self.text_data = text_data

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                dataType=DataTypePbo.TEXT,
                text_container=StepTextContainerPbo(items=self.text_data)
            )
        )


class ToolServiceBase(ToolServiceServicer, ABC):
    """
    A base class for implementing a tool service. Subclasses should implement the register_tools method to register
    their tools with the service.
    """
    def GetToolDetails(self, request: ToolDetailsRequestPbo, context: ServicerContext) -> ToolDetailsResponsePbo:
        try:
            # Get the tool details from the registered tools.
            details: list[ToolDetailsPbo] = self.get_details()
            return ToolDetailsResponsePbo(tool_framework_version=self.tool_version(), tool_details=details)
        except Exception:
            # TODO: This response doesn't even allow logs. What should we do if an exception occurs in this case?
            return ToolDetailsResponsePbo()

    def ProcessData(self, request: ProcessStepRequestPbo, context: ServicerContext) -> ProcessStepResponsePbo:
        try:
            # Convert the SapioConnectionInfo proto object to a SapioUser object.
            user = self.create_user(request.sapio_user)
            # Get the tool results from the registered tool matching the request and convert them to proto objects.
            output_data: list[StepOutputBatchPbo] = []
            new_records: list[FieldValueMapPbo] = []
            # TODO: Make use of the success value after the response object has a field for it.
            success, results, logs = self.run(user, request, context)
            for result in results:
                data: StepOutputBatchPbo | list[FieldValueMapPbo] = result.to_proto()
                if isinstance(data, StepOutputBatchPbo):
                    output_data.append(data)
                else:
                    new_records.extend(data)
            # Return a ProcessStepResponse proto object containing the output data and new records to the caller.
            return ProcessStepResponsePbo(output=output_data, log=logs, new_records=new_records)
        except Exception:
            # TODO: Return a False success result after the response object has a field for it.
            return ProcessStepResponsePbo(log=[traceback.format_exc()])

    @staticmethod
    def create_user(info: SapioConnectionInfoPbo, timeout_seconds: int = 60) -> SapioUser:
        """
        Create a SapioUser object from the given SapioConnectionInfo proto object.

        :param info: The SapioConnectionInfo proto object.
        :param timeout_seconds: The request timeout for calls made from this user object.
        """
        # TODO: Have a customizable request timeout? Would need to be added to the request object.
        # TODO: How should the RMI hosts and port be used in the connection info?
        user = SapioUser(info.webservice_url, True, timeout_seconds, guid=info.app_guid)
        if info.secret_type == SapioUserSecretTypePbo.SESSION_TOKEN:
            user.api_token = info.secret
        elif info.secret_type == SapioUserSecretTypePbo.PASSWORD:
            # TODO: Will the secret be base64 encoded if it's a password? That's how basic auth is normally handled.
            user.password = info.secret
        else:
            raise Exception(f"Unexpected secret type: {info.secret_type}")
        return user

    @staticmethod
    def tool_version() -> int:
        """
        :return: The version of this tool.
        """
        return 1

    def _get_tools(self) -> list[ToolBase]:
        """
        return: Get the tools registered with this service.
        """
        tools: list[ToolBase] = self.register_tools()
        if not tools:
            raise Exception("No tools registered with this service.")
        return tools

    def _get_tool(self, name: str) -> ToolBase:
        """
        Get a specific tool by its name.

        :param name: The name of the tool to retrieve.
        :return: The tool object corresponding to the given name.
        """
        tools: dict[str, ToolBase] = {x.name: x for x in self.register_tools()}
        if not tools:
            raise Exception("No tools registered with this service.")
        if name not in tools:
            raise Exception(f"Tool \"{name}\" not found in registered tools.")
        return tools[name]

    @abstractmethod
    def register_tools(self) -> list[ToolBase]:
        """
        Register the tools with this service. Create and instantiate ToolBase subclasses to register them.

        :return: A list of tools to register to this service.
        """
        pass

    def get_details(self) -> list[ToolDetailsPbo]:
        """
        Get the details of the tool.

        :return: A ToolDetailsResponse object containing the tool details.
        """
        tool_details: list[ToolDetailsPbo] = []
        for tool in self._get_tools():
            tool_details.append(tool.to_pbo())
        return tool_details

    def run(self, user: SapioUser, request: ProcessStepRequestPbo, context: ServicerContext) \
            -> tuple[bool, list[SapioToolResult], list[str]]:
        """
        Execute a tool from this service.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :param request: The request object containing the input data.
        :param context: The gRPC context.
        :return: Whether or not the tool succeeded, the results of the tool, and any logs generated by the tool.
        """
        tool = self._get_tool(request.tool_name)
        try:
            tool.setup(user, request, context)
            results: list[SapioToolResult] = tool.run(user)
            return True, results, tool.logs
        except Exception:
            tool.log_message(traceback.format_exc())
            return False, [], tool.logs


class ToolBase(ABC):
    """
    A base class for implementing a tool.
    """
    name: str
    description: str
    data_type_name: str | None
    inputs: list[ToolInputDetailsPbo]
    outputs: list[ToolOutputDetailsPbo]
    configs: list[VeloxFieldDefPbo]
    logs: list[str]

    user: SapioUser
    request: ProcessStepRequestPbo
    context: ServicerContext
    verbose_logging: bool

    def __init__(self, name: str, description: str, data_type_name: str | None = None):
        """
        :param name: The name of the tool.
        :param description: A description of the tool.
        :param data_type_name: The name of the output data type of this tool, if applicable. When this tool returns
            FieldMapResult objects in its run method, this name will be used to set the data type of the output data.
        """
        self.name = name
        self.description = description
        self.data_type_name = data_type_name
        self.inputs = []
        self.outputs = []
        self.configs = []
        self.logs = []

    def setup(self, user: SapioUser, request: ProcessStepRequestPbo, context: ServicerContext) -> None:
        """
        Setup the tool with the user, request, and context. This method can be overridden by subclasses to perform
        additional setup.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :param request: The request object containing the input data.
        :param context: The gRPC context.
        """
        self.user = user
        self.request = request
        self.context = context
        # TODO: Determine verbose logging from the request.
        self.verbose_logging = False

    def add_input(self, content_type: DataTypePbo, display_name: str, description: str, example: str | None = None,
                  validation: str | None = None, input_count: tuple[int, int] | None = None, is_paged: bool = False,
                  page_size: tuple[int, int] | None = None, max_request_bytes: int | None = None) -> None:
        """
        Add an input configuration to the tool. This determines how many inputs this tool will accept in the plan
        manager, as well as what those inputs are. The IO number of the input will be set to the current number of
        inputs. That is, the first time this is called, the IO number will be 0, the second time it is called, the IO
        number will be 1, and so on.

        :param content_type: The content type of the input.
        :param display_name: The display name of the input.
        :param description: The description of the input.
        :param example: An optional example of the input.
        :param validation: An optional validation string for the input.
        :param input_count: A tuple of the minimum and maximum number of inputs allowed for this tool.
        :param is_paged: If true, this input will be paged. If false, this input will not be paged.
        :param page_size: A tuple of the minimum and maximum page size for this tool. The input must be paged in order
            for this to have an effect.
        :param max_request_bytes: The maximum request size in bytes for this tool.
        """
        self.inputs.append(ToolInputDetailsPbo(
            base_config=ToolIoConfigBasePbo(
                io_number=len(self.inputs),
                content_type=ProtobufUtils.content_type_str(content_type),
                display_name=display_name,
                description=description,
                example=example
            ),
            validation=validation,
            min_input_count=input_count[0] if input_count else None,
            max_input_count=input_count[1] if input_count else None,
            paged=is_paged,
            min_page_size=page_size[0] if page_size else None,
            max_page_size=page_size[1] if page_size else None,
            max_request_bytes=max_request_bytes,
        ))

    def add_output(self, content_type: DataTypePbo, display_name: str, description: str, example: str | None = None) -> None:
        """
        Add an output configuration to the tool. This determines how many inputs this tool will accept in the plan
        manager, as well as what those inputs are. The IO number of the output will be set to the current number of
        outputs. That is, the first time this is called, the IO number will be 0, the second time it is called, the IO
        number will be 1, and so on.

        :param content_type: The content type of the output.
        :param display_name: The display name of the output.
        :param description: The description of the output.
        :param example: An example of the output.
        """
        self.outputs.append(ToolOutputDetailsPbo(
            base_config=ToolIoConfigBasePbo(
                io_number=len(self.outputs),
                content_type=ProtobufUtils.content_type_str(content_type),
                display_name=display_name,
                description=description,
                example=example
            )))

    def add_config_field(self, field: VeloxFieldDefPbo) -> None:
        """
        Add a configuration field to the tool. This field will be used to configure the tool in the plan manager.

        :param field: The configuration field details.
        """
        self.configs.append(field)

    def add_config_field_def(self, field: AbstractVeloxFieldDefinition) -> None:
        """
        Add a configuration field to the tool. This field will be used to configure the tool in the plan manager.

        :param field: The configuration field details.
        """
        self.configs.append(ProtobufUtils.field_def_to_pbo(field))

    def add_boolean_config_field(self, field_name: str, display_name: str, description: str, default_value: bool) \
            -> None:
        """
        Add a boolean configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        """
        self.configs.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.BOOLEAN,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=True,
            editable=True,
            boolean_properties=BooleanPropertiesPbo(
                default_value=default_value
            )
        ))

    def add_double_config_field(self, field_name: str, display_name: str, description: str, default_value: float,
                                min_value: float = -10.**120, max_value: float = 10.**120, precision: int = 2) -> None:
        """
        Add a double configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param min_value: The minimum value of the field.
        :param max_value: The maximum value of the field.
        :param precision: The precision of the field.
        """
        self.configs.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.DOUBLE,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=True,
            editable=True,
            double_properties=DoublePropertiesPbo(
                default_value=default_value,
                min_value=min_value,
                max_value=max_value,
                precision=precision
            )
        ))

    def add_integer_config_field(self, field_name: str, display_name: str, description: str,
                                 default_value: int, min_value: int = -2**31, max_value: int = 2**31-1) -> None:
        """
        Add an integer configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param min_value: The minimum value of the field.
        :param max_value: The maximum value of the field.
        """
        self.configs.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.INTEGER,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=True,
            editable=True,
            integer_properties=IntegerPropertiesPbo(
                default_value=default_value,
                min_value=min_value,
                max_value=max_value
            )
        ))

    def add_list_config_field(self, field_name: str, display_name: str, description: str, default_value: str,
                              allowed_values: list[str]) -> None:
        """
        Add a list configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param allowed_values: The list of allowed values for the field.
        """
        self.configs.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.SELECTION,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=True,
            editable=True,
            selection_properties=SelectionPropertiesPbo(
                default_value=default_value,
                static_list_values=allowed_values,
            )
        ))

    def add_multi_list_config_field(self, field_name: str, display_name: str, description: str,
                                    default_value: list[str], allowed_values: list[str]) -> None:
        """
        Add a multi-select list configuration field to the tool. This field will be used to configure the tool in the
        plan manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param allowed_values: The list of allowed values for the field.
        """
        self.configs.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.SELECTION,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=True,
            editable=True,
            selection_properties=SelectionPropertiesPbo(
                default_value=",".join(default_value),
                static_list_values=allowed_values,
                multi_select=True,
            )
        ))

    def to_pbo(self) -> ToolDetailsPbo:
        """
        :return: The ToolDetailsPbo proto object representing this tool.
        """
        return ToolDetailsPbo(
            name=self.name,
            description=self.description,
            input_configs=self.inputs,
            output_configs=self.outputs,
            output_data_type_name=self.data_type_name,
            config_fields=self.configs
        )

    @abstractmethod
    def run(self, user: SapioUser) -> list[SapioToolResult]:
        """
        Execute this tool.

        The request inputs can be accessed using the self.get_input_*() methods.
        The request settings can be accessed using the self.get_config_fields() method.
        The request itself can be accessed using self.request.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :return: A SapioToolResults object containing the response data. Each result in the list corresponds to a
            separate output from the tool. Field map results do not appear as tool output in the plan manager, instead
            appearing as records related to the plan step during the run.
        """
        pass

    def log_message(self, message: str, verbose: bool = False) -> None:
        """
        Log a message for this tool. This message will be included in the logs returned to the caller.

        :param message: The message to log.
        :param verbose: If true, the message will only be logged if verbose logging is enabled. If false, the message
            will be logged regardless of the verbose logging setting.
        """
        if not verbose or self.verbose_logging:
            self.logs.append(f"{self.name}: {message}")

    def get_input_binary(self, index: int = 0) -> list[bytes]:
        """
        Get the binary data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: The binary data from the request object.
        """
        return list(self.request.input[index].item_container.binary_container.items)

    def get_input_csv(self, index: int = 0) -> tuple[list[str], list[dict[str, str]]]:
        """
        Parse the CSV data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A tuple containing the header row and the data rows. The header row is a list of strings representing
            the column names, and the data rows are a list of dictionaries where each dictionary represents a row in the
            CSV with the column names as keys and the corresponding values as strings.
        """
        input_data: Sequence[StepInputBatchPbo] = self.request.input
        ret_val: list[dict[str, str]] = []
        headers: Iterable[str] = input_data[index].item_container.csv_container.header.cells
        for row in input_data[index].item_container.csv_container.items:
            row_dict: dict[str, str] = {}
            for header, value in zip(headers, row.cells):
                row_dict[header] = value
            ret_val.append(row_dict)
        return list(headers), ret_val

    def get_input_images(self, index: int = 0) -> tuple[str, list[bytes]]:
        """
        Parse the image data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A tuple containing the image format and the image data. The image format is a string representing the
            format of the image (e.g., PNG, JPEG), and the image data is a list of bytes representing the image data.
            Each entry in the list represents a separate image.
        """
        image_data: StepImageContainerPbo = self.request.input[index].item_container.image_container
        return image_data.image_format, list(image_data.items)

    def get_input_json(self, index: int = 0) -> list[list[Any]] | list[dict[str, Any]]:
        """
        Parse the JSON data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A list of parsed JSON objects. Each entry in the list represents a separate JSON entry from the input.
            Depending on this tool, this may be a list of dictionaries or a list of lists.
        """
        return [json.loads(x) for x in self.request.input[index].item_container.json_container.items]

    def get_input_text(self, index: int = 0) -> list[str]:
        """
        Parse the text data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A list of text data as strings.
        """
        return list(self.request.input[index].item_container.text_container.items)

    def get_config_defs(self) -> dict[str, VeloxFieldDefPbo]:
        """
        Get the config field definitions for this tool.

        :return: A dictionary of field definitions, where the keys are the field names and the values are the
            VeloxFieldDefPbo objects representing the field definitions.
        """
        field_defs: dict[str, VeloxFieldDefPbo] = {}
        for field_def in self.to_pbo().config_fields:
            field_defs[field_def.data_field_name] = field_def
        return field_defs

    def get_config_fields(self) -> dict[str, FieldValue]:
        """
        Get the configuration fields from the request object.

        :return: A dictionary of configuration field names and their values.
        """
        config_fields: dict[str, Any] = {}
        field_defs: dict[str, VeloxFieldDefPbo] = self.get_config_defs()
        for field_name, value in self.request.config_field_values.items():
            if field_name not in field_defs:
                continue
            config_fields[field_name] = ProtobufUtils.field_pbo_to_value(field_defs[field_name], value)
        return config_fields

    @staticmethod
    def read_from_json(json_data: list[dict[str, Any]], key: str) -> list[Any]:
        """
        From a list of dictionaries, return a list of values for the given key from each dictionary. Skips null values.

        :param json_data: The JSON data to read from.
        :param key: The key to read the values from.
        :return: A list of values corresponding to the given key in the JSON data.
        """
        ret_val: list[Any] = []
        for entry in json_data:
            if key in entry:
                value = entry[key]
                if isinstance(value, list):
                    ret_val.extend(value)
                elif value is not None:
                    ret_val.append(value)
        return ret_val
