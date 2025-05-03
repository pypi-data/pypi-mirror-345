import json

import pytest
from pydantic import ValidationError

from climate_ref_core.pycmec.metric import (
    CMECMetric,
    MetricDimensions,
    MetricResults,
)


@pytest.fixture(params=["dict", "CMECMetric"])
def cmec_right_metric_data(request, cmec_right_metric_dict):
    if request.param == "dict":
        return cmec_right_metric_dict
    elif request.param == "CMECMetric":
        return CMECMetric(**cmec_right_metric_dict)


@pytest.fixture(params=["dict", "MetricDimensions"])
def cmec_right_dimen_data(request, cmec_right_metric_dict):
    if request.param == "dict":
        return cmec_right_metric_dict["DIMENSIONS"]
    elif request.param == "MetricDimensions":
        return MetricDimensions(**cmec_right_metric_dict["DIMENSIONS"])


@pytest.fixture
def cmec_right_result_dimobj(cmec_right_metric_dict):
    return cmec_right_metric_dict["RESULTS"], MetricDimensions(**cmec_right_metric_dict["DIMENSIONS"])


@pytest.fixture
def cmec_wrongkw_metric_dict(cmec_right_metric_dict):
    return {
        "DIMENSIONS": {
            "xJSON": cmec_right_metric_dict["DIMENSIONS"]["json_structure"],
            "xmodel": cmec_right_metric_dict["DIMENSIONS"]["model"],
            "xmetric": cmec_right_metric_dict["DIMENSIONS"]["metric"],
        },
        "RESULTS": cmec_right_metric_dict["RESULTS"],
    }


@pytest.fixture
def cmec_wrongattr_metric_dict(cmec_right_metric_dict):
    return {
        "xDIMENSIONS": cmec_right_metric_dict["DIMENSIONS"],
        "xRESULTS": cmec_right_metric_dict["RESULTS"],
    }


@pytest.fixture
def cmec_wrongdim_metric_dict(cmec_right_metric_dict):
    cmec_right_metric_dict["DIMENSIONS"]["json_structure"] = ["model"]
    return cmec_right_metric_dict


def test_metric_missing_deepest_dimension(cmec_right_metric_dict):
    cmec_metric = cmec_right_metric_dict
    cmec_metric["DIMENSIONS"]["json_structure"] = cmec_right_metric_dict["DIMENSIONS"]["json_structure"][:-1]
    cmec_metric["DIMENSIONS"].pop("statistic")
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_metric)


def test_metric_missing_deepest_dimension_key(cmec_right_metric_dict):
    cmec_metric = cmec_right_metric_dict
    cmec_metric["RESULTS"]["E3SM"]["Hydrology Cycle"].pop("rmse")
    CMECMetric(**cmec_metric)

    cmec_metric["RESULTS"]["E3SM"]["Hydrology Cycle"]["unknown"] = 0.0
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_metric)


def test_metric_right(cmec_right_metric_data):
    CMECMetric.model_validate(cmec_right_metric_data)


def test_metric_right_init(cmec_right_metric_dict):
    CMECMetric(**cmec_right_metric_dict)


def test_dimen_right(cmec_right_dimen_data):
    MetricDimensions.model_validate(cmec_right_dimen_data)


def test_metric_wrongkm(cmec_wrongkw_metric_dict):
    with pytest.raises(ValidationError):
        CMECMetric.model_validate(cmec_wrongkw_metric_dict)
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_wrongkw_metric_dict)


def test_metric_wrongattr(cmec_wrongattr_metric_dict):
    with pytest.raises(ValidationError):
        CMECMetric.model_validate(cmec_wrongattr_metric_dict)
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_wrongattr_metric_dict)


def test_metric_wrongdim(cmec_wrongdim_metric_dict):
    with pytest.raises(ValidationError):
        CMECMetric.model_validate(cmec_wrongdim_metric_dict)
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_wrongdim_metric_dict)


def test_dimen_wrongdim(cmec_wrongdim_metric_dict):
    with pytest.raises(ValidationError):
        MetricDimensions.model_validate(cmec_wrongdim_metric_dict["DIMENSIONS"])
    with pytest.raises(ValidationError):
        MetricDimensions(DIMENSIONS=cmec_wrongdim_metric_dict["DIMENSIONS"])


