#! /usr/bin/env bash

function test_bluer_geo_watch_targets_get_catalog() {
    bluer_objects_download - $BLUE_GEO_WATCH_TARGET_LIST

    bluer_ai_log_warning "disabled, tracked in https://github.com/kamangir/bluer-geo/issues/2".
    return 0

    bluer_ai_assert \
        $(bluer_geo_watch_targets get \
            --what catalog \
            --target_name chilcotin-river-landslide \
            --log 0) \
        copernicus
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        "$(bluer_geo_watch_targets get \
            --what catalog \
            --target_name Deadpool \
            --log 0)" \
        - empty
}

function test_bluer_geo_watch_targets_get_collection() {
    bluer_objects_download - $BLUE_GEO_WATCH_TARGET_LIST

    bluer_ai_log_warning "disabled, tracked in https://github.com/kamangir/bluer-geo/issues/2".
    return 0

    bluer_ai_assert \
        $(bluer_geo_watch_targets get \
            --what collection \
            --target_name chilcotin-river-landslide \
            --log 0) \
        sentinel_2
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        "$(bluer_geo_watch_targets get \
            --what collection \
            --target_name Deadpool \
            --log 0)" \
        - empty
}

function test_bluer_geo_watch_targets_get_exists() {
    bluer_objects_download - $BLUE_GEO_WATCH_TARGET_LIST

    bluer_ai_log_warning "disabled, tracked in https://github.com/kamangir/bluer-geo/issues/2".
    return 0

    bluer_ai_assert \
        $(bluer_geo_watch_targets get \
            --what exists \
            --target_name chilcotin-river-landslide \
            --log 0) \
        1
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_geo_watch_targets get \
            --what exists \
            --target_name Deadpool \
            --log 0) \
        0
}

function test_bluer_geo_watch_targets_get_query_args() {
    bluer_objects_download - $BLUE_GEO_WATCH_TARGET_LIST

    bluer_ai_log_warning "disabled, tracked in https://github.com/kamangir/bluer-geo/issues/2".
    return 0

    bluer_ai_assert \
        $(bluer_geo_watch_targets get \
            --what query_args \
            --target_name chilcotin-river-landslide \
            --log 0 \
            --delim +) \
        sentinel_2
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        "$(bluer_geo_watch_targets get \
            --what query_args \
            --target_name Deadpool \
            --log 0 \
            --delim +)" \
        - empty
}
