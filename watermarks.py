from typing import Callable, Mapping, Union, Optional

Marker = Callable[[str], str]
Detector = Callable[[str], float]

Watermark = tuple[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]
Watermarks = Mapping[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]
