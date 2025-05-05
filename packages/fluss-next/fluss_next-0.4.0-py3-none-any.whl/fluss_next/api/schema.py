from enum import Enum
from typing import Any, Optional, List, Annotated, Dict, Iterable, Literal, Union, Tuple
from fluss_next.scalars import ValidatorFunction, EventValue
from datetime import datetime
from fluss_next.funcs import aexecute, execute
from pydantic import BaseModel, ConfigDict, Field
from fluss_next.traits import MockableTrait
from fluss_next.rath import FlussRath
from rath.scalars import ID


class GraphNodeKind(str, Enum):
    """No documentation"""

    REACTIVE = "REACTIVE"
    ARGS = "ARGS"
    RETURNS = "RETURNS"
    REKUEST = "REKUEST"
    REKUEST_FILTER = "REKUEST_FILTER"


class PortKind(str, Enum):
    """The kind of port."""

    INT = "INT"
    STRING = "STRING"
    STRUCTURE = "STRUCTURE"
    LIST = "LIST"
    BOOL = "BOOL"
    DICT = "DICT"
    FLOAT = "FLOAT"
    DATE = "DATE"
    UNION = "UNION"
    ENUM = "ENUM"
    MODEL = "MODEL"
    MEMORY_STRUCTURE = "MEMORY_STRUCTURE"


class EffectKind(str, Enum):
    """The kind of effect."""

    MESSAGE = "MESSAGE"
    HIDE = "HIDE"
    CUSTOM = "CUSTOM"


class AssignWidgetKind(str, Enum):
    """The kind of assign widget."""

    SEARCH = "SEARCH"
    CHOICE = "CHOICE"
    SLIDER = "SLIDER"
    CUSTOM = "CUSTOM"
    STRING = "STRING"
    STATE_CHOICE = "STATE_CHOICE"


class ReturnWidgetKind(str, Enum):
    """The kind of return widget."""

    CHOICE = "CHOICE"
    CUSTOM = "CUSTOM"


class ActionKind(str, Enum):
    """The kind of action."""

    FUNCTION = "FUNCTION"
    GENERATOR = "GENERATOR"


class GraphEdgeKind(str, Enum):
    """No documentation"""

    VANILLA = "VANILLA"
    LOGGING = "LOGGING"


class ReactiveImplementation(str, Enum):
    """No documentation"""

    ZIP = "ZIP"
    COMBINELATEST = "COMBINELATEST"
    WITHLATEST = "WITHLATEST"
    BUFFER_COMPLETE = "BUFFER_COMPLETE"
    BUFFER_UNTIL = "BUFFER_UNTIL"
    BUFFER_COUNT = "BUFFER_COUNT"
    DELAY = "DELAY"
    DELAY_UNTIL = "DELAY_UNTIL"
    CHUNK = "CHUNK"
    SPLIT = "SPLIT"
    OMIT = "OMIT"
    ENSURE = "ENSURE"
    SELECT = "SELECT"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"
    JUST = "JUST"
    PREFIX = "PREFIX"
    SUFFIX = "SUFFIX"
    FILTER = "FILTER"
    GATE = "GATE"
    TO_LIST = "TO_LIST"
    REORDER = "REORDER"
    FOREACH = "FOREACH"
    IF = "IF"
    AND = "AND"
    ALL = "ALL"


class RunEventKind(str, Enum):
    """No documentation"""

    NEXT = "NEXT"
    ERROR = "ERROR"
    COMPLETE = "COMPLETE"
    UNKNOWN = "UNKNOWN"


class MapStrategy(str, Enum):
    """No documentation"""

    MAP = "MAP"
    MAP_TO = "MAP_TO"
    MAP_FROM = "MAP_FROM"


