# 🌐 `@geo watch`

watch the planet's story unfold.


```bash
@geo watch help
```
<details>
<summary></summary>

```bash
@geo \
	watch \
	[batch,dryrun,name=<job-name>] \
	[<query-object-name> | target=<target>] \
	[algo=<algo>,<algo-options>] \
	[~submit | dryrun,to=<runner>] \
	[dryrun,<map-options>] \
	[content=<0.5>,dryrun,~gif,publish,<reduce-options>] \
	[-|<object-name>]
 . watch target -> <object-name>.
   algo: diff | modality
   <algo-options>:
      diff: modality=<modality>,range=<100.0>
      modality: modality=<modality>
   modality: rgb[@<keyword>]
   runner: generic | local
   target: 
@geo \
	watch \
	batch,dryrun,name=<job-name> \
	[<query-object-name> | target=<target>] \
	[algo=<algo>,<algo-options>] \
	[~submit | dryrun,to=<runner>] \
	[dryrun,<map-options>] \
	[content=<0.5>,dryrun,~gif,publish,<reduce-options>] \
	[-|<object-name>]
 . watch target -aws-batch-> <object-name>.
   algo: diff | modality
   <algo-options>:
      diff: modality=<modality>,range=<100.0>
      modality: modality=<modality>
   modality: rgb[@<keyword>]
   runner: generic | local
   target: 
@geo \
	watch \
	map \
	[algo=<algo>,dryrun,~download,modality=<modality>,offset=<offset>,suffix=<suffix>,~upload] \
	[.|<query-object-name>]
 . @geo watch map <query-object-name> @ <offset> -> /<suffix>.
@geo \
	watch \
	query \
	[dryrun,target=<target>,~upload] \
	[.|<object-name>]
 . query target -> <object-name>.
@geo \
	watch \
	reduce \
	[algo=<algo>dryrun,~download,publish,suffix=<suffix>,~upload] \
	[..|<query-object-name>] \
	[.|<object-name>]
 . @geo watch reduce <query-object-name>/<suffix> -> <object-name>.
@targets cat \
	<target-name>
 . cat <target-name>.
@targets cp|copy \
	[-] \
	[..|<object-name-1>] \
	[.|<object-name-2>]
 . copy <object-name-1>/target -> <object-name-2>.
@targets download \
	[open,QGIS]
 . download watch targets.
   object: $BLUE_GEO_WATCH_TARGET_LIST
@targets edit
 . edit watch targets.
   /Users/kamangir/storage/abcli/bluer-geo-target-list-v1/metadata.yaml
   object: $BLUE_GEO_WATCH_TARGET_LIST
@targets get \
	[--delim space] \
	[--including_versions 0] \
	[--target_name <target>] \
	[--what <catalog|collection|exists|one_liner|query_args>]
 . get <target> info.
@targets list \
	[--catalog <catalog>] \
	[--collection <collection>] \
	[--count <count>] \
	[--delim <space>] \
	[--including_versions 0]
 . list targets.
@targets open \
	[~QGIS,template]
 . open targets.
@targets publish \
	[template]
 . publish watch targets.
@targets save \
	[target=all|<target-name>] \
	[.|<object-name>]
 . save target(s) -> <object-name>.
   template: $BLUE_GEO_QGIS_TEMPLATE_WATCH
@targets test
 . test watch targets.
@targets update_template \
	[~download,target=all|<target-name>,~upload]
 . update target template.
@targets upload
 . upload watch targets.
   object: $BLUE_GEO_WATCH_TARGET_LIST
```

</details>



## targets 🎯

