# License and notices for the bundled fastener data

The files `bolts.json` and `nuts.json` in this directory are derived from the
BOLTS dimension tables. They are distributed under the **GNU Lesser General
Public License, version 2.1 or (at your option) any later version**
(`LGPL-2.1-or-later`), not under the MIT license covering this project's Python
code, generator scripts, and original documentation.

## Upstream attribution and license notice

BOLTS - Open Library of Technical Specifications

Copyright (C) 2013 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>

The upstream nut tables also include the hexagon lock nut contribution by
Maciej Małecki (2022-07-20, commit
`4300044b42f3d813e7c4f75fe6a8c2dc0d658d51`).

This library is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 2.1 of the License, or (at your option)
any later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this library. The complete text is supplied as
`LICENSES/LGPL-2.1-or-later.txt` in the source distribution and under
`bd_buildabolt-<version>.dist-info/licenses/LICENSES/` in an installed wheel.
It is also available at <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>.

## Derivation and modification record

These JSON files are **modified extracts, not verbatim copies**, of BOLTS
`data/hex_socket.blt` and `data/nut.blt`. The generator selects five classes,
renames and selects their dimension columns, groups the records by size and
kind, and serializes them as JSON. It also retains the original package's
flattened default-nut fields and derives the headless bolt records from the
socket-head table. No upstream CAD implementation is included.

**2026-11-13:** bd-buildabolt documented this existing extraction and added
these licensing and attribution notices. Both JSON files remain byte-for-byte
unchanged by this licensing update.

## Upstream references

The source tables and their original license notices can be inspected at:

- [BOLTS data/hex_socket.blt](https://github.com/boltsparts/boltsparts/blob/4300044b42f3d813e7c4f75fe6a8c2dc0d658d51/data/hex_socket.blt)
- [BOLTS data/nut.blt](https://github.com/boltsparts/boltsparts/blob/4300044b42f3d813e7c4f75fe6a8c2dc0d658d51/data/nut.blt)

Upstream repository: <https://github.com/boltsparts/boltsparts>.

The JSON files are separate, editable data resources loaded at runtime. Users
may replace them with interface-compatible modified versions; there is no
runtime checksum or signature restriction. Modifications to the BOLTS-derived
data remain subject to its LGPL terms. The MIT license does not replace those
terms.