class OffsetPaginationInput(BaseModel):
    """No documentation"""

    offset: int
    limit: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateWorkspaceInput(BaseModel):
    """No documentation"""

    workspace: ID
    graph: "GraphInput"
    title: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphInput(BaseModel):
    """No documentation"""

    nodes: Tuple["GraphNodeInput", ...]
    edges: Tuple["GraphEdgeInput", ...]
    globals: Tuple["GlobalArgInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphNodeInput(BaseModel):
    """No documentation"""

    hello: Optional[str] = None
    path: Optional[str] = None
    id: str
    kind: GraphNodeKind
    position: "PositionInput"
    parent_node: Optional[str] = Field(alias="parentNode", default=None)
    ins: Tuple[Tuple["PortInput", ...], ...]
    outs: Tuple[Tuple["PortInput", ...], ...]
    constants: Tuple["PortInput", ...]
    voids: Tuple["PortInput", ...]
    constants_map: Dict = Field(alias="constantsMap")
    globals_map: Dict = Field(alias="globalsMap")
    description: Optional[str] = None
    title: Optional[str] = None
    retries: Optional[int] = None
    retry_delay: Optional[int] = Field(alias="retryDelay", default=None)
    action_kind: Optional[ActionKind] = Field(alias="actionKind", default=None)
    next_timeout: Optional[int] = Field(alias="nextTimeout", default=None)
    hash: Optional[str] = None
    map_strategy: Optional[MapStrategy] = Field(alias="mapStrategy", default=None)
    allow_local_execution: Optional[bool] = Field(
        alias="allowLocalExecution", default=None
    )
    binds: Optional["BindsInput"] = None
    implementation: Optional[ReactiveImplementation] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PositionInput(BaseModel):
    """No documentation"""

    x: float
    y: float
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PortInput(BaseModel):
    """Port

    A Port is a single input or output of a action. It is composed of a key and a kind
    which are used to uniquely identify the port.

    If the Port is a structure, we need to define a identifier and scope,
    Identifiers uniquely identify a specific type of model for the scopes (e.g
    all the ports that have the identifier "@mikro/image" are of the same type, and
    are hence compatible with each other). Scopes are used to define in which context
    the identifier is valid (e.g. a port with the identifier "@mikro/image" and the
    scope "local", can only be wired to other ports that have the same identifier and
    are running in the same app). Global ports are ports that have the scope "global",
    and can be wired to any other port that has the same identifier, as there exists a
    mechanism to resolve and retrieve the object for each app. Please check the rekuest
    documentation for more information on how this works.


    """

    validators: Optional[Tuple["ValidatorInput", ...]] = None
    key: str
    label: Optional[str] = None
    kind: PortKind
    description: Optional[str] = None
    identifier: Optional[str] = None
    nullable: bool
    effects: Optional[Tuple["EffectInput", ...]] = None
    default: Optional[Any] = None
    children: Optional[Tuple["PortInput", ...]] = None
    choices: Optional[Tuple["ChoiceInput", ...]] = None
    assign_widget: Optional["AssignWidgetInput"] = Field(
        alias="assignWidget", default=None
    )
    return_widget: Optional["ReturnWidgetInput"] = Field(
        alias="returnWidget", default=None
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ValidatorInput(BaseModel):
    """
    A validating function for a port. Can specify a function that will run when validating values of the port.
    If outside dependencies are needed they need to be specified in the dependencies field. With the .. syntax
    when transversing the tree of ports.

    """

    function: ValidatorFunction
    dependencies: Optional[Tuple[str, ...]] = None
    label: Optional[str] = None
    error_message: Optional[str] = Field(alias="errorMessage", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EffectInput(BaseModel):
    """
                 An effect is a way to modify a port based on a condition. For example,
    you could have an effect that sets a port to null if another port is null.

    Or, you could have an effect that hides the port if another port meets a condition.
    E.g when the user selects a certain option in a dropdown, another port is hidden.


    """

    function: ValidatorFunction
    dependencies: Optional[Tuple[str, ...]] = None
    message: Optional[str] = None
    kind: EffectKind
    hook: Optional[str] = None
    ward: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChoiceInput(BaseModel):
    """
    A choice is a value that can be selected in a dropdown.

    It is composed of a value, a label, and a description. The value is the
    value that is returned when the choice is selected. The label is the
    text that is displayed in the dropdown. The description is the text
    that is displayed when the user hovers over the choice.

    """

    value: Any
    label: str
    image: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AssignWidgetInput(BaseModel):
    """No documentation"""

    as_paragraph: Optional[bool] = Field(alias="asParagraph", default=None)
    "Whether to display the input as a paragraph or not. This is used for text inputs and dropdowns"
    kind: AssignWidgetKind
    query: Optional[str] = None
    choices: Optional[Tuple[ChoiceInput, ...]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    placeholder: Optional[str] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    fallback: Optional["AssignWidgetInput"] = None
    filters: Optional[Tuple[PortInput, ...]] = None
    dependencies: Optional[Tuple[str, ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ReturnWidgetInput(BaseModel):
    """A Return Widget is a UI element that is used to display the value of a port.

    Return Widgets get displayed both if we show the return values of an assignment,
    but also when we inspect the given arguments of a previous run task. Their primary
    usecase is to adequately display the value of a port, in a user readable way.

    Return Widgets are often overwriten by the underlying UI framework (e.g. Orkestrator)
    to provide a better user experience. For example, a return widget that displays a
    date could be overwriten to display a calendar widget.

    Return Widgets provide more a way to customize this overwriten behavior.

    """

    kind: ReturnWidgetKind
    query: Optional[str] = None
    choices: Optional[Tuple[ChoiceInput, ...]] = None
    min: Optional[int] = None
    max: Optional[int] = None
    step: Optional[int] = None
    placeholder: Optional[str] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BindsInput(BaseModel):
    """No documentation"""

    implementations: Optional[Tuple[str, ...]] = None
    clients: Optional[Tuple[str, ...]] = None
    desired_instances: int = Field(alias="desiredInstances")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GraphEdgeInput(BaseModel):
    """No documentation"""

    label: Optional[str] = None
    level: Optional[str] = None
    kind: GraphEdgeKind
    id: str
    source: str
    target: str
    source_handle: str = Field(alias="sourceHandle")
    target_handle: str = Field(alias="targetHandle")
    stream: Tuple["StreamItemInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StreamItemInput(BaseModel):
    """No documentation"""

    kind: PortKind
    label: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GlobalArgInput(BaseModel):
    """No documentation"""

    key: str
    port: PortInput
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateWorkspaceInput(BaseModel):
    """No documentation"""

    graph: Optional[GraphInput] = None
    title: Optional[str] = None
    description: Optional[str] = None
    vanilla: bool
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateRunInput(BaseModel):
    """No documentation"""

    flow: ID
    snapshot_interval: int = Field(alias="snapshotInterval")
    assignation: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SnapshotRunInput(BaseModel):
    """No documentation"""

    run: ID
    events: Tuple[ID, ...]
    t: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TrackInput(BaseModel):
    """No documentation"""

    reference: str
    t: int
    kind: RunEventKind
    value: Optional[EventValue] = None
    run: ID
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    message: Optional[str] = None
    exception: Optional[str] = None
    source: Optional[str] = None
    handle: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RunFlow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    title: str
    model_config = ConfigDict(frozen=True)


class RunEvents(BaseModel):
    """RunEvent(id, created_at, reference, run, kind, t, caused_by, source, handle, value, exception)"""

    typename: Literal["RunEvent"] = Field(
        alias="__typename", default="RunEvent", exclude=True
    )
    kind: RunEventKind
    "The type of event"
    t: int
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    created_at: datetime = Field(alias="createdAt")
    value: Optional[EventValue] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class Run(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    assignation: ID
    flow: RunFlow
    events: Tuple[RunEvents, ...]
    created_at: datetime = Field(alias="createdAt")
    model_config = ConfigDict(frozen=True)


class FlussStringAssignWidget(BaseModel):
    """No documentation"""

    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    placeholder: str
    as_paragraph: bool = Field(alias="asParagraph")
    model_config = ConfigDict(frozen=True)


class FlussSliderAssignWidget(BaseModel):
    """No documentation"""

    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    min: Optional[float] = Field(default=None)
    max: Optional[float] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussSearchAssignWidget(BaseModel):
    """No documentation"""

    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    query: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussCustomAssignWidget(BaseModel):
    """No documentation"""

    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )
    ward: str
    hook: str
    model_config = ConfigDict(frozen=True)


class FlussChoiceAssignWidgetChoices(BaseModel):
    """No documentation"""

    typename: Literal["Choice"] = Field(
        alias="__typename", default="Choice", exclude=True
    )
    value: str
    label: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussChoiceAssignWidget(BaseModel):
    """No documentation"""

    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )
    kind: AssignWidgetKind
    choices: Optional[Tuple[FlussChoiceAssignWidgetChoices, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussCustomEffect(BaseModel):
    """No documentation"""

    typename: Literal["CustomEffect"] = Field(
        alias="__typename", default="CustomEffect", exclude=True
    )
    kind: EffectKind
    hook: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussMessageEffect(BaseModel):
    """No documentation"""

    typename: Literal["MessageEffect"] = Field(
        alias="__typename", default="MessageEffect", exclude=True
    )
    kind: EffectKind
    message: str
    model_config = ConfigDict(frozen=True)


class Validator(BaseModel):
    """No documentation"""

    typename: Literal["Validator"] = Field(
        alias="__typename", default="Validator", exclude=True
    )
    function: ValidatorFunction
    dependencies: Optional[Tuple[str, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussCustomReturnWidget(BaseModel):
    """No documentation"""

    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )
    kind: ReturnWidgetKind
    hook: str
    ward: str
    model_config = ConfigDict(frozen=True)


class FlussChoiceReturnWidgetChoices(BaseModel):
    """No documentation"""

    typename: Literal["Choice"] = Field(
        alias="__typename", default="Choice", exclude=True
    )
    label: str
    value: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussChoiceReturnWidget(BaseModel):
    """No documentation"""

    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )
    choices: Optional[Tuple[FlussChoiceReturnWidgetChoices, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class EvenBasierGraphNodeBase(BaseModel):
    """No documentation"""

    parent_node: Optional[str] = Field(default=None, alias="parentNode")


class EvenBasierGraphNodeCatch(EvenBasierGraphNodeBase):
    """Catch all class for EvenBasierGraphNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    parent_node: Optional[str] = Field(default=None, alias="parentNode")


class EvenBasierGraphNodeRekuestFilterActionNode(EvenBasierGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class EvenBasierGraphNodeRekuestMapActionNode(EvenBasierGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class EvenBasierGraphNodeArgNode(EvenBasierGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class EvenBasierGraphNodeReturnNode(EvenBasierGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class EvenBasierGraphNodeReactiveNode(EvenBasierGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class FlussBinds(BaseModel):
    """No documentation"""

    typename: Literal["Binds"] = Field(
        alias="__typename", default="Binds", exclude=True
    )
    implementations: Tuple[ID, ...]
    model_config = ConfigDict(frozen=True)


class RetriableNodeBase(BaseModel):
    """No documentation"""

    retries: Optional[int] = Field(default=None)
    retry_delay: Optional[int] = Field(default=None, alias="retryDelay")


class RetriableNodeCatch(RetriableNodeBase):
    """Catch all class for RetriableNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    retries: Optional[int] = Field(default=None)
    retry_delay: Optional[int] = Field(default=None, alias="retryDelay")


class RetriableNodeRekuestFilterActionNode(RetriableNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class RetriableNodeRekuestMapActionNode(RetriableNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class AssignableNodeBase(BaseModel):
    """No documentation"""

    next_timeout: Optional[int] = Field(default=None, alias="nextTimeout")


class AssignableNodeCatch(AssignableNodeBase):
    """Catch all class for AssignableNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    next_timeout: Optional[int] = Field(default=None, alias="nextTimeout")


class AssignableNodeRekuestFilterActionNode(AssignableNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class AssignableNodeRekuestMapActionNode(AssignableNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class StreamItem(MockableTrait, BaseModel):
    """No documentation"""

    typename: Literal["StreamItem"] = Field(
        alias="__typename", default="StreamItem", exclude=True
    )
    kind: PortKind
    label: str
    model_config = ConfigDict(frozen=True)


class ListFlowWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ListFlow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    title: str
    created_at: datetime = Field(alias="createdAt")
    workspace: ListFlowWorkspace
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenAssignwidgetBase(BaseModel):
    """No documentation"""

    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortNestedChildrenAssignwidgetBaseCatchAll(
    FlussChildPortNestedChildrenAssignwidgetBase, BaseModel
):
    """Catch all class for FlussChildPortNestedChildrenAssignwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPortNestedChildrenReturnwidgetBase(BaseModel):
    """No documentation"""

    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedChildrenReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortNestedChildrenReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortNestedChildrenReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortNestedChildrenReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPortNestedChildrenReturnwidgetBaseCatchAll(
    FlussChildPortNestedChildrenReturnwidgetBase, BaseModel
):
    """Catch all class for FlussChildPortNestedChildrenReturnwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPortNestedChildren(BaseModel):
    """No documentation"""

    typename: Literal["Port"] = Field(alias="__typename", default="Port", exclude=True)
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    assign_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortNestedChildrenAssignwidgetBaseSliderAssignWidget,
                    FlussChildPortNestedChildrenAssignwidgetBaseChoiceAssignWidget,
                    FlussChildPortNestedChildrenAssignwidgetBaseSearchAssignWidget,
                    FlussChildPortNestedChildrenAssignwidgetBaseStateChoiceAssignWidget,
                    FlussChildPortNestedChildrenAssignwidgetBaseStringAssignWidget,
                    FlussChildPortNestedChildrenAssignwidgetBaseCustomAssignWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortNestedChildrenAssignwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortNestedChildrenReturnwidgetBaseCustomReturnWidget,
                    FlussChildPortNestedChildrenReturnwidgetBaseChoiceReturnWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortNestedChildrenReturnwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="returnWidget")
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedAssignwidgetBase(BaseModel):
    """No documentation"""

    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortNestedAssignwidgetBaseCatchAll(
    FlussChildPortNestedAssignwidgetBase, BaseModel
):
    """Catch all class for FlussChildPortNestedAssignwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPortNestedReturnwidgetBase(BaseModel):
    """No documentation"""

    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortNestedReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortNestedReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortNestedReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortNestedReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPortNestedReturnwidgetBaseCatchAll(
    FlussChildPortNestedReturnwidgetBase, BaseModel
):
    """Catch all class for FlussChildPortNestedReturnwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPortNested(BaseModel):
    """No documentation"""

    typename: Literal["Port"] = Field(alias="__typename", default="Port", exclude=True)
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    children: Optional[Tuple[FlussChildPortNestedChildren, ...]] = Field(default=None)
    assign_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortNestedAssignwidgetBaseSliderAssignWidget,
                    FlussChildPortNestedAssignwidgetBaseChoiceAssignWidget,
                    FlussChildPortNestedAssignwidgetBaseSearchAssignWidget,
                    FlussChildPortNestedAssignwidgetBaseStateChoiceAssignWidget,
                    FlussChildPortNestedAssignwidgetBaseStringAssignWidget,
                    FlussChildPortNestedAssignwidgetBaseCustomAssignWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortNestedAssignwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortNestedReturnwidgetBaseCustomReturnWidget,
                    FlussChildPortNestedReturnwidgetBaseChoiceReturnWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortNestedReturnwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="returnWidget")
    model_config = ConfigDict(frozen=True)


class RekuestActionNodeBase(BaseModel):
    """No documentation"""

    hash: str
    map_strategy: str = Field(alias="mapStrategy")
    allow_local_execution: bool = Field(alias="allowLocalExecution")
    binds: FlussBinds
    action_kind: ActionKind = Field(alias="actionKind")


class RekuestActionNodeCatch(RekuestActionNodeBase):
    """Catch all class for RekuestActionNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    hash: str
    map_strategy: str = Field(alias="mapStrategy")
    allow_local_execution: bool = Field(alias="allowLocalExecution")
    binds: FlussBinds
    action_kind: ActionKind = Field(alias="actionKind")


class RekuestActionNodeRekuestFilterActionNode(RekuestActionNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class RekuestActionNodeRekuestMapActionNode(RekuestActionNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class BaseGraphEdgeBase(BaseModel):
    """No documentation"""

    id: ID
    source: str
    source_handle: str = Field(alias="sourceHandle")
    target: str
    target_handle: str = Field(alias="targetHandle")
    kind: GraphEdgeKind
    stream: Tuple[StreamItem, ...]


class BaseGraphEdgeCatch(BaseGraphEdgeBase):
    """Catch all class for BaseGraphEdgeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    id: ID
    source: str
    source_handle: str = Field(alias="sourceHandle")
    target: str
    target_handle: str = Field(alias="targetHandle")
    kind: GraphEdgeKind
    stream: Tuple[StreamItem, ...]


class BaseGraphEdgeVanillaEdge(BaseGraphEdgeBase, BaseModel):
    """No documentation"""

    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )


class BaseGraphEdgeLoggingEdge(BaseGraphEdgeBase, BaseModel):
    """No documentation"""

    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )


class ListWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    title: str
    description: Optional[str] = Field(default=None)
    latest_flow: Optional[ListFlow] = Field(default=None, alias="latestFlow")
    model_config = ConfigDict(frozen=True)


class FlussChildPortAssignwidgetBase(BaseModel):
    """No documentation"""

    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseStateChoiceAssignWidget(
    FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussChildPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussChildPortAssignwidgetBaseCatchAll(FlussChildPortAssignwidgetBase, BaseModel):
    """Catch all class for FlussChildPortAssignwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPortReturnwidgetBase(BaseModel):
    """No documentation"""

    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussChildPortReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussChildPortReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussChildPortReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussChildPortReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussChildPortReturnwidgetBaseCatchAll(FlussChildPortReturnwidgetBase, BaseModel):
    """Catch all class for FlussChildPortReturnwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussChildPort(BaseModel):
    """No documentation"""

    typename: Literal["Port"] = Field(alias="__typename", default="Port", exclude=True)
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    children: Optional[Tuple[FlussChildPortNested, ...]] = Field(default=None)
    assign_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortAssignwidgetBaseSliderAssignWidget,
                    FlussChildPortAssignwidgetBaseChoiceAssignWidget,
                    FlussChildPortAssignwidgetBaseSearchAssignWidget,
                    FlussChildPortAssignwidgetBaseStateChoiceAssignWidget,
                    FlussChildPortAssignwidgetBaseStringAssignWidget,
                    FlussChildPortAssignwidgetBaseCustomAssignWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortAssignwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussChildPortReturnwidgetBaseCustomReturnWidget,
                    FlussChildPortReturnwidgetBaseChoiceReturnWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussChildPortReturnwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="returnWidget")
    nullable: bool
    model_config = ConfigDict(frozen=True)


class LoggingEdge(BaseGraphEdgeLoggingEdge, BaseModel):
    """No documentation"""

    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )
    level: str
    model_config = ConfigDict(frozen=True)


class VanillaEdge(BaseGraphEdgeVanillaEdge, BaseModel):
    """No documentation"""

    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )
    label: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class FlussPortEffectsBase(BaseModel):
    """No documentation"""

    kind: EffectKind
    function: ValidatorFunction
    dependencies: Tuple[str, ...]
    model_config = ConfigDict(frozen=True)


class FlussPortEffectsBaseCustomEffect(
    FlussCustomEffect, FlussPortEffectsBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomEffect"] = Field(
        alias="__typename", default="CustomEffect", exclude=True
    )


class FlussPortEffectsBaseMessageEffect(
    FlussMessageEffect, FlussPortEffectsBase, BaseModel
):
    """No documentation"""

    typename: Literal["MessageEffect"] = Field(
        alias="__typename", default="MessageEffect", exclude=True
    )


class FlussPortEffectsBaseCatchAll(FlussPortEffectsBase, BaseModel):
    """Catch all class for FlussPortEffectsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussPortAssignwidgetBase(BaseModel):
    """No documentation"""

    kind: AssignWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussPortAssignwidgetBaseSliderAssignWidget(
    FlussSliderAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SliderAssignWidget"] = Field(
        alias="__typename", default="SliderAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseChoiceAssignWidget(
    FlussChoiceAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceAssignWidget"] = Field(
        alias="__typename", default="ChoiceAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseSearchAssignWidget(
    FlussSearchAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["SearchAssignWidget"] = Field(
        alias="__typename", default="SearchAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseStateChoiceAssignWidget(
    FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StateChoiceAssignWidget"] = Field(
        alias="__typename", default="StateChoiceAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseStringAssignWidget(
    FlussStringAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["StringAssignWidget"] = Field(
        alias="__typename", default="StringAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseCustomAssignWidget(
    FlussCustomAssignWidget, FlussPortAssignwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomAssignWidget"] = Field(
        alias="__typename", default="CustomAssignWidget", exclude=True
    )


class FlussPortAssignwidgetBaseCatchAll(FlussPortAssignwidgetBase, BaseModel):
    """Catch all class for FlussPortAssignwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussPortReturnwidgetBase(BaseModel):
    """No documentation"""

    kind: ReturnWidgetKind
    model_config = ConfigDict(frozen=True)


class FlussPortReturnwidgetBaseCustomReturnWidget(
    FlussCustomReturnWidget, FlussPortReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["CustomReturnWidget"] = Field(
        alias="__typename", default="CustomReturnWidget", exclude=True
    )


class FlussPortReturnwidgetBaseChoiceReturnWidget(
    FlussChoiceReturnWidget, FlussPortReturnwidgetBase, BaseModel
):
    """No documentation"""

    typename: Literal["ChoiceReturnWidget"] = Field(
        alias="__typename", default="ChoiceReturnWidget", exclude=True
    )


class FlussPortReturnwidgetBaseCatchAll(FlussPortReturnwidgetBase, BaseModel):
    """Catch all class for FlussPortReturnwidgetBase"""

    typename: str = Field(alias="__typename", exclude=True)


class FlussPort(BaseModel):
    """No documentation"""

    typename: Literal["Port"] = Field(alias="__typename", default="Port", exclude=True)
    key: str
    label: Optional[str] = Field(default=None)
    nullable: bool
    description: Optional[str] = Field(default=None)
    effects: Optional[
        Tuple[
            Union[
                Annotated[
                    Union[
                        FlussPortEffectsBaseCustomEffect,
                        FlussPortEffectsBaseMessageEffect,
                    ],
                    Field(discriminator="typename"),
                ],
                FlussPortEffectsBaseCatchAll,
            ],
            ...,
        ]
    ] = Field(default=None)
    assign_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussPortAssignwidgetBaseSliderAssignWidget,
                    FlussPortAssignwidgetBaseChoiceAssignWidget,
                    FlussPortAssignwidgetBaseSearchAssignWidget,
                    FlussPortAssignwidgetBaseStateChoiceAssignWidget,
                    FlussPortAssignwidgetBaseStringAssignWidget,
                    FlussPortAssignwidgetBaseCustomAssignWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussPortAssignwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="assignWidget")
    return_widget: Optional[
        Union[
            Annotated[
                Union[
                    FlussPortReturnwidgetBaseCustomReturnWidget,
                    FlussPortReturnwidgetBaseChoiceReturnWidget,
                ],
                Field(discriminator="typename"),
            ],
            FlussPortReturnwidgetBaseCatchAll,
        ]
    ] = Field(default=None, alias="returnWidget")
    kind: PortKind
    identifier: Optional[str] = Field(default=None)
    children: Optional[Tuple[FlussChildPort, ...]] = Field(default=None)
    default: Optional[Any] = Field(default=None)
    nullable: bool
    validators: Optional[Tuple[Validator, ...]] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ReactiveTemplate(BaseModel):
    """ReactiveTemplate(id, title, description, implementation, ins, outs, voids, constants)"""

    typename: Literal["ReactiveTemplate"] = Field(
        alias="__typename", default="ReactiveTemplate", exclude=True
    )
    id: ID
    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    implementation: ReactiveImplementation
    "Check async Programming Textbook"
    title: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class BaseGraphNodePosition(BaseModel):
    """No documentation"""

    typename: Literal["Position"] = Field(
        alias="__typename", default="Position", exclude=True
    )
    x: float
    y: float
    model_config = ConfigDict(frozen=True)


class BaseGraphNodeBase(BaseModel):
    """No documentation"""

    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    voids: Tuple[FlussPort, ...]
    id: ID
    position: BaseGraphNodePosition
    parent_node: Optional[str] = Field(default=None, alias="parentNode")
    globals_map: Dict = Field(alias="globalsMap")
    constants_map: Dict = Field(alias="constantsMap")
    title: str
    description: str
    kind: GraphNodeKind


class BaseGraphNodeCatch(BaseGraphNodeBase):
    """Catch all class for BaseGraphNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    ins: Tuple[Tuple[FlussPort, ...], ...]
    outs: Tuple[Tuple[FlussPort, ...], ...]
    constants: Tuple[FlussPort, ...]
    voids: Tuple[FlussPort, ...]
    id: ID
    position: BaseGraphNodePosition
    parent_node: Optional[str] = Field(default=None, alias="parentNode")
    globals_map: Dict = Field(alias="globalsMap")
    constants_map: Dict = Field(alias="constantsMap")
    title: str
    description: str
    kind: GraphNodeKind


class BaseGraphNodeRekuestFilterActionNode(
    EvenBasierGraphNodeRekuestFilterActionNode, BaseGraphNodeBase, BaseModel
):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class BaseGraphNodeRekuestMapActionNode(
    EvenBasierGraphNodeRekuestMapActionNode, BaseGraphNodeBase, BaseModel
):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class BaseGraphNodeArgNode(EvenBasierGraphNodeArgNode, BaseGraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class BaseGraphNodeReturnNode(
    EvenBasierGraphNodeReturnNode, BaseGraphNodeBase, BaseModel
):
    """No documentation"""

    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class BaseGraphNodeReactiveNode(
    EvenBasierGraphNodeReactiveNode, BaseGraphNodeBase, BaseModel
):
    """No documentation"""

    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GlobalArg(BaseModel):
    """No documentation"""

    typename: Literal["GlobalArg"] = Field(
        alias="__typename", default="GlobalArg", exclude=True
    )
    key: str
    port: FlussPort
    model_config = ConfigDict(frozen=True)


class RekuestMapActionNode(
    RekuestActionNodeRekuestMapActionNode,
    AssignableNodeRekuestMapActionNode,
    RetriableNodeRekuestMapActionNode,
    BaseGraphNodeRekuestMapActionNode,
    BaseModel,
):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )
    hello: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class RekuestFilterActionNode(
    RekuestActionNodeRekuestFilterActionNode,
    AssignableNodeRekuestFilterActionNode,
    RetriableNodeRekuestFilterActionNode,
    BaseGraphNodeRekuestFilterActionNode,
    BaseModel,
):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )
    path: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ReactiveNode(BaseGraphNodeReactiveNode, BaseModel):
    """No documentation"""

    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )
    implementation: ReactiveImplementation
    model_config = ConfigDict(frozen=True)


class ArgNode(BaseGraphNodeArgNode, BaseModel):
    """No documentation"""

    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )
    model_config = ConfigDict(frozen=True)


class ReturnNode(BaseGraphNodeReturnNode, BaseModel):
    """No documentation"""

    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )
    model_config = ConfigDict(frozen=True)


class GraphNodeBase(BaseModel):
    """No documentation"""

    kind: GraphNodeKind


class GraphNodeCatch(GraphNodeBase):
    """Catch all class for GraphNodeBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "No documentation"
    kind: GraphNodeKind


class GraphNodeRekuestFilterActionNode(
    RekuestFilterActionNode, GraphNodeBase, BaseModel
):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class GraphNodeRekuestMapActionNode(RekuestMapActionNode, GraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class GraphNodeArgNode(ArgNode, GraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class GraphNodeReturnNode(ReturnNode, GraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class GraphNodeReactiveNode(ReactiveNode, GraphNodeBase, BaseModel):
    """No documentation"""

    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GraphNodesBase(BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class GraphNodesBaseRekuestFilterActionNode(
    GraphNodeRekuestFilterActionNode, GraphNodesBase, BaseModel
):
    """No documentation"""

    typename: Literal["RekuestFilterActionNode"] = Field(
        alias="__typename", default="RekuestFilterActionNode", exclude=True
    )


class GraphNodesBaseRekuestMapActionNode(
    GraphNodeRekuestMapActionNode, GraphNodesBase, BaseModel
):
    """No documentation"""

    typename: Literal["RekuestMapActionNode"] = Field(
        alias="__typename", default="RekuestMapActionNode", exclude=True
    )


class GraphNodesBaseArgNode(GraphNodeArgNode, GraphNodesBase, BaseModel):
    """No documentation"""

    typename: Literal["ArgNode"] = Field(
        alias="__typename", default="ArgNode", exclude=True
    )


class GraphNodesBaseReturnNode(GraphNodeReturnNode, GraphNodesBase, BaseModel):
    """No documentation"""

    typename: Literal["ReturnNode"] = Field(
        alias="__typename", default="ReturnNode", exclude=True
    )


class GraphNodesBaseReactiveNode(GraphNodeReactiveNode, GraphNodesBase, BaseModel):
    """No documentation"""

    typename: Literal["ReactiveNode"] = Field(
        alias="__typename", default="ReactiveNode", exclude=True
    )


class GraphNodesBaseCatchAll(GraphNodesBase, BaseModel):
    """Catch all class for GraphNodesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class GraphEdgesBase(BaseModel):
    """No documentation"""

    model_config = ConfigDict(frozen=True)


class GraphEdgesBaseVanillaEdge(VanillaEdge, GraphEdgesBase, BaseModel):
    """No documentation"""

    typename: Literal["VanillaEdge"] = Field(
        alias="__typename", default="VanillaEdge", exclude=True
    )


class GraphEdgesBaseLoggingEdge(LoggingEdge, GraphEdgesBase, BaseModel):
    """No documentation"""

    typename: Literal["LoggingEdge"] = Field(
        alias="__typename", default="LoggingEdge", exclude=True
    )


class GraphEdgesBaseCatchAll(GraphEdgesBase, BaseModel):
    """Catch all class for GraphEdgesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class Graph(BaseModel):
    """No documentation"""

    typename: Literal["Graph"] = Field(
        alias="__typename", default="Graph", exclude=True
    )
    nodes: Tuple[
        Union[
            Annotated[
                Union[
                    GraphNodesBaseRekuestFilterActionNode,
                    GraphNodesBaseRekuestMapActionNode,
                    GraphNodesBaseArgNode,
                    GraphNodesBaseReturnNode,
                    GraphNodesBaseReactiveNode,
                ],
                Field(discriminator="typename"),
            ],
            GraphNodesBaseCatchAll,
        ],
        ...,
    ]
    edges: Tuple[
        Union[
            Annotated[
                Union[GraphEdgesBaseVanillaEdge, GraphEdgesBaseLoggingEdge],
                Field(discriminator="typename"),
            ],
            GraphEdgesBaseCatchAll,
        ],
        ...,
    ]
    globals: Tuple[GlobalArg, ...]
    model_config = ConfigDict(frozen=True)


class FlowWorkspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class Flow(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    id: ID
    graph: Graph
    title: str
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(alias="createdAt")
    workspace: FlowWorkspace
    model_config = ConfigDict(frozen=True)


class Workspace(BaseModel):
    """Graph is a Template for a Template"""

    typename: Literal["Workspace"] = Field(
        alias="__typename", default="Workspace", exclude=True
    )
    id: ID
    title: str
    latest_flow: Optional[Flow] = Field(default=None, alias="latestFlow")
    model_config = ConfigDict(frozen=True)


class CreateRunMutationCreaterun(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class CreateRunMutation(BaseModel):
    """Start a run on fluss"""

    create_run: CreateRunMutationCreaterun = Field(alias="createRun")

    class Arguments(BaseModel):
        """Arguments for CreateRun"""

        input: CreateRunInput

    class Meta:
        """Meta class for CreateRun"""

        document = "mutation CreateRun($input: CreateRunInput!) {\n  createRun(input: $input) {\n    id\n    __typename\n  }\n}"


class CloseRunMutationCloserun(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class CloseRunMutation(BaseModel):
    """Start a run on fluss"""

    close_run: CloseRunMutationCloserun = Field(alias="closeRun")

    class Arguments(BaseModel):
        """Arguments for CloseRun"""

        run: ID

    class Meta:
        """Meta class for CloseRun"""

        document = "mutation CloseRun($run: ID!) {\n  closeRun(input: {run: $run}) {\n    id\n    __typename\n  }\n}"


class SnapshotMutationSnapshot(BaseModel):
    """Snapshot(id, created_at, run, t, status)"""

    typename: Literal["Snapshot"] = Field(
        alias="__typename", default="Snapshot", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class SnapshotMutation(BaseModel):
    """Snapshot the current state on the fluss platform"""

    snapshot: SnapshotMutationSnapshot

    class Arguments(BaseModel):
        """Arguments for Snapshot"""

        input: SnapshotRunInput

    class Meta:
        """Meta class for Snapshot"""

        document = "mutation Snapshot($input: SnapshotRunInput!) {\n  snapshot(input: $input) {\n    id\n    __typename\n  }\n}"


class TrackMutationTrack(BaseModel):
    """RunEvent(id, created_at, reference, run, kind, t, caused_by, source, handle, value, exception)"""

    typename: Literal["RunEvent"] = Field(
        alias="__typename", default="RunEvent", exclude=True
    )
    id: ID
    kind: RunEventKind
    "The type of event"
    value: Optional[EventValue] = Field(default=None)
    caused_by: Tuple[ID, ...] = Field(alias="causedBy")
    model_config = ConfigDict(frozen=True)


class TrackMutation(BaseModel):
    """Track a new event on the fluss platform"""

    track: TrackMutationTrack

    class Arguments(BaseModel):
        """Arguments for Track"""

        input: TrackInput

    class Meta:
        """Meta class for Track"""

        document = "mutation Track($input: TrackInput!) {\n  track(input: $input) {\n    id\n    kind\n    value\n    causedBy\n    __typename\n  }\n}"


class UpdateWorkspaceMutation(BaseModel):
    """No documentation found for this operation."""

    update_workspace: Workspace = Field(alias="updateWorkspace")

    class Arguments(BaseModel):
        """Arguments for UpdateWorkspace"""

        input: UpdateWorkspaceInput

    class Meta:
        """Meta class for UpdateWorkspace"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n}\n\nfragment FlussBinds on Binds {\n  implementations\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment RekuestActionNode on RekuestActionNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  actionKind\n  __typename\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment RekuestFilterActionNode on RekuestFilterActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment RekuestMapActionNode on RekuestMapActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterActionNode\n  ...RekuestMapActionNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateWorkspace($input: UpdateWorkspaceInput!) {\n  updateWorkspace(input: $input) {\n    ...Workspace\n    __typename\n  }\n}"


class CreateWorkspaceMutation(BaseModel):
    """No documentation found for this operation."""

    create_workspace: Workspace = Field(alias="createWorkspace")

    class Arguments(BaseModel):
        """Arguments for CreateWorkspace"""

        input: CreateWorkspaceInput

    class Meta:
        """Meta class for CreateWorkspace"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n}\n\nfragment FlussBinds on Binds {\n  implementations\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment RekuestActionNode on RekuestActionNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  actionKind\n  __typename\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment RekuestFilterActionNode on RekuestFilterActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment RekuestMapActionNode on RekuestMapActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterActionNode\n  ...RekuestMapActionNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nmutation CreateWorkspace($input: CreateWorkspaceInput!) {\n  createWorkspace(input: $input) {\n    ...Workspace\n    __typename\n  }\n}"


class RunQuery(BaseModel):
    """No documentation found for this operation."""

    run: Run

    class Arguments(BaseModel):
        """Arguments for Run"""

        id: ID

    class Meta:
        """Meta class for Run"""

        document = "fragment Run on Run {\n  id\n  assignation\n  flow {\n    id\n    title\n    __typename\n  }\n  events {\n    kind\n    t\n    causedBy\n    createdAt\n    value\n    __typename\n  }\n  createdAt\n  __typename\n}\n\nquery Run($id: ID!) {\n  run(id: $id) {\n    ...Run\n    __typename\n  }\n}"


class SearchRunsQueryOptions(BaseModel):
    """Run(id, created_at, flow, assignation, status, snapshot_interval)"""

    typename: Literal["Run"] = Field(alias="__typename", default="Run", exclude=True)
    value: ID
    label: ID
    model_config = ConfigDict(frozen=True)


class SearchRunsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchRunsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchRuns"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        """Meta class for SearchRuns"""

        document = "query SearchRuns($search: String, $values: [ID!]) {\n  options: runs(filters: {search: $search, ids: $values}) {\n    value: id\n    label: assignation\n    __typename\n  }\n}"


class WorkspaceQuery(BaseModel):
    """No documentation found for this operation."""

    workspace: Workspace

    class Arguments(BaseModel):
        """Arguments for Workspace"""

        id: ID

    class Meta:
        """Meta class for Workspace"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n}\n\nfragment FlussBinds on Binds {\n  implementations\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment RekuestActionNode on RekuestActionNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  actionKind\n  __typename\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment RekuestFilterActionNode on RekuestFilterActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment RekuestMapActionNode on RekuestMapActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterActionNode\n  ...RekuestMapActionNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nfragment Workspace on Workspace {\n  id\n  title\n  latestFlow {\n    ...Flow\n    __typename\n  }\n  __typename\n}\n\nquery Workspace($id: ID!) {\n  workspace(id: $id) {\n    ...Workspace\n    __typename\n  }\n}"


class WorkspacesQuery(BaseModel):
    """No documentation found for this operation."""

    workspaces: Tuple[ListWorkspace, ...]

    class Arguments(BaseModel):
        """Arguments for Workspaces"""

        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        """Meta class for Workspaces"""

        document = "fragment ListFlow on Flow {\n  id\n  title\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment ListWorkspace on Workspace {\n  id\n  title\n  description\n  latestFlow {\n    ...ListFlow\n    __typename\n  }\n  __typename\n}\n\nquery Workspaces($pagination: OffsetPaginationInput) {\n  workspaces(pagination: $pagination) {\n    ...ListWorkspace\n    __typename\n  }\n}"


class ReactiveTemplatesQuery(BaseModel):
    """No documentation found for this operation."""

    reactive_templates: Tuple[ReactiveTemplate, ...] = Field(alias="reactiveTemplates")

    class Arguments(BaseModel):
        """Arguments for ReactiveTemplates"""

        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        """Meta class for ReactiveTemplates"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ReactiveTemplate on ReactiveTemplate {\n  id\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  implementation\n  title\n  description\n  __typename\n}\n\nquery ReactiveTemplates($pagination: OffsetPaginationInput) {\n  reactiveTemplates(pagination: $pagination) {\n    ...ReactiveTemplate\n    __typename\n  }\n}"


class ReactiveTemplateQuery(BaseModel):
    """No documentation found for this operation."""

    reactive_template: ReactiveTemplate = Field(alias="reactiveTemplate")

    class Arguments(BaseModel):
        """Arguments for ReactiveTemplate"""

        id: ID

    class Meta:
        """Meta class for ReactiveTemplate"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ReactiveTemplate on ReactiveTemplate {\n  id\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  implementation\n  title\n  description\n  __typename\n}\n\nquery ReactiveTemplate($id: ID!) {\n  reactiveTemplate(id: $id) {\n    ...ReactiveTemplate\n    __typename\n  }\n}"


class GetFlowQuery(BaseModel):
    """No documentation found for this operation."""

    flow: Flow

    class Arguments(BaseModel):
        """Arguments for GetFlow"""

        id: ID

    class Meta:
        """Meta class for GetFlow"""

        document = "fragment FlussChildPortNested on Port {\n  __typename\n  kind\n  identifier\n  children {\n    kind\n    identifier\n    assignWidget {\n      __typename\n      kind\n      ...FlussStringAssignWidget\n      ...FlussSearchAssignWidget\n      ...FlussSliderAssignWidget\n      ...FlussChoiceAssignWidget\n      ...FlussCustomAssignWidget\n    }\n    returnWidget {\n      __typename\n      kind\n      ...FlussCustomReturnWidget\n      ...FlussChoiceReturnWidget\n    }\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n}\n\nfragment EvenBasierGraphNode on GraphNode {\n  __typename\n  parentNode\n}\n\nfragment FlussBinds on Binds {\n  implementations\n  __typename\n}\n\nfragment FlussStringAssignWidget on StringAssignWidget {\n  __typename\n  kind\n  placeholder\n  asParagraph\n}\n\nfragment FlussCustomAssignWidget on CustomAssignWidget {\n  __typename\n  ward\n  hook\n}\n\nfragment FlussSearchAssignWidget on SearchAssignWidget {\n  __typename\n  kind\n  query\n  ward\n}\n\nfragment FlussSliderAssignWidget on SliderAssignWidget {\n  __typename\n  kind\n  min\n  max\n}\n\nfragment Validator on Validator {\n  function\n  dependencies\n  __typename\n}\n\nfragment AssignableNode on AssignableNode {\n  nextTimeout\n  __typename\n}\n\nfragment RekuestActionNode on RekuestActionNode {\n  hash\n  mapStrategy\n  allowLocalExecution\n  binds {\n    ...FlussBinds\n    __typename\n  }\n  actionKind\n  __typename\n}\n\nfragment FlussMessageEffect on MessageEffect {\n  __typename\n  kind\n  message\n}\n\nfragment FlussCustomReturnWidget on CustomReturnWidget {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChoiceAssignWidget on ChoiceAssignWidget {\n  __typename\n  kind\n  choices {\n    value\n    label\n    description\n    __typename\n  }\n}\n\nfragment StreamItem on StreamItem {\n  kind\n  label\n  __typename\n}\n\nfragment RetriableNode on RetriableNode {\n  retries\n  retryDelay\n  __typename\n}\n\nfragment FlussCustomEffect on CustomEffect {\n  __typename\n  kind\n  hook\n  ward\n}\n\nfragment FlussChildPort on Port {\n  __typename\n  kind\n  identifier\n  children {\n    ...FlussChildPortNested\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  nullable\n}\n\nfragment BaseGraphNode on GraphNode {\n  ...EvenBasierGraphNode\n  __typename\n  ins {\n    ...FlussPort\n    __typename\n  }\n  outs {\n    ...FlussPort\n    __typename\n  }\n  constants {\n    ...FlussPort\n    __typename\n  }\n  voids {\n    ...FlussPort\n    __typename\n  }\n  id\n  position {\n    x\n    y\n    __typename\n  }\n  parentNode\n  globalsMap\n  constantsMap\n  title\n  description\n  kind\n}\n\nfragment FlussChoiceReturnWidget on ChoiceReturnWidget {\n  __typename\n  choices {\n    label\n    value\n    description\n    __typename\n  }\n}\n\nfragment RekuestFilterActionNode on RekuestFilterActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  path\n}\n\nfragment FlussPort on Port {\n  __typename\n  key\n  label\n  nullable\n  description\n  effects {\n    kind\n    function\n    dependencies\n    ...FlussCustomEffect\n    ...FlussMessageEffect\n    __typename\n  }\n  assignWidget {\n    __typename\n    kind\n    ...FlussStringAssignWidget\n    ...FlussSearchAssignWidget\n    ...FlussSliderAssignWidget\n    ...FlussChoiceAssignWidget\n    ...FlussCustomAssignWidget\n  }\n  returnWidget {\n    __typename\n    kind\n    ...FlussCustomReturnWidget\n    ...FlussChoiceReturnWidget\n  }\n  kind\n  identifier\n  children {\n    ...FlussChildPort\n    __typename\n  }\n  default\n  nullable\n  validators {\n    ...Validator\n    __typename\n  }\n}\n\nfragment ArgNode on ArgNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment BaseGraphEdge on GraphEdge {\n  __typename\n  id\n  source\n  sourceHandle\n  target\n  targetHandle\n  kind\n  stream {\n    ...StreamItem\n    __typename\n  }\n}\n\nfragment ReactiveNode on ReactiveNode {\n  ...BaseGraphNode\n  __typename\n  implementation\n}\n\nfragment RekuestMapActionNode on RekuestMapActionNode {\n  ...BaseGraphNode\n  ...RetriableNode\n  ...AssignableNode\n  ...RekuestActionNode\n  __typename\n  hello\n}\n\nfragment ReturnNode on ReturnNode {\n  ...BaseGraphNode\n  __typename\n}\n\nfragment VanillaEdge on VanillaEdge {\n  ...BaseGraphEdge\n  label\n  __typename\n}\n\nfragment LoggingEdge on LoggingEdge {\n  ...BaseGraphEdge\n  level\n  __typename\n}\n\nfragment GlobalArg on GlobalArg {\n  key\n  port {\n    ...FlussPort\n    __typename\n  }\n  __typename\n}\n\nfragment GraphNode on GraphNode {\n  kind\n  ...RekuestFilterActionNode\n  ...RekuestMapActionNode\n  ...ReactiveNode\n  ...ArgNode\n  ...ReturnNode\n  __typename\n}\n\nfragment Graph on Graph {\n  nodes {\n    ...GraphNode\n    __typename\n  }\n  edges {\n    ...LoggingEdge\n    ...VanillaEdge\n    __typename\n  }\n  globals {\n    ...GlobalArg\n    __typename\n  }\n  __typename\n}\n\nfragment Flow on Flow {\n  __typename\n  id\n  graph {\n    ...Graph\n    __typename\n  }\n  title\n  description\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n}\n\nquery GetFlow($id: ID!) {\n  flow(id: $id) {\n    ...Flow\n    __typename\n  }\n}"


class FlowsQuery(BaseModel):
    """No documentation found for this operation."""

    flows: Tuple[ListFlow, ...]

    class Arguments(BaseModel):
        """Arguments for Flows"""

        limit: Optional[int] = Field(default=None)

    class Meta:
        """Meta class for Flows"""

        document = "fragment ListFlow on Flow {\n  id\n  title\n  createdAt\n  workspace {\n    id\n    __typename\n  }\n  __typename\n}\n\nquery Flows($limit: Int) {\n  flows(pagination: {limit: $limit}) {\n    ...ListFlow\n    __typename\n  }\n}"


class SearchFlowsQueryOptions(BaseModel):
    """Flow(id, created_at, workspace, creator, restrict, version, title, nodes, edges, graph, hash, description, brittle)"""

    typename: Literal["Flow"] = Field(alias="__typename", default="Flow", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchFlowsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[SearchFlowsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for SearchFlows"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        """Meta class for SearchFlows"""

        document = "query SearchFlows($search: String, $values: [ID!]) {\n  options: flows(filters: {search: $search, ids: $values}) {\n    value: id\n    label: title\n    __typename\n  }\n}"


async def acreate_run(
    flow: ID, snapshot_interval: int, assignation: ID, rath: Optional[FlussRath] = None
) -> CreateRunMutationCreaterun:
    """CreateRun
     Start a run on fluss

    Arguments:
        flow: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        snapshot_interval: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        assignation: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateRunMutationCreaterun
    """
    return (
        await aexecute(
            CreateRunMutation,
            {
                "input": {
                    "flow": flow,
                    "snapshotInterval": snapshot_interval,
                    "assignation": assignation,
                }
            },
            rath=rath,
        )
    ).create_run


def create_run(
    flow: ID, snapshot_interval: int, assignation: ID, rath: Optional[FlussRath] = None
) -> CreateRunMutationCreaterun:
    """CreateRun
     Start a run on fluss

    Arguments:
        flow: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        snapshot_interval: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        assignation: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateRunMutationCreaterun
    """
    return execute(
        CreateRunMutation,
        {
            "input": {
                "flow": flow,
                "snapshotInterval": snapshot_interval,
                "assignation": assignation,
            }
        },
        rath=rath,
    ).create_run


async def aclose_run(
    run: ID, rath: Optional[FlussRath] = None
) -> CloseRunMutationCloserun:
    """CloseRun
     Start a run on fluss

    Arguments:
        run (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CloseRunMutationCloserun
    """
    return (await aexecute(CloseRunMutation, {"run": run}, rath=rath)).close_run


def close_run(run: ID, rath: Optional[FlussRath] = None) -> CloseRunMutationCloserun:
    """CloseRun
     Start a run on fluss

    Arguments:
        run (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CloseRunMutationCloserun
    """
    return execute(CloseRunMutation, {"run": run}, rath=rath).close_run


async def asnapshot(
    run: ID, events: Iterable[ID], t: int, rath: Optional[FlussRath] = None
) -> SnapshotMutationSnapshot:
    """Snapshot
     Snapshot the current state on the fluss platform

    Arguments:
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        events: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        SnapshotMutationSnapshot
    """
    return (
        await aexecute(
            SnapshotMutation,
            {"input": {"run": run, "events": events, "t": t}},
            rath=rath,
        )
    ).snapshot


def snapshot(
    run: ID, events: Iterable[ID], t: int, rath: Optional[FlussRath] = None
) -> SnapshotMutationSnapshot:
    """Snapshot
     Snapshot the current state on the fluss platform

    Arguments:
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        events: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        SnapshotMutationSnapshot
    """
    return execute(
        SnapshotMutation, {"input": {"run": run, "events": events, "t": t}}, rath=rath
    ).snapshot


async def atrack(
    reference: str,
    t: int,
    kind: RunEventKind,
    run: ID,
    caused_by: Iterable[ID],
    value: Optional[EventValue] = None,
    message: Optional[str] = None,
    exception: Optional[str] = None,
    source: Optional[str] = None,
    handle: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> TrackMutationTrack:
    """Track
     Track a new event on the fluss platform

    Arguments:
        reference: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        kind: RunEventKind (required)
        value: The `ArrayLike` scalasr typsse represents a reference to a store previously created by the user n a datalayer
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        caused_by: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        message: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        exception: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        source: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        handle: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        TrackMutationTrack
    """
    return (
        await aexecute(
            TrackMutation,
            {
                "input": {
                    "reference": reference,
                    "t": t,
                    "kind": kind,
                    "value": value,
                    "run": run,
                    "causedBy": caused_by,
                    "message": message,
                    "exception": exception,
                    "source": source,
                    "handle": handle,
                }
            },
            rath=rath,
        )
    ).track


def track(
    reference: str,
    t: int,
    kind: RunEventKind,
    run: ID,
    caused_by: Iterable[ID],
    value: Optional[EventValue] = None,
    message: Optional[str] = None,
    exception: Optional[str] = None,
    source: Optional[str] = None,
    handle: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> TrackMutationTrack:
    """Track
     Track a new event on the fluss platform

    Arguments:
        reference: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required)
        kind: RunEventKind (required)
        value: The `ArrayLike` scalasr typsse represents a reference to a store previously created by the user n a datalayer
        run: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        caused_by: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        message: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        exception: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        source: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        handle: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        TrackMutationTrack
    """
    return execute(
        TrackMutation,
        {
            "input": {
                "reference": reference,
                "t": t,
                "kind": kind,
                "value": value,
                "run": run,
                "causedBy": caused_by,
                "message": message,
                "exception": exception,
                "source": source,
                "handle": handle,
            }
        },
        rath=rath,
    ).track


async def aupdate_workspace(
    workspace: ID,
    graph: GraphInput,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """UpdateWorkspace


    Arguments:
        workspace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        graph:  (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return (
        await aexecute(
            UpdateWorkspaceMutation,
            {
                "input": {
                    "workspace": workspace,
                    "graph": graph,
                    "title": title,
                    "description": description,
                }
            },
            rath=rath,
        )
    ).update_workspace


def update_workspace(
    workspace: ID,
    graph: GraphInput,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """UpdateWorkspace


    Arguments:
        workspace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        graph:  (required)
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return execute(
        UpdateWorkspaceMutation,
        {
            "input": {
                "workspace": workspace,
                "graph": graph,
                "title": title,
                "description": description,
            }
        },
        rath=rath,
    ).update_workspace


async def acreate_workspace(
    vanilla: bool,
    graph: Optional[GraphInput] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """CreateWorkspace


    Arguments:
        graph:
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vanilla: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return (
        await aexecute(
            CreateWorkspaceMutation,
            {
                "input": {
                    "graph": graph,
                    "title": title,
                    "description": description,
                    "vanilla": vanilla,
                }
            },
            rath=rath,
        )
    ).create_workspace


def create_workspace(
    vanilla: bool,
    graph: Optional[GraphInput] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[FlussRath] = None,
) -> Workspace:
    """CreateWorkspace


    Arguments:
        graph:
        title: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vanilla: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return execute(
        CreateWorkspaceMutation,
        {
            "input": {
                "graph": graph,
                "title": title,
                "description": description,
                "vanilla": vanilla,
            }
        },
        rath=rath,
    ).create_workspace


async def arun(id: ID, rath: Optional[FlussRath] = None) -> Run:
    """Run


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Run
    """
    return (await aexecute(RunQuery, {"id": id}, rath=rath)).run


def run(id: ID, rath: Optional[FlussRath] = None) -> Run:
    """Run


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Run
    """
    return execute(RunQuery, {"id": id}, rath=rath).run


async def asearch_runs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchRunsQueryOptions, ...]:
    """SearchRuns


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchRunsQueryRuns]
    """
    return (
        await aexecute(SearchRunsQuery, {"search": search, "values": values}, rath=rath)
    ).options


def search_runs(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchRunsQueryOptions, ...]:
    """SearchRuns


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchRunsQueryRuns]
    """
    return execute(
        SearchRunsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aworkspace(id: ID, rath: Optional[FlussRath] = None) -> Workspace:
    """Workspace


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return (await aexecute(WorkspaceQuery, {"id": id}, rath=rath)).workspace


def workspace(id: ID, rath: Optional[FlussRath] = None) -> Workspace:
    """Workspace


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Workspace
    """
    return execute(WorkspaceQuery, {"id": id}, rath=rath).workspace


async def aworkspaces(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListWorkspace, ...]:
    """Workspaces


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListWorkspace]
    """
    return (
        await aexecute(WorkspacesQuery, {"pagination": pagination}, rath=rath)
    ).workspaces


def workspaces(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListWorkspace, ...]:
    """Workspaces


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListWorkspace]
    """
    return execute(WorkspacesQuery, {"pagination": pagination}, rath=rath).workspaces


async def areactive_templates(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ReactiveTemplate, ...]:
    """ReactiveTemplates


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ReactiveTemplate]
    """
    return (
        await aexecute(ReactiveTemplatesQuery, {"pagination": pagination}, rath=rath)
    ).reactive_templates


def reactive_templates(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[FlussRath] = None
) -> Tuple[ReactiveTemplate, ...]:
    """ReactiveTemplates


    Arguments:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ReactiveTemplate]
    """
    return execute(
        ReactiveTemplatesQuery, {"pagination": pagination}, rath=rath
    ).reactive_templates


async def areactive_template(
    id: ID, rath: Optional[FlussRath] = None
) -> ReactiveTemplate:
    """ReactiveTemplate


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReactiveTemplate
    """
    return (
        await aexecute(ReactiveTemplateQuery, {"id": id}, rath=rath)
    ).reactive_template


def reactive_template(id: ID, rath: Optional[FlussRath] = None) -> ReactiveTemplate:
    """ReactiveTemplate


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ReactiveTemplate
    """
    return execute(ReactiveTemplateQuery, {"id": id}, rath=rath).reactive_template


async def aget_flow(id: ID, rath: Optional[FlussRath] = None) -> Flow:
    """GetFlow


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flow
    """
    return (await aexecute(GetFlowQuery, {"id": id}, rath=rath)).flow


def get_flow(id: ID, rath: Optional[FlussRath] = None) -> Flow:
    """GetFlow


    Arguments:
        id (ID): No description
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Flow
    """
    return execute(GetFlowQuery, {"id": id}, rath=rath).flow


async def aflows(
    limit: Optional[int] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListFlow, ...]:
    """Flows


    Arguments:
        limit (Optional[int], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListFlow]
    """
    return (await aexecute(FlowsQuery, {"limit": limit}, rath=rath)).flows


def flows(
    limit: Optional[int] = None, rath: Optional[FlussRath] = None
) -> Tuple[ListFlow, ...]:
    """Flows


    Arguments:
        limit (Optional[int], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListFlow]
    """
    return execute(FlowsQuery, {"limit": limit}, rath=rath).flows


async def asearch_flows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchFlowsQueryOptions, ...]:
    """SearchFlows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlowsQueryFlows]
    """
    return (
        await aexecute(
            SearchFlowsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_flows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[FlussRath] = None,
) -> Tuple[SearchFlowsQueryOptions, ...]:
    """SearchFlows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (fluss_next.rath.FlussRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[SearchFlowsQueryFlows]
    """
    return execute(
        SearchFlowsQuery, {"search": search, "values": values}, rath=rath
    ).options


AssignWidgetInput.model_rebuild()
GraphEdgeInput.model_rebuild()
GraphInput.model_rebuild()
GraphNodeInput.model_rebuild()
PortInput.model_rebuild()
UpdateWorkspaceInput.model_rebuild()
