"""Tests for the Part 2 (CRS), Part 3 (Filtering) and Part 4 (Transactions) models."""

import pytest
from pydantic import ValidationError

from pydantic_ogcapi import (
    CRS84,
    QUERYABLES_SCHEMA_DIALECT,
    ConditionalHeaders,
    CrsParameters,
    FilterLang,
    FilterParameters,
    Function,
    Functions,
    Queryable,
    Queryables,
    QueryableType,
    TransactionResponse,
    TransactionStatus,
    format_content_crs,
    parse_content_crs,
)


class TestCrs:
    def test_bbox_crs_uses_kebab_case_alias(self):
        params = CrsParameters(crs=CRS84, bbox_crs=CRS84)
        assert params.model_dump()["bbox-crs"] == CRS84

    def test_parses_kebab_case_input(self):
        assert CrsParameters.model_validate({"bbox-crs": CRS84}).bbox_crs == CRS84

    def test_content_crs_header_round_trip(self):
        header = format_content_crs(CRS84)
        assert header == f"<{CRS84}>"
        assert parse_content_crs(header) == CRS84

    def test_parse_tolerates_missing_brackets(self):
        assert parse_content_crs(CRS84) == CRS84


class TestFiltering:
    def test_filter_lang_defaults_to_cql2_text(self):
        assert FilterParameters().filter_lang is FilterLang.cql2_text

    def test_filter_params_use_kebab_case(self):
        params = FilterParameters(filter="city='Bonn'", filter_crs=CRS84)
        dumped = params.model_dump()
        assert dumped["filter-lang"] == "cql2-text"
        assert dumped["filter-crs"] == CRS84

    def test_rejects_unknown_filter_lang(self):
        with pytest.raises(ValidationError):
            FilterParameters(filter_lang="sql")

    def test_spatial_queryable_omits_type(self):
        q = Queryable(format="geometry-polygon", x_ogc_role="primary-geometry")
        dumped = q.model_dump()
        assert "type" not in dumped
        assert dumped["x-ogc-role"] == "primary-geometry"

    def test_queryables_defaults(self):
        q = Queryables(id="http://example.com/queryables")
        dumped = q.model_dump()
        assert dumped["$schema"] == QUERYABLES_SCHEMA_DIALECT
        assert dumped["$id"] == "http://example.com/queryables"
        assert dumped["type"] == "object"
        assert dumped["additionalProperties"] is True

    def test_queryables_parses_schema_document(self):
        doc = {
            "$schema": QUERYABLES_SCHEMA_DIALECT,
            "$id": "http://example.com/queryables",
            "type": "object",
            "properties": {
                "name": {"type": "string", "title": "Name"},
                "geom": {"format": "geometry-point", "x-ogc-role": "primary-geometry"},
            },
            "additionalProperties": False,
        }
        parsed = Queryables.model_validate(doc)
        assert parsed.properties["name"].type == "string"
        assert parsed.properties["geom"].x_ogc_role == "primary-geometry"
        assert parsed.additional_properties is False

    def test_function_requires_name_and_returns(self):
        with pytest.raises(ValidationError):
            Function(name="buffer")

    def test_functions_response(self):
        resp = Functions(
            functions=[
                Function(
                    name="buffer",
                    returns=[QueryableType.geometry],
                    arguments=[{"type": ["geometry", "number"]}],
                    metadata_url="http://example.com/buffer",
                )
            ]
        )
        dumped = resp.model_dump()
        assert dumped["functions"][0]["returns"] == ["geometry"]
        assert dumped["functions"][0]["metadataUrl"] == "http://example.com/buffer"

    def test_rejects_unknown_argument_type(self):
        with pytest.raises(ValidationError):
            Function(name="f", returns=["blob"])


class TestTransactions:
    def test_created_response(self):
        resp = TransactionResponse(status=201, location="/collections/b/items/1")
        assert resp.status is TransactionStatus.created
        assert resp.is_success

    @pytest.mark.parametrize("code", [400, 404, 409, 412, 428])
    def test_error_statuses_are_not_success(self, code):
        assert TransactionResponse(status=code).is_success is False

    def test_dump_uses_camel_case(self):
        resp = TransactionResponse(status=200, last_modified="2017-08-17T08:05:32Z")
        assert "lastModified" in resp.model_dump()

    def test_conditional_headers_render(self):
        headers = ConditionalHeaders(if_match='"abc123"').to_headers()
        assert headers == {"If-Match": '"abc123"'}

    def test_conditional_headers_format_http_date(self):
        headers = ConditionalHeaders(if_unmodified_since="2017-08-17T08:05:32Z").to_headers()
        assert headers["If-Unmodified-Since"] == "Thu, 17 Aug 2017 08:05:32 GMT"

    def test_empty_conditional_headers(self):
        assert ConditionalHeaders().to_headers() == {}
