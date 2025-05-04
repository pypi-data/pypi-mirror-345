#! /usr/bin/env bash

function test_bluer_geo_gdal_get_crs() {
    local options=$1

    bluer_ai_log_warning "disabled, tracked in https://github.com/kamangir/bluer-geo/issues/2".
    return 0

    local object_name=$BLUE_GEO_WATCH_TARGET_LIST
    bluer_objects_download - $object_name

    local crs=$(bluer_geo_gdal_get_crs $ABCLI_OBJECT_ROOT/$object_name/target/shape.geojson)

    bluer_ai_assert "$crs" EPSG:4326
}