- [`targets.geojson`](./targets.geojson)
- list of targets: [bluer-geo-target-list-v1.tar.gz](https://kamangir-public.s3.ca-central-1.amazonaws.com/bluer-geo-target-list-v1.tar.gz)
- template: [bluer_geo_watch_template_v1.tar.gz](https://kamangir-public.s3.ca-central-1.amazonaws.com/bluer_geo_watch_template_v1.tar.gz)

## example run

```bash
@geo watch \
  batch \
  target=elkhema-2024 - \
  to=aws_batch - \
  publish \
  geo-watch-elkhema-2024-2024-10-05-a-b
```

[dev notes](https://arash-kamangir.medium.com/%EF%B8%8F-conversations-with-ai-252-2118326b1de2).

ℹ️ suffix published gif urls with `-2X` and `-4X` for different scales. example: [1X](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b.gif), [2X](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b-2X.gif), [4X](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b-4X.gif).

## `Cache-Creek`

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-Cache-Creek-2x-wider-2024-11-05/geo-watch-Cache-Creek-2x-wider-2024-11-05-4X.gif?raw=true&random=he7fvvevwgqo2t5b)](TBA/geo-watch-Cache-Creek-2x-wider-2024-11-05/geo-watch-Cache-Creek-2x-wider-2024-11-05.gif)

</details>

- [`geo-watch-Cache-Creek-2024-10-06-a`](TBA/geo-watch-Cache-Creek-2024-10-06-a.tar.gz), [gif](TBA/geo-watch-Cache-Creek-2024-10-06-a/geo-watch-Cache-Creek-2024-10-06-a.gif).
- [`geo-watch-Cache-Creek-2x-wider-2024-10-06-a`](TBA/geo-watch-Cache-Creek-2x-wider-2024-10-06-a.tar.gz), [gif](TBA/geo-watch-Cache-Creek-2x-wider-2024-10-06-a/geo-watch-Cache-Creek-2x-wider-2024-10-06-a.gif).
- [`geo-watch-Cache-Creek-2024-11-05`](TBA/geo-watch-Cache-Creek-2024-11-05.tar.gz), [gif](TBA/geo-watch-Cache-Creek-2024-11-05/geo-watch-Cache-Creek-2024-11-05.gif).
- [`geo-watch-Cache-Creek-2x-wider-2024-11-05`](TBA/geo-watch-Cache-Creek-2x-wider-2024-11-05.tar.gz), [gif](TBA/geo-watch-Cache-Creek-2x-wider-2024-11-05/geo-watch-Cache-Creek-2x-wider-2024-11-05.gif).

## [`DrugSuperLab`](./targets/md/DrugSuperLab.md)

<details>
<summary>🌐</summary>

[![image](TBA/DrugSuperLab-2024-12-09-ZnmC5L/DrugSuperLab-2024-12-09-ZnmC5L-4X.gif?raw=true&random=l05o78v8tlas188w)](TBA/DrugSuperLab-2024-12-09-ZnmC5L/DrugSuperLab-2024-12-09-ZnmC5L.gif)

</details>

- [`geo-watch-DrugSuperLab-2024-11-19-13954`](TBA/geo-watch-DrugSuperLab-2024-11-19-13954.tar.gz), [gif](TBA/geo-watch-DrugSuperLab-2024-11-19-13954/geo-watch-DrugSuperLab-2024-11-19-13954.gif), known issues: successive frames may have different projections..
- [`DrugSuperLab-2024-12-08-pGErp2`](TBA/DrugSuperLab-2024-12-08-pGErp2.tar.gz), [gif](TBA/DrugSuperLab-2024-12-08-pGErp2/DrugSuperLab-2024-12-08-pGErp2.gif).
- [`DrugSuperLab-2024-12-09-ZnmC5L`](TBA/DrugSuperLab-2024-12-09-ZnmC5L.tar.gz), [gif](TBA/DrugSuperLab-2024-12-09-ZnmC5L/DrugSuperLab-2024-12-09-ZnmC5L.gif).

## [`Fagradalsfjall`](./targets/md/Fagradalsfjall.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-2024-09-04-Fagradalsfjall-a/geo-watch-2024-09-04-Fagradalsfjall-a-2X.gif?raw=true&random=dhnd2lupms6dnzfn)](TBA/geo-watch-2024-09-04-Fagradalsfjall-a/geo-watch-2024-09-04-Fagradalsfjall-a.gif)

</details>

- [`geo-watch-2024-09-04-Fagradalsfjall-a`](TBA/geo-watch-2024-09-04-Fagradalsfjall-a.tar.gz), [gif](TBA/geo-watch-2024-09-04-Fagradalsfjall-a/geo-watch-2024-09-04-Fagradalsfjall-a.gif).

## [`Jasper`](./targets/md/Jasper.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-Jasper-2024-11-03/geo-watch-Jasper-2024-11-03-2X.gif?raw=true&random=ct8jv6jn7o2yu496)](TBA/geo-watch-Jasper-2024-11-03/geo-watch-Jasper-2024-11-03.gif)

</details>

- [`geo-watch-2024-09-06-Jasper-a`](TBA/geo-watch-2024-09-06-Jasper-a.tar.gz), [gif](TBA/geo-watch-2024-09-06-Jasper-a/geo-watch-2024-09-06-Jasper-a.gif).
- [`geo-watch-Jasper-2024-11-03`](TBA/geo-watch-Jasper-2024-11-03.tar.gz), [gif](TBA/geo-watch-Jasper-2024-11-03/geo-watch-Jasper-2024-11-03.gif).

## [`Leonardo`](./targets/md/Leonardo.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-2024-10-27-16-17-36-12059/geo-watch-2024-10-27-16-17-36-12059-4X.gif?raw=true&random=tb0trlk66bacnu7a)](TBA/geo-watch-2024-10-27-16-17-36-12059/geo-watch-2024-10-27-16-17-36-12059.gif)

</details>

- [`test_bluer_geo_watch_v4-diff-Leonardo-test`](TBA/test_bluer_geo_watch_v4-diff-Leonardo-test.tar.gz), [gif](TBA/test_bluer_geo_watch_v4-diff-Leonardo-test/test_bluer_geo_watch_v4-diff-Leonardo-test.gif), [![bashtest](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml).
- [`test_bluer_geo_watch_v4-modality-Leonardo-test`](TBA/test_bluer_geo_watch_v4-modality-Leonardo-test.tar.gz), [gif](TBA/test_bluer_geo_watch_v4-modality-Leonardo-test/test_bluer_geo_watch_v4-modality-Leonardo-test.gif), [![bashtest](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml).
- [`geo-watch-2024-09-30-Leonardo-g`](TBA/geo-watch-2024-09-30-Leonardo-g.tar.gz), [gif](TBA/geo-watch-2024-09-30-Leonardo-g/geo-watch-2024-09-30-Leonardo-g.gif).
- [`geo-watch-Leonardo-2024-10-05-a`](TBA/geo-watch-Leonardo-2024-10-05-a.tar.gz), [gif](TBA/geo-watch-Leonardo-2024-10-05-a/geo-watch-Leonardo-2024-10-05-a.gif).
- [`geo-watch-Leonardo-2024-10-06-a`](TBA/geo-watch-Leonardo-2024-10-06-a.tar.gz), [gif](TBA/geo-watch-Leonardo-2024-10-06-a/geo-watch-Leonardo-2024-10-06-a.gif).
- [`geo-watch-2024-10-27-16-17-36-12059`](TBA/geo-watch-2024-10-27-16-17-36-12059.tar.gz), [gif](TBA/geo-watch-2024-10-27-16-17-36-12059/geo-watch-2024-10-27-16-17-36-12059.gif).

## [`Mount-Etna`](./targets/md/Mount-Etna.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-2024-09-04-Mount-Etna-a/geo-watch-2024-09-04-Mount-Etna-a-2X.gif?raw=true&random=h3ryjoop8c9obd5y)](TBA/geo-watch-2024-09-04-Mount-Etna-a/geo-watch-2024-09-04-Mount-Etna-a.gif)

</details>

- [`geo-watch-2024-09-04-Mount-Etna-a`](TBA/geo-watch-2024-09-04-Mount-Etna-a.tar.gz), [gif](TBA/geo-watch-2024-09-04-Mount-Etna-a/geo-watch-2024-09-04-Mount-Etna-a.gif).

## [`Palisades`](./targets/md/Palisades.md)

<details>
<summary>🌐</summary>

[![image](TBA/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8-2X.gif?raw=true&random=7tdjfwmnnd2oo0qe)](TBA/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8.gif)

</details>

- [`Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8`](TBA/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8.tar.gz), [gif](TBA/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8/Palisades-Sentinel-2-2025-01-15-16-50-38-vyjxu8.gif).

## `Sheerness`

<details>
<summary>🌐</summary>

[![image](TBA/Sheerness-20x-2024-12-14-EDkXl0/Sheerness-20x-2024-12-14-EDkXl0-4X.gif?raw=true&random=zofv0hsbxywut7br)](TBA/Sheerness-20x-2024-12-14-EDkXl0/Sheerness-20x-2024-12-14-EDkXl0.gif)

</details>

- [`Sheerness-20x-2024-12-09-S8xKmn`](TBA/Sheerness-20x-2024-12-09-S8xKmn.tar.gz), [gif](TBA/Sheerness-20x-2024-12-09-S8xKmn/Sheerness-20x-2024-12-09-S8xKmn.gif), half-blank frames, will rerun with content-ratio > 0.6..
- [`Sheerness-20x-2024-12-14-EDkXl0`](TBA/Sheerness-20x-2024-12-14-EDkXl0.tar.gz), [gif](TBA/Sheerness-20x-2024-12-14-EDkXl0/Sheerness-20x-2024-12-14-EDkXl0.gif).

## `Silver-Peak`

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-Silver-Peak-2024-10-12-a/geo-watch-Silver-Peak-2024-10-12-a-4X.gif?raw=true&random=yhmbfxs9s23ht3o2)](TBA/geo-watch-Silver-Peak-2024-10-12-a/geo-watch-Silver-Peak-2024-10-12-a.gif)

</details>

- [`geo-watch-Silver-Peak-2024-10-12-a`](TBA/geo-watch-Silver-Peak-2024-10-12-a.tar.gz), [gif](TBA/geo-watch-Silver-Peak-2024-10-12-a/geo-watch-Silver-Peak-2024-10-12-a.gif).

## `bellingcat-2024-09-27-nagorno-karabakh`

<details>
<summary>🌐</summary>

[![image](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1-4X.gif?raw=true&random=1noaq7oint8cpvi9)](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1.gif)

</details>

- [`bellingcat-2024-09-27-nagorno-karabakh-2024-10-01-c-b`](TBA/bellingcat-2024-09-27-nagorno-karabakh-2024-10-01-c-b.tar.gz), [gif](TBA/bellingcat-2024-09-27-nagorno-karabakh-2024-10-01-c-b/bellingcat-2024-09-27-nagorno-karabakh-2024-10-01-c-b.gif).
- [`bellingcat-2024-09-27-nagorno-karabakh-b`](TBA/bellingcat-2024-09-27-nagorno-karabakh-b.tar.gz), [gif](TBA/bellingcat-2024-09-27-nagorno-karabakh-b/bellingcat-2024-09-27-nagorno-karabakh-b.gif).
- [`bellingcat-2024-09-27-nagorno-karabakh-6X-a`](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-a.tar.gz), [gif](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-a/bellingcat-2024-09-27-nagorno-karabakh-6X-a.gif).
- [`geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b`](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b.tar.gz), [gif](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-05-b.gif).
- [`geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-06-a`](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-06-a.tar.gz), [gif](TBA/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-06-a/geo-watch-bellingcat-2024-09-27-nagorno-karabakh-6X-2024-10-06-a.gif).
- [`bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1`](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1.tar.gz), [gif](TBA/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1/bellingcat-2024-09-27-nagorno-karabakh-6X-2024-12-14-EUUpS1.gif).

## [`burning-man-2024`](./targets/md/burning-man-2024.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-2024-09-04-burning-man-2024-a/geo-watch-2024-09-04-burning-man-2024-a-2X.gif?raw=true&random=rc8adlx5yk4qakpc)](TBA/geo-watch-2024-09-04-burning-man-2024-a/geo-watch-2024-09-04-burning-man-2024-a.gif)

</details>

- [`geo-watch-2024-09-04-burning-man-2024-a`](TBA/geo-watch-2024-09-04-burning-man-2024-a.tar.gz), [gif](TBA/geo-watch-2024-09-04-burning-man-2024-a/geo-watch-2024-09-04-burning-man-2024-a.gif).

## [`chilcotin-river-landslide`](./targets/md/chilcotin-river-landslide.md)

<details>
<summary>🌐</summary>

[![image](TBA/geo-watch-Chilcotin-2024-11-03/geo-watch-Chilcotin-2024-11-03-4X.gif?raw=true&random=3wb01kzgd13ua3ha)](TBA/geo-watch-Chilcotin-2024-11-03/geo-watch-Chilcotin-2024-11-03.gif)

</details>

- [`test_bluer_geo_watch_v4-diff-chilcotin-river-landslide-test`](TBA/test_bluer_geo_watch_v4-diff-chilcotin-river-landslide-test.tar.gz), [gif](TBA/test_bluer_geo_watch_v4-diff-chilcotin-river-landslide-test/test_bluer_geo_watch_v4-diff-chilcotin-river-landslide-test.gif), [![bashtest](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml).
- [`test_bluer_geo_watch_v4-modality-chilcotin-river-landslide-test`](TBA/test_bluer_geo_watch_v4-modality-chilcotin-river-landslide-test.tar.gz), [gif](TBA/test_bluer_geo_watch_v4-modality-chilcotin-river-landslide-test/test_bluer_geo_watch_v4-modality-chilcotin-river-landslide-test.gif), [![bashtest](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/bluer-geo/actions/workflows/bashtest.yml).
- [`geo-watch-2024-08-31-chilcotin-c`](TBA/geo-watch-2024-08-31-chilcotin-c.tar.gz), [gif](TBA/geo-watch-2024-08-31-chilcotin-c/geo-watch-2024-08-31-chilcotin-c.gif), L1C and L2A mixed, `2024-07-30/2024-08-09`.
- [`geo-watch-2024-09-01-chilcotin-a`](TBA/geo-watch-2024-09-01-chilcotin-a.tar.gz), [gif](TBA/geo-watch-2024-09-01-chilcotin-a/geo-watch-2024-09-01-chilcotin-a.gif).
- [`geo-watch-2024-09-01-chilcotin-c`](TBA/geo-watch-2024-09-01-chilcotin-c.tar.gz), [gif](TBA/geo-watch-2024-09-01-chilcotin-c/geo-watch-2024-09-01-chilcotin-c.gif), [on reddit](https://www.reddit.com/r/bash/comments/1f9cvyx/a_bash_python_tool_to_watch_a_target_in_satellite/)..
- [`geo-watch-Chilcotin-2024-11-03`](TBA/geo-watch-Chilcotin-2024-11-03.tar.gz), [gif](TBA/geo-watch-Chilcotin-2024-11-03/geo-watch-Chilcotin-2024-11-03.gif).

## `elkhema ⛺️`

<details>
<summary>🌐</summary>

[![image](TBA/elkhema-2024-12-15-8EqPXl/elkhema-2024-12-15-8EqPXl-4X.gif?raw=true&random=gpg59u71ag03ay7x)](TBA/elkhema-2024-12-15-8EqPXl/elkhema-2024-12-15-8EqPXl.gif)

</details>

- [`geo-watch-elkhema-2024-2024-10-05-a-b`](TBA/geo-watch-elkhema-2024-2024-10-05-a-b.tar.gz), [gif](TBA/geo-watch-elkhema-2024-2024-10-05-a-b/geo-watch-elkhema-2024-2024-10-05-a-b.gif).
- [`elkhema-2024-12-15-8EqPXl`](TBA/elkhema-2024-12-15-8EqPXl.tar.gz), [gif](TBA/elkhema-2024-12-15-8EqPXl/elkhema-2024-12-15-8EqPXl.gif).

