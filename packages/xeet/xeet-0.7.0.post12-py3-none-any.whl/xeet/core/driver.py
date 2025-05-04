from functools import cache
from .test import Test, TestModel
from .resource import ResourceModel
from .matrix import MatrixModel
from . import TestsCriteria, RuntimeInfo
from .event_logger import EventLogger
from xeet.log import log_info, logging_enabled
from xeet.common import XeetException, NonEmptyStr, pydantic_errmsg, XeetVars, validate_token
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from typing import Any
from yaml import safe_load
from yaml.parser import ParserError as YamlParserError
from yaml.constructor import ConstructorError
from yaml.composer import ComposerError
from yaml.scanner import ScannerError
import re
import json
import os


_NAME = "name"
_GROUPS = "groups"
_ABSTRACT = "abstract"


class XeetModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    json_schema: str | None = Field(None, alias="$schema")
    includes: list[NonEmptyStr] = Field(default_factory=list, alias="include")
    tests: list[dict] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, dict] = Field(default_factory=dict)
    resources: dict[str, list[ResourceModel]] = Field(default_factory=dict)
    matrix: MatrixModel = Field(default_factory=dict)

    root_dir: str = Field(default_factory=str, exclude=True)
    tests_dict: dict[str, dict] = Field(default_factory=dict, alias="test_names", exclude=True)

    @model_validator(mode='after')
    def post_validate(self) -> "XeetModel":
        for t in self.tests:
            name = t.get(_NAME, "").strip()
            t[_NAME] = name  # Remove leading/trailing spaces
            if not name:
                continue
            if name in self.tests_dict:
                raise ValueError(f"Duplicate test name '{name}'")
            self.tests_dict[name] = t
        for s in self.settings.keys():
            if not validate_token(s):
                raise ValueError(f"Invalid setting name '{s}'")
        return self

    def include(self, other: "XeetModel") -> None:
        self.variables = {**other.variables, **self.variables}
        self.resources = {**other.resources, **self.resources}
        self.matrix = {**other.matrix, **self.matrix}
        other_tests = []
        for test in other.tests:
            name = test.get(_NAME)
            if not name or name in self.tests_dict:
                continue
            self.tests_dict[name] = test
            other_tests.append(test)
        self.tests = other_tests + self.tests
        for key, value in other.settings.items():
            if key in self.settings:
                self.settings[key] = {**value, **self.settings[key]}
            else:
                self.settings[key] = value


_TEST_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]*$")


class _Driver:
    def __init__(self, model: XeetModel, rti: RuntimeInfo) -> None:
        self.model = model
        self.rti = rti
        self.rti.xvars.set_vars(model.variables)
        self.tests_cache: dict[str, Test] = {}

        #  Check if any of the matrix names conflict with the existing variables
        colliding_keys = set(model.matrix.keys()) & set(self.rti.xvars.vars_map.keys())
        if colliding_keys:
            keys_str = ', '.join(colliding_keys)
            raise XeetException(f"Matrix names conflict with the existing variables: {keys_str}")

        #  Add matrix variables to the environment, with temporary values. The actual values will be
        #  set by the matrix module when the matrix is resolved, but for now we need to have them
        #  defined for information commands to show something meaningful.
        matrix_tmp_vars = {m: f"<matrix:{m}>" for m in model.matrix.keys()}
        self.rti.xvars.set_vars(matrix_tmp_vars)

        for name, resources in model.resources.items():
            self.rti.add_resource_pool(name, resources)

    def _test_model(self, desc: dict, inherited: set[str] | None = None) -> TestModel:
        if inherited is None:
            inherited = set()
        name = desc.get(_NAME)
        if not name:
            desc = {"name": "<Unknown>", "error": "Test has no name"}
            return TestModel(**desc)
        if not _TEST_NAME_PATTERN.match(name):
            desc = {"name": name, "error": f"Invalid test name '{name}'"}
            return TestModel(**desc)
        try:
            ret = TestModel(**desc)
        except ValidationError as e:
            err = pydantic_errmsg(e)
            desc = {"name": name, "error": err}
            return TestModel(**desc)

        base_name = ret.base
        if not base_name:
            return ret
        if base_name in inherited:
            desc = {"name": name, "error": f"Inheritance loop detected for '{base_name}'"}
            return TestModel(**desc)
        inherited.add(name)
        base_desc = self.test_desc(base_name)
        if not base_desc:
            desc = {"name": name, "error": f"No such base test '{base_name}'"}
            return TestModel(**desc)
        base_model = self._test_model(base_desc, inherited)
        if base_model.error:
            ret.error = f"Base test '{base_name}' error: {base_model.error}"
            return ret
        ret.inherit(base_model)
        return ret

    def _test(self, desc: dict) -> Test:
        if desc[_NAME] not in self.tests_cache:
            model = self._test_model(desc)
            self.tests_cache[desc[_NAME]] = Test(model, self.rti)
        return self.tests_cache[desc[_NAME]]

    def get_test(self, name: str) -> Test | None:
        if name in self.tests_cache:
            return self.tests_cache[name]
        desc = self.test_desc(name)
        if not desc:
            log_info(f"Test '{name}' not found")
            return None
        return self._test(desc)

    def get_tests(self, criteria: TestsCriteria) -> list[Test]:
        return [self._test(desc) for desc in self.model.tests
                if criteria.match(desc.get(_NAME, ""),
                                  desc.get(_GROUPS, []), desc.get(_ABSTRACT, False))]

    def test_desc(self, name: str) -> dict | None:
        return self.model.tests_dict.get(name, None)

    def all_groups(self) -> set[str]:
        ret = set()
        for desc in self.model.tests:
            ret.update(desc.get(_GROUPS, []))
        return ret


