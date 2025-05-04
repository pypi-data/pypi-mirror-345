## 1.29.6 - 2025-05-04
### Extractors
#### Additions
- [manganelo] support `nelomanga.net` and mirror domains ([#7423](https://github.com/mikf/gallery-dl/issues/7423))
#### Fixes
- [deviantart] unescape `\'` in JSON data ([#6653](https://github.com/mikf/gallery-dl/issues/6653))
- [kemonoparty] revert to using default creator posts endpoint ([#7438](https://github.com/mikf/gallery-dl/issues/7438) [#7450](https://github.com/mikf/gallery-dl/issues/7450) [#7462](https://github.com/mikf/gallery-dl/issues/7462))
- [pixiv:novel] fix `embeds` extraction by using AJAX API ([#7422](https://github.com/mikf/gallery-dl/issues/7422) [#7435](https://github.com/mikf/gallery-dl/issues/7435))
- [scrolller] fix exception for albums with missing media ([#7428](https://github.com/mikf/gallery-dl/issues/7428))
- [twitter] fix `404 Not Found ()` errors ([#7382](https://github.com/mikf/gallery-dl/issues/7382) [#7386](https://github.com/mikf/gallery-dl/issues/7386) [#7426](https://github.com/mikf/gallery-dl/issues/7426) [#7430](https://github.com/mikf/gallery-dl/issues/7430) [#7431](https://github.com/mikf/gallery-dl/issues/7431) [#7445](https://github.com/mikf/gallery-dl/issues/7445) [#7459](https://github.com/mikf/gallery-dl/issues/7459))
#### Improvements
- [kemonoparty] add `endpoint` option ([#7438](https://github.com/mikf/gallery-dl/issues/7438) [#7450](https://github.com/mikf/gallery-dl/issues/7450) [#7462](https://github.com/mikf/gallery-dl/issues/7462))
- [tumblr] improve error message for dashboard-only blogs ([#7455](https://github.com/mikf/gallery-dl/issues/7455))
- [weasyl] support `/view/` URLs ([#7469](https://github.com/mikf/gallery-dl/issues/7469))
#### Metadata
- [chevereto] extract `date` metadata ([#7437](https://github.com/mikf/gallery-dl/issues/7437))
- [civitai] implement retrieving `model` and `version` metadata ([#7432](https://github.com/mikf/gallery-dl/issues/7432))
- [manganelo] extract more metadata
### Post Processors
- [directory] add `directory` post processor ([#7432](https://github.com/mikf/gallery-dl/issues/7432))
### Miscellaneous
- [job] do not reset skip count when `skip-filter` fails ([#7433](https://github.com/mikf/gallery-dl/issues/7433))