@pytest.mark.parametrize(
    "dim_name,dim_dict",
    [
        ("model", {"BCC-CSM2-MR": {"name": "BCC-CSM2-MR"}}),
        (
            "metric",
            {
                "Hydrology Cycle::Sensible Heat!!FLUXNET2015": {
                    "Name": "Hydrology Cycle::Latent Heat!!FLUXNET2015",
                    "Abstract": "benchmark score",
                    "URI": ["https://www.osti.gov/biblio/1330803"],
                }
            },
        ),
    ],
)
def test_add_dimensions_exist_dimen(cmec_right_dimen_data, dim_name, dim_dict):
    if isinstance(cmec_right_dimen_data, MetricDimensions):
        cmec_dims = cmec_right_dimen_data
    else:
        cmec_dims = MetricDimensions(cmec_right_dimen_data)

    js_struct_old = cmec_dims.root["json_structure"]
    cmec_dims.add_dimension(dim_name, dim_dict)
    js_struct_new = cmec_dims.root["json_structure"]

    assert js_struct_old == js_struct_new

    if dim_name == "model":
        assert cmec_dims.root["model"]["BCC-CSM2-MR"] == {"name": "BCC-CSM2-MR"}
    if dim_name == "metric":
        assert cmec_dims.root["metric"]["Hydrology Cycle::Sensible Heat!!FLUXNET2015"] == {
            "Name": "Hydrology Cycle::Latent Heat!!FLUXNET2015",
            "Abstract": "benchmark score",
            "URI": ["https://www.osti.gov/biblio/1330803"],
        }


def test_add_dimensions_new_dimen(cmec_right_dimen_data):
    if isinstance(cmec_right_dimen_data, MetricDimensions):
        cmec_dims = cmec_right_dimen_data
    else:
        cmec_dims = MetricDimensions(cmec_right_dimen_data)

    cmec_dims.add_dimension("region", {"global": {"title": "global"}, "NA": {"title": "North America"}})

    assert "region" in cmec_dims.root["json_structure"]

    assert cmec_dims.root["region"] == {
        "global": {"title": "global"},
        "NA": {"title": "North America"},
    }


def test_metric_otherdicts(cmec_right_metric_dict):
    cmec_right_metric_dict["otherdict1"] = {}
    cmec_right_metric_dict["otherdict2"] = {}

    CMECMetric(**cmec_right_metric_dict)


def test_metric_attributes_each_level(cmec_right_metric_dict):
    cmec_right_metric_dict["RESULTS"]["E3SM"]["attributes"] = "some information for model level"

    CMECMetric(**cmec_right_metric_dict)


def test_metric_attributes_in_results(cmec_right_metric_dict):
    cmec_right_metric_dict["RESULTS"]["attributes"] = "some information for executions level"

    with pytest.raises(ValidationError):
        CMECMetric(**cmec_right_metric_dict)


def test_validate_result_wo_dim(cmec_right_metric_dict):
    with pytest.raises(ValidationError):
        MetricResults(cmec_right_metric_dict["RESULTS"])


def test_metric_deepest_dictionary_value(cmec_right_metric_dict):
    cmec_right_metric_dict["RESULTS"]["CESM2"]["Ecosystem and Carbon Cycle"]["overall score"] = {
        "value": 0.11,
    }
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_right_metric_dict)

    cmec_right_metric_dict["RESULTS"]["CESM2"]["Ecosystem and Carbon Cycle"]["overall score"] = "best"
    with pytest.raises(ValidationError):
        CMECMetric(**cmec_right_metric_dict)


def test_metric_mismatch_dimension_key(cmec_right_metric_dict):
    cmec_right_metric_dict["RESULTS"]["unknow_model"] = cmec_right_metric_dict["RESULTS"]["CESM2"]

    with pytest.raises(ValidationError):
        CMECMetric(**cmec_right_metric_dict)


def test_metric_nested_dict(cmec_right_metric_dict):
    cmec_right_metric_dict["RESULTS"]["CESM2"]["Ecosystem and Carbon Cycle"] = 1.0

    with pytest.raises(ValidationError):
        CMECMetric(**cmec_right_metric_dict)