class XeetConfigException(XeetException):
    ...


class XeetIncludeLoopException(XeetConfigException):
    def __init__(self, file_path: str) -> None:
        super().__init__(f"Include loop detected - '{file_path}'")


def _read_conf_file(file_path: str,
                    xvars: XeetVars,
                    root_dir: str,
                    included: set[str] | None = None) -> XeetModel:
    if included is None:
        included = set()

    file_path = xvars.expand(file_path)
    if not os.path.isabs(file_path):
        file_path = os.path.join(root_dir, file_path)

    if file_path in included:
        raise XeetIncludeLoopException(file_path)

    file_suffix = os.path.splitext(file_path)[1]
    log_info(f"reading configuration file '{file_path}'")
    try:
        with open(file_path, 'r') as f:
            if file_suffix == ".yaml" or file_suffix == ".yml":
                desc = safe_load(f)
            else:
                desc = json.load(f)
            model = XeetModel(**desc)
            model.root_dir = root_dir
    except ValidationError as e:
        raise XeetConfigException(f"Error parsing {file_path} - {pydantic_errmsg(e)}")
    except (IOError, TypeError, ValueError, YamlParserError, ConstructorError,
            ComposerError, ScannerError) as e:
        raise XeetConfigException(f"Error parsing {file_path} - {e}")

    included.add(file_path)
    if model.includes:
        includes = [r.root for r in model.includes]
        log_info(f"reading included files: {', '.join(includes)}")
        for i in includes[::-1]:
            inc_model = _read_conf_file(i, xvars, root_dir, included)
            model.include(inc_model)
    included.remove(file_path)

    return model


# Use _xeet_init function for caching as default arguments mess up the cache decorator.
@cache
def _xeet_init(file_path: str, debug_mode: bool) -> _Driver:
    if not file_path:
        for file in ("xeet.yaml", "xeet.yml", "xeet.json"):
            if os.path.exists(file):
                file_path = file
                break
        if not file_path:
            raise XeetConfigException("Empty configuration file path")

    rti = RuntimeInfo(file_path, debug_mode)
    if logging_enabled():
        rti.add_run_reporter(EventLogger())
    model = _read_conf_file(rti.xeet_file_path, rti.xvars, rti.root_dir)
    rti.set_defs(model.model_dump(by_alias=True))
    rti.notifier.on_init()
    ret = _Driver(model, rti)
    return ret


def xeet_init(file_path: str, debug_mode: bool = False) -> _Driver:
    return _xeet_init(file_path, debug_mode)


def clear_drivers_cache() -> None:
    _xeet_init.cache_clear()
