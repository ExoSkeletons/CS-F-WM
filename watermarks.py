from typing import Callable, Mapping

Marker = Callable[[str], str]
Detector = Callable[[str], float]

Watermark = tuple[str, Marker | None | tuple[Marker, Detector | None]]
Watermarks = Mapping[str, Marker | None | tuple[Marker, Detector | None]]
