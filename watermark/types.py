from typing import Union, Callable, Optional

Marker = Callable[[str], str]
Detector = Callable[[str], float]

Watermark = tuple[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]
Watermarks = dict[str, Union[Marker, None, tuple[Marker, Optional[Detector]]]]