def test_metric_merge():
    dict_pmp = {
        "DIMENSIONS": {
            "json_structure": ["model", "metric"],
            "model": {"GFDL-ESM2M": {"Source": "CMIP5 ESGF"}},
            "metric": {
                "NinoSstDiversity_2": {"Name": "NinoSstDiversity_2"},
                "BiasTauxLonRmse": {"name": "BiasTauxLonRmse"},
            },
        },
        "RESULTS": {
            "GFDL-ESM2M": {
                "NinoSstDiversity_2": -75,
                "BiasTauxLonRmse": 5.959564210237568,
                "attributes": {
                    "NinoSstDiversity_2": "Nino SST diversity",
                    "BiasTauxLonRmse": "Bias Taux RMSE",
                },
            },
            "attributes": {
                "package": "pmp",
                "NinoSstDiversity_2": {},
            },
        },
    }
    dict_ilamb = {
        "DIMENSIONS": {
            "json_structure": ["model", "metric"],
            "model": {
                "E3SM": {"name": "E3SM"},
                "CESM": {"name": "CESM"},
                "GFDL-ESM2M": {"name": "GFDL-ESM2M"},
            },
            "metric": {"carbon": {"name": "carbon"}},
        },
        "RESULTS": {
            "E3SM": {
                "carbon": 0.11,
                "attributes": {
                    "score": "ILAMB scoring system",
                },
            },
            "CESM": {
                "carbon": 0.05,
            },
            "GFDL-ESM2M": {
                "carbon": 0.35,
                "attributes": {
                    "score": "ILAMB scoring system",
                },
            },
            "attributes": {
                "package": "ilamb",
                "overall score": {},
            },
        },
    }

    dict_merged = {
        "DIMENSIONS": {
            "json_structure": ["model", "metric"],
            "model": {
                "GFDL-ESM2M": {"Source": "CMIP5 ESGF"},
                "E3SM": {"name": "E3SM"},
                "CESM": {"name": "CESM"},
            },
            "metric": {
                "NinoSstDiversity_2": {"Name": "NinoSstDiversity_2"},
                "BiasTauxLonRmse": {"name": "BiasTauxLonRmse"},
                "carbon": {"name": "carbon"},
            },
        },
        "RESULTS": {
            "E3SM": {
                "carbon": 0.11,
                "attributes": {
                    "score": "ILAMB scoring system",
                },
            },
            "CESM": {
                "carbon": 0.05,
            },
            "GFDL-ESM2M": {
                "NinoSstDiversity_2": -75,
                "BiasTauxLonRmse": 5.959564210237568,
                "attributes": {
                    "NinoSstDiversity_2": "Nino SST diversity",
                    "BiasTauxLonRmse": "Bias Taux RMSE",
                    "score": "ILAMB scoring system",
                },
                "carbon": 0.35,
            },
            "attributes": {
                "package": "ilamb",
                "NinoSstDiversity_2": {},
                "overall score": {},
            },
        },
        "PROVENANCE": None,
        "DISCLAIMER": None,
        "NOTES": None,
    }

    assert json.loads(CMECMetric.merge(dict_pmp, dict_ilamb).model_dump_json(indent=2)) == dict_merged

    mdim_pmp = dict_pmp["DIMENSIONS"]
    mdim_ilamb = dict_ilamb["DIMENSIONS"]

    mdim_ilamb["json_structure"] = ["model"]
    mdim_ilamb.pop("metric")

    with pytest.raises(ValueError):
        MetricDimensions.merge_dimension(mdim_pmp, mdim_ilamb)


def test_metric_create_template():
    assert CMECMetric.create_template() == {
        "DIMENSIONS": {"json_structure": ["model", "metric"], "metric": {}, "model": {}},
        "RESULTS": {},
        "DISCLAIMER": None,
        "NOTES": None,
        "PROVENANCE": None,
    }


def test_metric_load_from_jsons(datadir):
    assert CMECMetric.load_from_json(datadir / "cmec_metric_sample.json")


def test_metric_json_schema(data_regression):
    from climate_ref_core.pycmec.metric import CMECGenerateJsonSchema

    cmec_model_schema = CMECMetric.model_json_schema(schema_generator=CMECGenerateJsonSchema)

    data_regression.check(cmec_model_schema)
