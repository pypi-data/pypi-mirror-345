# Auto generated from omni_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-09-11T19:13:36
# Schema: omni-schema
#
# id: https://w3id.org/omnibenchmark/omni-schema
# description: Data model for omnibenchmark.
# license: Apache Software License 2.0

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from datetime import date, datetime, time
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String, Uriorcurie
from linkml_runtime.utils.metamodelcore import URIorCURIE

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
EXAMPLE = CurieNamespace('example', 'https://example.org/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OMNI_SCHEMA = CurieNamespace('omni_schema', 'https://w3id.org/omnibenchmark/omni-schema/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = OMNI_SCHEMA


# Types

# Class references
class IdentifiableEntityId(URIorCURIE):
    pass


class BenchmarkId(IdentifiableEntityId):
    pass


class StageId(IdentifiableEntityId):
    pass


class ModuleId(IdentifiableEntityId):
    pass


class IOFileId(IdentifiableEntityId):
    pass


class SoftwareEnvironmentId(IdentifiableEntityId):
    pass


@dataclass(repr=False)
class IdentifiableEntity(YAMLRoot):
    """
    A generic grouping for any identifiable entity
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["Thing"]
    class_class_curie: ClassVar[str] = "schema:Thing"
    class_name: ClassVar[str] = "IdentifiableEntity"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.IdentifiableEntity

    id: Union[str, IdentifiableEntityId] = None
    name: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, IdentifiableEntityId):
            self.id = IdentifiableEntityId(self.id)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Benchmark(IdentifiableEntity):
    """
    A multi-stage workflow to evaluate processing stage for a specific task.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["Benchmark"]
    class_class_curie: ClassVar[str] = "omni_schema:Benchmark"
    class_name: ClassVar[str] = "Benchmark"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.Benchmark

    id: Union[str, BenchmarkId] = None
    version: str = None
    benchmarker: str = None
    software_backend: Union[str, "SoftwareBackendEnum"] = None
    storage: str = None
    storage_api: Union[str, "StorageAPIEnum"] = None
    storage_bucket_name: str = None
    software_environments: Union[Dict[Union[str, SoftwareEnvironmentId], Union[dict, "SoftwareEnvironment"]], List[Union[dict, "SoftwareEnvironment"]]] = empty_dict()
    stages: Union[Dict[Union[str, StageId], Union[dict, "Stage"]], List[Union[dict, "Stage"]]] = empty_dict()
    benchmark_yaml_spec: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, BenchmarkId):
            self.id = BenchmarkId(self.id)

        if self._is_empty(self.version):
            self.MissingRequiredField("version")
        if not isinstance(self.version, str):
            self.version = str(self.version)

        if self._is_empty(self.benchmarker):
            self.MissingRequiredField("benchmarker")
        if not isinstance(self.benchmarker, str):
            self.benchmarker = str(self.benchmarker)

        if self._is_empty(self.software_backend):
            self.MissingRequiredField("software_backend")
        if not isinstance(self.software_backend, SoftwareBackendEnum):
            self.software_backend = SoftwareBackendEnum(self.software_backend)

        if self._is_empty(self.storage):
            self.MissingRequiredField("storage")
        if not isinstance(self.storage, str):
            self.storage = str(self.storage)

        if self._is_empty(self.storage_api):
            self.MissingRequiredField("storage_api")
        if not isinstance(self.storage_api, StorageAPIEnum):
            self.storage_api = StorageAPIEnum(self.storage_api)

        if self._is_empty(self.storage_bucket_name):
            self.MissingRequiredField("storage_bucket_name")
        if not isinstance(self.storage_bucket_name, str):
            self.storage_bucket_name = str(self.storage_bucket_name)

        if self._is_empty(self.software_environments):
            self.MissingRequiredField("software_environments")
        self._normalize_inlined_as_list(slot_name="software_environments", slot_type=SoftwareEnvironment, key_name="id", keyed=True)

        if self._is_empty(self.stages):
            self.MissingRequiredField("stages")
        self._normalize_inlined_as_list(slot_name="stages", slot_type=Stage, key_name="id", keyed=True)

        if self.benchmark_yaml_spec is not None and not isinstance(self.benchmark_yaml_spec, str):
            self.benchmark_yaml_spec = str(self.benchmark_yaml_spec)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Stage(IdentifiableEntity):
    """
    A benchmark subtask with equivalent and independent modules.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["Stage"]
    class_class_curie: ClassVar[str] = "omni_schema:Stage"
    class_name: ClassVar[str] = "Stage"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.Stage

    id: Union[str, StageId] = None
    modules: Union[Dict[Union[str, ModuleId], Union[dict, "Module"]], List[Union[dict, "Module"]]] = empty_dict()
    inputs: Optional[Union[Union[dict, "InputCollection"], List[Union[dict, "InputCollection"]]]] = empty_list()
    outputs: Optional[Union[Dict[Union[str, IOFileId], Union[dict, "IOFile"]], List[Union[dict, "IOFile"]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, StageId):
            self.id = StageId(self.id)

        if self._is_empty(self.modules):
            self.MissingRequiredField("modules")
        self._normalize_inlined_as_list(slot_name="modules", slot_type=Module, key_name="id", keyed=True)

        if not isinstance(self.inputs, list):
            self.inputs = [self.inputs] if self.inputs is not None else []
        self.inputs = [v if isinstance(v, InputCollection) else InputCollection(**as_dict(v)) for v in self.inputs]

        self._normalize_inlined_as_list(slot_name="outputs", slot_type=IOFile, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Module(IdentifiableEntity):
    """
    A single benchmark component assigned to a specific stage.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["Module"]
    class_class_curie: ClassVar[str] = "omni_schema:Module"
    class_name: ClassVar[str] = "Module"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.Module

    id: Union[str, ModuleId] = None
    software_environment: Union[str, SoftwareEnvironmentId] = None
    repository: Union[dict, "Repository"] = None
    exclude: Optional[Union[Union[str, ModuleId], List[Union[str, ModuleId]]]] = empty_list()
    parameters: Optional[Union[Union[dict, "Parameter"], List[Union[dict, "Parameter"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ModuleId):
            self.id = ModuleId(self.id)

        if self._is_empty(self.software_environment):
            self.MissingRequiredField("software_environment")
        if not isinstance(self.software_environment, SoftwareEnvironmentId):
            self.software_environment = SoftwareEnvironmentId(self.software_environment)

        if self._is_empty(self.repository):
            self.MissingRequiredField("repository")
        if not isinstance(self.repository, Repository):
            self.repository = Repository(**as_dict(self.repository))

        if not isinstance(self.exclude, list):
            self.exclude = [self.exclude] if self.exclude is not None else []
        self.exclude = [v if isinstance(v, ModuleId) else ModuleId(v) for v in self.exclude]

        if not isinstance(self.parameters, list):
            self.parameters = [self.parameters] if self.parameters is not None else []
        self.parameters = [v if isinstance(v, Parameter) else Parameter(**as_dict(v)) for v in self.parameters]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class IOFile(IdentifiableEntity):
    """
    Represents an input / output file.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["IOFile"]
    class_class_curie: ClassVar[str] = "omni_schema:IOFile"
    class_name: ClassVar[str] = "IOFile"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.IOFile

    id: Union[str, IOFileId] = None
    path: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, IOFileId):
            self.id = IOFileId(self.id)

        if self.path is not None and not isinstance(self.path, str):
            self.path = str(self.path)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class InputCollection(YAMLRoot):
    """
    A holder for valid input combinations.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["InputCollection"]
    class_class_curie: ClassVar[str] = "omni_schema:InputCollection"
    class_name: ClassVar[str] = "InputCollection"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.InputCollection

    entries: Optional[Union[Union[str, IOFileId], List[Union[str, IOFileId]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.entries, list):
            self.entries = [self.entries] if self.entries is not None else []
        self.entries = [v if isinstance(v, IOFileId) else IOFileId(v) for v in self.entries]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Repository(YAMLRoot):
    """
    A reference to code repository containing the module's executable code.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["Repository"]
    class_class_curie: ClassVar[str] = "omni_schema:Repository"
    class_name: ClassVar[str] = "Repository"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.Repository

    url: str = None
    commit: str = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.url):
            self.MissingRequiredField("url")
        if not isinstance(self.url, str):
            self.url = str(self.url)

        if self._is_empty(self.commit):
            self.MissingRequiredField("commit")
        if not isinstance(self.commit, str):
            self.commit = str(self.commit)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Parameter(YAMLRoot):
    """
    A parameter and its scope.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["Parameter"]
    class_class_curie: ClassVar[str] = "omni_schema:Parameter"
    class_name: ClassVar[str] = "Parameter"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.Parameter

    values: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.values, list):
            self.values = [self.values] if self.values is not None else []
        self.values = [v if isinstance(v, str) else str(v) for v in self.values]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SoftwareEnvironment(IdentifiableEntity):
    """
    Contains snapshots of the software environment required for the modules to run.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OMNI_SCHEMA["SoftwareEnvironment"]
    class_class_curie: ClassVar[str] = "omni_schema:SoftwareEnvironment"
    class_name: ClassVar[str] = "SoftwareEnvironment"
    class_model_uri: ClassVar[URIRef] = OMNI_SCHEMA.SoftwareEnvironment

    id: Union[str, SoftwareEnvironmentId] = None
    easyconfig: Optional[str] = None
    envmodule: Optional[str] = None
    conda: Optional[str] = None
    apptainer: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, SoftwareEnvironmentId):
            self.id = SoftwareEnvironmentId(self.id)

        if self.easyconfig is not None and not isinstance(self.easyconfig, str):
            self.easyconfig = str(self.easyconfig)

        if self.envmodule is not None and not isinstance(self.envmodule, str):
            self.envmodule = str(self.envmodule)

        if self.conda is not None and not isinstance(self.conda, str):
            self.conda = str(self.conda)

        if self.apptainer is not None and not isinstance(self.apptainer, str):
            self.apptainer = str(self.apptainer)

        super().__post_init__(**kwargs)


# Enumerations
class StorageAPIEnum(EnumDefinitionImpl):

    S3 = PermissibleValue(text="S3")

    _defn = EnumDefinition(
        name="StorageAPIEnum",
    )

class SoftwareBackendEnum(EnumDefinitionImpl):

    apptainer = PermissibleValue(text="apptainer")
    envmodules = PermissibleValue(text="envmodules")
    conda = PermissibleValue(text="conda")
    docker = PermissibleValue(text="docker")
    host = PermissibleValue(text="host")

    _defn = EnumDefinition(
        name="SoftwareBackendEnum",
    )

# Slots
class slots:
    pass

slots.id = Slot(uri=SCHEMA.identifier, name="id", curie=SCHEMA.curie('identifier'),
                   model_uri=OMNI_SCHEMA.id, domain=None, range=URIRef)

slots.name = Slot(uri=SCHEMA.name, name="name", curie=SCHEMA.curie('name'),
                   model_uri=OMNI_SCHEMA.name, domain=None, range=Optional[str])

slots.description = Slot(uri=SCHEMA.description, name="description", curie=SCHEMA.curie('description'),
                   model_uri=OMNI_SCHEMA.description, domain=None, range=Optional[str])

slots.version = Slot(uri=OMNI_SCHEMA.version, name="version", curie=OMNI_SCHEMA.curie('version'),
                   model_uri=OMNI_SCHEMA.version, domain=None, range=str)

slots.benchmarker = Slot(uri=OMNI_SCHEMA.benchmarker, name="benchmarker", curie=OMNI_SCHEMA.curie('benchmarker'),
                   model_uri=OMNI_SCHEMA.benchmarker, domain=None, range=str)

slots.software_backend = Slot(uri=OMNI_SCHEMA.software_backend, name="software_backend", curie=OMNI_SCHEMA.curie('software_backend'),
                   model_uri=OMNI_SCHEMA.software_backend, domain=None, range=Union[str, "SoftwareBackendEnum"])

slots.storage = Slot(uri=OMNI_SCHEMA.storage, name="storage", curie=OMNI_SCHEMA.curie('storage'),
                   model_uri=OMNI_SCHEMA.storage, domain=None, range=str)

slots.storage_api = Slot(uri=OMNI_SCHEMA.storage_api, name="storage_api", curie=OMNI_SCHEMA.curie('storage_api'),
                   model_uri=OMNI_SCHEMA.storage_api, domain=None, range=Union[str, "StorageAPIEnum"])

slots.storage_bucket_name = Slot(uri=OMNI_SCHEMA.storage_bucket_name, name="storage_bucket_name", curie=OMNI_SCHEMA.curie('storage_bucket_name'),
                   model_uri=OMNI_SCHEMA.storage_bucket_name, domain=None, range=str)

slots.stages = Slot(uri=OMNI_SCHEMA.stages, name="stages", curie=OMNI_SCHEMA.curie('stages'),
                   model_uri=OMNI_SCHEMA.stages, domain=None, range=Union[Dict[Union[str, StageId], Union[dict, Stage]], List[Union[dict, Stage]]])

slots.modules = Slot(uri=OMNI_SCHEMA.modules, name="modules", curie=OMNI_SCHEMA.curie('modules'),
                   model_uri=OMNI_SCHEMA.modules, domain=None, range=Union[Dict[Union[str, ModuleId], Union[dict, Module]], List[Union[dict, Module]]])

slots.inputs = Slot(uri=OMNI_SCHEMA.inputs, name="inputs", curie=OMNI_SCHEMA.curie('inputs'),
                   model_uri=OMNI_SCHEMA.inputs, domain=None, range=Optional[Union[Union[dict, InputCollection], List[Union[dict, InputCollection]]]])

slots.outputs = Slot(uri=OMNI_SCHEMA.outputs, name="outputs", curie=OMNI_SCHEMA.curie('outputs'),
                   model_uri=OMNI_SCHEMA.outputs, domain=None, range=Optional[Union[Dict[Union[str, IOFileId], Union[dict, IOFile]], List[Union[dict, IOFile]]]])

slots.exclude = Slot(uri=OMNI_SCHEMA.exclude, name="exclude", curie=OMNI_SCHEMA.curie('exclude'),
                   model_uri=OMNI_SCHEMA.exclude, domain=None, range=Optional[Union[Union[str, ModuleId], List[Union[str, ModuleId]]]])

slots.repository = Slot(uri=OMNI_SCHEMA.repository, name="repository", curie=OMNI_SCHEMA.curie('repository'),
                   model_uri=OMNI_SCHEMA.repository, domain=None, range=Union[dict, Repository])

slots.parameters = Slot(uri=OMNI_SCHEMA.parameters, name="parameters", curie=OMNI_SCHEMA.curie('parameters'),
                   model_uri=OMNI_SCHEMA.parameters, domain=None, range=Optional[Union[Union[dict, Parameter], List[Union[dict, Parameter]]]])

slots.software_environments = Slot(uri=OMNI_SCHEMA.software_environments, name="software_environments", curie=OMNI_SCHEMA.curie('software_environments'),
                   model_uri=OMNI_SCHEMA.software_environments, domain=None, range=Union[Dict[Union[str, SoftwareEnvironmentId], Union[dict, SoftwareEnvironment]], List[Union[dict, SoftwareEnvironment]]])

slots.software_environment = Slot(uri=OMNI_SCHEMA.software_environment, name="software_environment", curie=OMNI_SCHEMA.curie('software_environment'),
                   model_uri=OMNI_SCHEMA.software_environment, domain=None, range=Union[str, SoftwareEnvironmentId])

slots.path = Slot(uri=OMNI_SCHEMA.path, name="path", curie=OMNI_SCHEMA.curie('path'),
                   model_uri=OMNI_SCHEMA.path, domain=None, range=Optional[str])

slots.url = Slot(uri=OMNI_SCHEMA.url, name="url", curie=OMNI_SCHEMA.curie('url'),
                   model_uri=OMNI_SCHEMA.url, domain=None, range=str)

slots.commit = Slot(uri=OMNI_SCHEMA.commit, name="commit", curie=OMNI_SCHEMA.curie('commit'),
                   model_uri=OMNI_SCHEMA.commit, domain=None, range=str)

slots.values = Slot(uri=OMNI_SCHEMA.values, name="values", curie=OMNI_SCHEMA.curie('values'),
                   model_uri=OMNI_SCHEMA.values, domain=None, range=Optional[Union[str, List[str]]])

slots.entries = Slot(uri=OMNI_SCHEMA.entries, name="entries", curie=OMNI_SCHEMA.curie('entries'),
                   model_uri=OMNI_SCHEMA.entries, domain=None, range=Optional[Union[Union[str, IOFileId], List[Union[str, IOFileId]]]])

slots.easyconfig = Slot(uri=OMNI_SCHEMA.easyconfig, name="easyconfig", curie=OMNI_SCHEMA.curie('easyconfig'),
                   model_uri=OMNI_SCHEMA.easyconfig, domain=None, range=Optional[str])

slots.envmodule = Slot(uri=OMNI_SCHEMA.envmodule, name="envmodule", curie=OMNI_SCHEMA.curie('envmodule'),
                   model_uri=OMNI_SCHEMA.envmodule, domain=None, range=Optional[str])

slots.conda = Slot(uri=OMNI_SCHEMA.conda, name="conda", curie=OMNI_SCHEMA.curie('conda'),
                   model_uri=OMNI_SCHEMA.conda, domain=None, range=Optional[str])

slots.apptainer = Slot(uri=OMNI_SCHEMA.apptainer, name="apptainer", curie=OMNI_SCHEMA.curie('apptainer'),
                   model_uri=OMNI_SCHEMA.apptainer, domain=None, range=Optional[str])

slots.benchmark_yaml_spec = Slot(uri=OMNI_SCHEMA.benchmark_yaml_spec, name="benchmark_yaml_spec", curie=OMNI_SCHEMA.curie('benchmark_yaml_spec'),
                   model_uri=OMNI_SCHEMA.benchmark_yaml_spec, domain=None, range=Optional[str])